import json
import re
from machine import Pin, PWM
from uasyncio import create_task, sleep_ms
import logging


class Light(PWM):  # Lamp is a subclass of PWM
    def __init__(self, pin):
        super().__init__(Pin(pin))
        self.pin = pin
        self.update(state='OFF', brightness=0)

    def update(self, state, brightness):
        if state:
            self.state = state
        if brightness is not None:
            self.brightness = int(brightness)
        duty = 0 if self.state=='OFF' else int(1023 * self.brightness / 255)
        log.info(f'{duty=}   {state=}   {self.state=}   {brightness=}   {self.brightness=}')
        self.duty(duty)


class Lights:
    def __init__(self, mqclient, topic):
        self.mqclient = mqclient
        self.topic = topic
        self.lights = [Light(LED_PIN)]

    def isValid(self, state, brightness):
        return (
            state in ('ON', 'OFF') and
            (
              brightness is None or
              (type(brightness) == str and re.match('^[0-9]*$', brightness)) or
              type(brightness) == int
            )
        )

    def getLight(self, pin):
        for light in self.lights:
            if light.pin == pin:
                return light
        else:
            light = Light(pin)
            self.lights.append(light)
            return light

    async def update(self, pin, state, brightness):
        if not self.isValid(state, brightness):
            return
        light = self.getLight(pin)
        try:
            light.update(state, brightness)
        except:  # noqa
            return
        await self.publish(light)

    async def publish(self, light):
        payload = {'state':light.state, 'brightness':light.brightness}
        await self.mqclient.publish(self.topic+f'/stat/{light.pin}', json.dumps(payload))

    async def run(self):
        await self.publish(self.lights[0])
        while True:
            await sleep_ms(1000)

    def on_msg(self, topic, msg, retained, qos, dup):
        topic = topic.decode()
        if not topic.startswith(self.topic + '/set'):
            return
        pin = re.sub('.*/([0-9]+)$', r'\1', topic)
        if pin == topic:
            return
        payload = json.loads(msg)
        create_task(
          self.update(int(pin), payload.get('state'), payload.get('brightness'))
        )

    async def hook_it_up(self, mqtt):
        mqtt.on_msg(self.on_msg)
        topic = self.topic + '/set/+'
        await mqtt.client.subscribe(topic, qos=1)
        log.info("Subscribed to %s", self.topic)


# start is called by the module launcher loop in main.py; it is passed:
# - a handle onto the MQTT dispatcher and
# - a handle onto the config dict in config.py
def start(mqtt, config):
    lights = Lights(mqtt.client, config['topic'])
    create_task(lights.run())
    mqtt.on_init(lights.hook_it_up(mqtt))


log = logging.getLogger(__name__)
LED_PIN = 17
