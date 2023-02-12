"""
App example: Blink the onboard led with name "blinky" in file blinky.py
Configuration in lib/config.py;
1. Add module name "blinky" to the list "modules" in config.py.
2. Add a dict "blinky" in config.py to specify the configuration variables for the app if any.
"""
import logging
from uasyncio import Loop as loop, sleep_ms
from board import act_led
from safemode.config import uniqueId

blinky = {  # blinks the boards default led, if any
    "topic"  : f'{uniqueId}/period',
    "period" : 800,  # initial period in milliseconds
}


class Blinker:
    def __init__(self, mqclient, topic, period):
        self.mqclient = mqclient
        self.topic = topic
        self.period = period

    async def blinker(self):
        while True:
            act_led(1)
            await sleep_ms(self.period // 2)
            act_led(0)
            await sleep_ms(self.period // 2)

    def period(self, millisecs):
        self.period = millisecs

    def on_msg(self, topic, msg, retained, qos, dup):
        topic = str(topic, "utf-8")
        if topic == self.topic:
            try:
                p = int(msg)
                if p < 50 or p > 10000:
                    raise ValueError("period must be in 50..10000")
                self.period = p
            except Exception as e:
                log.exc(e, "Invalid incoming message")

    async def hook_it_up(self, mqtt):
        log.info("hook_it_up called")
        mqtt.on_msg(self.on_msg)
        await mqtt.client.subscribe(self.topic, qos=1)
        log.info("Subscribed to %s", self.topic)


# start is called by the module launcher loop in main.py; it is passed a handle onto the MQTT
# dispatcher and to the "blinky" config dict in config.py
def start(mqtt, config):
    period = config.get("period", 1000)  # get period from config with a default of 1000ms
    log.info("start called, period=%d", period)
    bl = Blinker(mqtt.client, config["topic"], period)
    loop.create_task(bl.blinker())
    mqtt.on_init(bl.hook_it_up(mqtt))


log = logging.getLogger(__name__)
