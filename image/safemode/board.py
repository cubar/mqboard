# Board configuration so other modules don't need to be too board-specific
# Copyright © 2020 by Thorsten von Eicken.
import machine

# Pull-in the specifics of the board from `config`. That should be the only file that is
# customized for each board. It also contains passwords and keys and should thus not be checked
# into public version control.
# There is a `config_tmpl.py` file around to use as template.
from config import *  # noqa

# ===== LED stuff and battery voltage stuff

act_led = False  # network activity LED, typ. blue, turn on with act_led(True)
fail_led = False  # failure/error, type red, turn on with fail_led(True)
bat_volt_pin = None  # voltage divider pin to measure battery
bat_fct = 2  # voltage divider factor


def define_led():
    global act_led, fail_led, bat_volt_pin, bat_fct
    if kind == "tve-bare":  # noqa
        # bare esp32-wroom module with LED across IO23 and gnd
        lpin = machine.Pin(23, machine.Pin.OUT, None, value=0)
        led = lambda v: lpin(v)
        act_led, fail_led = (led, led)
    elif kind == "huzzah32":  # noqa
        # Adafruit Huzzah32 feather
        lpin = machine.Pin(13, machine.Pin.OUT, None, value=0)
        led = lambda v: lpin(v)
        fail_led = led
    elif kind == "esp32-sim1":  # noqa
        # TvE custom ESP32 SIM module v1
        lpin1 = machine.Pin(2, machine.Pin.OUT, None, value=1)
        act_led = lambda v: lpin1(v)
        lpin2 = machine.Pin(5, machine.Pin.OUT, None, value=1)
        fail_led = lambda v: lpin2(not v)
        bat_volt_pin = machine.ADC(machine.Pin(35))
        bat_volt_pin.atten(machine.ADC.ATTN_11DB)
    elif kind == "lolin-d32":  # noqa
        # Wemos Lolin D-32
        lpin = machine.Pin(5, machine.Pin.OUT, None, value=1)
        led = lambda v: lpin(not v)
        bat_volt_pin = machine.ADC(machine.Pin(35))
        bat_volt_pin.atten(machine.ADC.ATTN_11DB)
        act_led, fail_led = (led, led)
    elif kind == "esp22":  # noqa
        # Esp22
        ledPin = 22  # default led on this module
        lpin = machine.Pin(ledPin, machine.Pin.OUT, None, value=0)
        led = lambda v: lpin(v)
        act_led, fail_led = (led, led)
    elif kind == "nodemcu":  # noqa
        # NodeMCU
        lpin = machine.Pin(2, machine.Pin.OUT, None, value=0)
        led = lambda v: lpin(v)
        act_led, fail_led = (led, led)
    elif kind == "esp32thing":  # noqa
        # Sparkfun ESP32 Thing
        lpin = machine.Pin(5, machine.Pin.OUT, None, value=0)
        led = lambda v: lpin(v)
        act_led, fail_led = (led, led)
    elif kind == "ezsbc":  # noqa
        # EzSBC
        lpin1 = machine.Pin(19, machine.Pin.OUT, None, value=1)
        act_led = lambda v: lpin1(not v)
        lpin2 = machine.Pin(16, machine.Pin.OUT, None, value=1)
        fail_led = lambda v: lpin2(not v)
    elif kind == "tinypico":  # noqa
        # TinyPICO has an RGB LED so we use the red channel for WiFi and the blue
        # channel for message rx
        from machine import SPI, Pin
        import tinypico as TinyPICO
        from dotstar import DotStar

        spi = SPI(
            sck=Pin(TinyPICO.DOTSTAR_CLK),
            mosi=Pin(TinyPICO.DOTSTAR_DATA),
            miso=Pin(TinyPICO.SPI_MISO),
        )
        dotstar = DotStar(spi, 1, brightness=0.5)  # Just one DotStar, half brightness
        TinyPICO.set_dotstar_power(True)

        color = [255, 0, 0]

        def set_red(v):
            color[0] = 255 if v else 0
            dotstar[0] = color

        def set_blue(v):
            color[2] = 255 if v else 0
            dotstar[0] = color

        fail_led = set_red
        act_led = set_blue
    elif kind == "pybd":  # noqa
        from pyb import LED

        def led(n, v):
            if v:
                LED(n).on()
            else:
                LED(n).off()

        act_led = lambda v: led(3, v)
        fail_led = lambda v: led(1, v)


define_led()
del define_led  # GC the function


def get_battery_voltage():
    """
    Returns the current battery voltage. If no battery is connected, returns 3.7V
    This is an approximation only, but useful to detect if the battery is getting low.
    """
    if bat_volt_pin == None:  # noqa
        return 0
    measuredvbat = bat_volt_pin.read() / 4095
    measuredvbat *= 3.6 * bat_fct  # 3.6V at full scale
    return measuredvbat


# ===== Wifi stuff
# connect_wifi is a handy little function to manually connect wifi
def connect_wifi():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    print(f"Connecting {wifi_ssid=} {wifi_pass=}")  # noqa
    wlan.connect(wifi_ssid, wifi_pass)  # noqa
    while not wlan.isconnected():
        pass
    print("Connected!")
