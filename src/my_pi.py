from typing import Union

from gpiozero import Button, LED, PWMLED
from gpiozero.pins.pigpio import PiGPIOFactory


class RemoteGPIO(object):
    MODE_OUT = 'output'
    MODE_IN = 'input'

    def __init__(self, host: str = None, port: int = None, pull_up: bool = True):
        self.remote_gpio = PiGPIOFactory(host, port)
        self._pi_info = None
        self.pins = {}
        self.pull_up = pull_up

    def read(self, pin_number: int, pull_up: bool = None) -> Union[int, float]:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_IN]
        ):
            self.pins[pin_number]['mode'] = self.MODE_IN
            if self.pins[pin_number]['obj'] is None:
                if pull_up is None:
                    pull_up = self.pull_up
                self.pins[pin_number]['obj'] = Button(pin_number, pull_up=pull_up, pin_factory=self.remote_gpio)
            return self.pins[pin_number]['obj'].is_pressed
        elif(
            pin_number in self.pins and
            self.pins[pin_number]['mode'] == self.MODE_OUT and
            self.pins[pin_number]['obj']
        ):
            return self.pins[pin_number]['obj'].value

    def pull_up(self, pin_number: int) -> bool:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_IN]
        ):
            self.pins[pin_number]['mode'] = self.MODE_IN
            self.pins[pin_number]['obj'] = Button(pin_number, pull_up=True, pin_factory=self.remote_gpio)
            return True
        return False

    def pull_down(self, pin_number: int) -> bool:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_IN]
        ):
            self.pins[pin_number]['mode'] = self.MODE_IN
            self.pins[pin_number]['obj'] = Button(pin_number, pull_up=False, pin_factory=self.remote_gpio)
            return True
        return False

    def write(self, pin_number: int, value: bool) -> bool:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_OUT]
        ):
            self.pins[pin_number]['mode'] = self.MODE_OUT
            if self.pins[pin_number]['obj'] is None:
                self.pins[pin_number]['obj'] = LED(pin_number, pin_factory=self.remote_gpio)
            if value:
                self.pins[pin_number]['obj'].on()
            else:
                self.pins[pin_number]['obj'].off()
            return True
        return False

    def pwm(self, pin_number: int, value: float) -> bool:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_OUT]
        ):
            self.pins[pin_number]['mode'] = self.MODE_OUT
            if self.pins[pin_number]['obj'] is None:
                self.pins[pin_number]['obj'] = PWMLED(pin_number, pin_factory=self.remote_gpio)
            self.pins[pin_number]['obj'].value = value
            return True
        return False

    def get_pi_info(self) -> dict:
        if self._pi_info is None:
            self._pi_info = {
                'model': self.remote_gpio.pi_info.model,
                'bluetooth': self.remote_gpio.pi_info.bluetooth,
                'csi': self.remote_gpio.pi_info.csi,
                'dsi': self.remote_gpio.pi_info.dsi,
                'ethernet': self.remote_gpio.pi_info.ethernet,
                'manufacturer': self.remote_gpio.pi_info.manufacturer,
                'memory': self.remote_gpio.pi_info.memory,
                'pcb_revision': self.remote_gpio.pi_info.pcb_revision,
                'released': self.remote_gpio.pi_info.released,
                'revision': self.remote_gpio.pi_info.revision,
                'soc': self.remote_gpio.pi_info.soc,
                'storage': self.remote_gpio.pi_info.storage,
                'usb': self.remote_gpio.pi_info.usb,
                'wifi': self.remote_gpio.pi_info.wifi,
                'pins': [],
            }
            for header in self.remote_gpio.pi_info.headers.values():
                for pin in header.pins.values():
                    if pin.function not in ['3V3', '5V', 'GND']:
                        self.pins[pin.number] = {
                            'function': pin.function,
                            'pull_up': pin.pull_up,
                            'mode': None,
                            'obj': None,
                        }
                        self._pi_info['pins'].append({
                            'number': pin.number,
                            'function': pin.function,
                            'pull_up': pin.pull_up,
                        })
        return self._pi_info


if __name__ == '__main__':
    REMOTE_PI_HOST = '127.0.0.1'
    REMOTE_GPIO = RemoteGPIO(REMOTE_PI_HOST)
    print(REMOTE_GPIO.get_pi_info())
