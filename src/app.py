import os
from flask import Flask, render_template, jsonify
from my_pi import RemoteGPIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)

REMOTE_PI_HOST = '127.0.0.1'
REMOTE_PI_PORT = 8888
REMOTE_GPIO = RemoteGPIO(REMOTE_PI_HOST, REMOTE_PI_PORT)

INDEX_PINS = {
    17: {
        'pin': 17,
        'type': 'led',
        'name': 'light',
        'pull_up': False,
    },
}


@app.route('/info')
def info():
    return render_template('pi_info.html', ** REMOTE_GPIO.get_pi_info())


@app.route('/<int:pin>/<action>/')
def pin_action(pin, action):
    data = {
        'pin': pin,
        'action': action,
        'error': [],
        'data': None,
    }
    if not REMOTE_GPIO.pins:
        REMOTE_GPIO.get_pi_info()
    if pin not in REMOTE_GPIO.pins:
        data['error'].append('Invalid Pin')
    if action not in ['read', 'on', 'off', 'info', 'pull_up', 'pull_down']:
        data['error'].append('Invalid action')

    if not data['error']:
        pi_info = REMOTE_GPIO.pins[pin]
        if action == 'read':
            data['data'] = {
                'value': REMOTE_GPIO.read(pin),
                'pull_up': pi_info['pull_up'],
                'mode': pi_info['mode'],
            }
        elif action == 'on':
            REMOTE_GPIO.write(pin, True)
        elif action == 'off':
            REMOTE_GPIO.write(pin, False)
        elif action == 'info':
            data['data'] = {
                'name': pi_info['name'],
                'pull_up': pi_info['pull_up'],
                'mode': pi_info['mode'],
                'number': pi_info['number'],
                'value': None,
            }
            if pi_info['mode'] in [RemoteGPIO.MODE_IN, RemoteGPIO.MODE_OUT]:
                data['data']['value'] = REMOTE_GPIO.read(pin)
        elif action == 'pull_up':
            REMOTE_GPIO.pull_up(pin)
        elif action == 'pull_down':
            REMOTE_GPIO.pull_down(pin)
    return jsonify(data)


@app.route('/')
def index():
    context = {
        'pins': INDEX_PINS,
    }
    return render_template('index.html', **context)


if __name__ == '__main__':
    pi_info = REMOTE_GPIO.get_pi_info()
    for pin in INDEX_PINS.values():
        pin_type = pin.get('type', 'led')
        if pin_type == 'led':
            REMOTE_GPIO.write(pin.get('pin'), False)
        elif pin_type == 'button':
            REMOTE_GPIO.read(pin.get('pin'), pin.get('pull_up', True))
    app.run(host='0.0.0.0')
