# This has not been tested by me
"""
Receiving 433/315Mhz signals with low-cost RF Modules
"""

import time
from collections import namedtuple
from machine import Pin


MAX_CHANGES = 67

Protocol = namedtuple('Protocol',
                      ['pulselength',
                       'sync_high', 'sync_low',
                       'zero_high', 'zero_low',
                       'one_high', 'one_low'])
PROTOCOLS = (None,
             Protocol(350, 1, 31, 1, 3, 3, 1),
             Protocol(650, 1, 10, 1, 2, 2, 1),
             Protocol(100, 30, 71, 4, 11, 9, 6),
             Protocol(380, 1, 6, 1, 3, 3, 1),
             Protocol(500, 6, 14, 1, 2, 2, 1),
             Protocol(200, 1, 10, 1, 5, 1, 1))


class RFDevice:
    """Representation of a GPIO RF device."""

    # pylint: disable=too-many-instance-attributes,too-many-arguments
    def __init__(self, pin, rx_tolerance=80):
        """Initialize the RF device."""
        self.pin = pin
        self.rx_tolerance = rx_tolerance
        # internal values
        self._rx_timings = [0] * (MAX_CHANGES + 1)
        self._rx_last_timestamp = 0
        self._rx_change_count = 0
        self._rx_repeat_count = 0
        # successful RX values
        self.rx_code = None
        self.rx_code_timestamp = None
        self.rx_proto = None
        self.rx_bitlength = None
        self.rx_pulselength = None
        self.enable_rx()

    def enable_rx(self):
        """Enable RX, set up GPIO and add event detection."""
        self.pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.rx_callback)
        print(f'RX enabled on {self.pin}')
        return True

    # pylint: disable=unused-argument
    def rx_callback(self, pin):
        """RX callback for pin event detection. Handle basic signal detection."""
        timestamp = int(time.ticks_us())
        duration = timestamp - self._rx_last_timestamp

        if duration > 5000:
            if abs(duration - self._rx_timings[0]) < 200:
                self._rx_repeat_count += 1
                self._rx_change_count -= 1
                if self._rx_repeat_count == 2:
                    for pnum in range(1, len(PROTOCOLS)):
                        if self._rx_waveform(pnum, self._rx_change_count, timestamp):
                            print("RX code " + str(self.rx_code))
                            break
                    self._rx_repeat_count = 0
            self._rx_change_count = 0

        if self._rx_change_count >= MAX_CHANGES:
            self._rx_change_count = 0
            self._rx_repeat_count = 0
        self._rx_timings[self._rx_change_count] = duration
        self._rx_change_count += 1
        self._rx_last_timestamp = timestamp

    def _rx_waveform(self, pnum, change_count, timestamp):
        """Detect waveform and format code."""
        code = 0
        delay = int(self._rx_timings[0] / PROTOCOLS[pnum].sync_low)
        delay_tolerance = delay * self.rx_tolerance / 100

        for i in range(1, change_count, 2):
            if (
                abs(self._rx_timings[i] - delay * PROTOCOLS[pnum].zero_high) < delay_tolerance and
                abs(self._rx_timings[i+1] - delay * PROTOCOLS[pnum].zero_low) < delay_tolerance
            ):
                code <<= 1
            elif (
                abs(self._rx_timings[i] - delay * PROTOCOLS[pnum].one_high) < delay_tolerance and
                abs(self._rx_timings[i+1] - delay * PROTOCOLS[pnum].one_low) < delay_tolerance
            ):
                code <<= 1
                code |= 1
            else:
                return False

        if self._rx_change_count > 6 and code != 0:
            self.rx_code = code
            self.rx_code_timestamp = timestamp
            self.rx_bitlength = int(change_count / 2)
            self.rx_pulselength = delay
            self.rx_proto = pnum
            return True

        return False


def receive(rf, sleepTime):
    global S
    timestamp = None
    while True:
        if rf.rx_code_timestamp != timestamp:
            timestamp = rf.rx_code_timestamp
            code = str(rf.rx_code)
            pulse = rf.rx_pulselength
            proto = rf.rx_proto
            print(f'        {code} [pulselength {pulse} proto {proto}]')
        time.sleep(sleepTime)


def rx(sleepTime=0.5):
    Pin(23, Pin.OUT, 0)  # receiver needs gnd on pin 23
    rf = RFDevice(Pin(19))  # receiver data on pin 19
    try:
        receive(rf, sleepTime)
    finally:
        Pin(23, Pin.IN)  # receiver needs gnd on pin 23
