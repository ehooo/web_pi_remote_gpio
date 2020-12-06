from typing import Union

from gpiozero import Button, LED, PWMLED
from gpiozero import GPIOPinInUse, PinFixedPull
from gpiozero import pi_info as pi_info_funct
from gpiozero.pins.pigpio import PiGPIOFactory


class RemoteGPIO(object):
    MODE_OUT = 'output'
    MODE_IN = 'input'

    def __init__(self, host: str = None, port: int = None, pull_up: bool = True):
        self.remote_gpio = None
        if host and port:
            self.remote_gpio = PiGPIOFactory(host, port)
        self._pi_info = None
        self.pins = {}
        self.default_pull_up = pull_up

    def read(self, pin_number: int, pull_up: bool = None) -> Union[int, float]:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_IN]
        ):
            self.pins[pin_number]['mode'] = self.MODE_IN
            if self.pins[pin_number]['obj'] is None:
                if pull_up is None:
                    pull_up = self.default_pull_up
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
            try:
                self.pins[pin_number]['obj'] = Button(pin_number, pull_up=False, pin_factory=self.remote_gpio)
            except PinFixedPull:
                self.pins[pin_number]['obj'] = Button(pin_number, pull_up=True, pin_factory=self.remote_gpio)
                return False
            return True
        return False

    def write(self, pin_number: int, value: bool) -> bool:
        if (
            pin_number in self.pins and
            self.pins[pin_number]['mode'] in [None, self.MODE_OUT]
        ):
            try:
                self.pins[pin_number]['mode'] = self.MODE_OUT
                if self.pins[pin_number]['obj'] is None:
                    self.pins[pin_number]['obj'] = LED(pin_number, pin_factory=self.remote_gpio)
                if value:
                    self.pins[pin_number]['obj'].on()
                else:
                    self.pins[pin_number]['obj'].off()
                return True
            except GPIOPinInUse:
                del(self.pins[pin_number])
            except ValueError:
                del(self.pins[pin_number])
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
            pi_info = self.remote_gpio.pi_info if self.remote_gpio else pi_info_funct()
            self._pi_info = {
                'model': pi_info.model,
                'bluetooth': pi_info.bluetooth,
                'csi': pi_info.csi,
                'dsi': pi_info.dsi,
                'ethernet': pi_info.ethernet,
                'manufacturer': pi_info.manufacturer,
                'memory': pi_info.memory,
                'pcb_revision': pi_info.pcb_revision,
                'released': pi_info.released,
                'revision': pi_info.revision,
                'soc': pi_info.soc,
                'storage': pi_info.storage,
                'usb': pi_info.usb,
                'wifi': pi_info.wifi,
                'pins': [],
            }
            for header in pi_info.headers.values():
                for pin in header.pins.values():
                    #if pin.function not in ['3V3', '5V', 'GND']:
                    if pin.function.startswith('GPIO'):
                        pin_number = int(pin.function.replace('GPIO', ''))
                        self.pins[pin_number] = {
                            'function': pin.function,
                            'pull_up': pin.pull_up,
                            'number': pin.number,
                            'pin': pin_number,
                            'mode': None,
                            'obj': None,
                        }
            self._pi_info['pins'] = self.pins
        return self._pi_info


if __name__ == '__main__':
    REMOTE_PI_HOST = '127.0.0.1'
    REMOTE_PI_PORT = 8888
    REMOTE_GPIO = RemoteGPIO(REMOTE_PI_HOST, REMOTE_PI_PORT)
    print(REMOTE_GPIO.get_pi_info())
