import os
from flask import Flask, render_template, jsonify
from my_pi import RemoteGPIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)

REMOTE_PI_HOST = '127.0.0.1'
REMOTE_PI_PORT = 8888
REMOTE_GPIO = RemoteGPIO(REMOTE_PI_HOST, REMOTE_PI_PORT)


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
        pin_info = REMOTE_GPIO.pins[pin]
        if action == 'read':
            data['data'] = {
                'value': REMOTE_GPIO.read(pin),
                'pull_up': pin_info['pull_up'],
                'mode': pin_info['mode'],
            }
        elif action == 'on':
            REMOTE_GPIO.write(pin, True)
        elif action == 'off':
            REMOTE_GPIO.write(pin, False)
        elif action == 'info':
            data['data'] = {
                'function': pin_info['function'],
                'pull_up': pin_info['pull_up'],
                'mode': pin_info['mode'],
                'number': pin_info['number'],
            }
        elif action == 'pull_up':
            REMOTE_GPIO.pull_up(pin)
        elif action == 'pull_down':
            REMOTE_GPIO.pull_down(pin)
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
