import os
from flask import Flask, render_template, send_from_directory, jsonify
from my_pi import RemoteGPIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=template_dir)

REMOTE_PI_HOST = '127.0.0.1'
REMOTE_GPIO = RemoteGPIO(REMOTE_PI_HOST)


@app.route('/')
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
    if action not in ['read', 'on', 'off', 'info']:
        data['error'].append('Invalid action')

    if not data['error']:
        if action == 'read':
            data['data'] = REMOTE_GPIO.read(pin)
        elif action == 'on':
            REMOTE_GPIO.write(pin, True)
        elif action == 'off':
            REMOTE_GPIO.write(pin, False)
        elif action == 'info':
            info = REMOTE_GPIO.pins[pin]
            data['data'] = {
                'function': info['function'],
                'pull_up': info['pull_up'],
                'mode': info['mode'],
            }
        elif action == 'pull_up':
            REMOTE_GPIO.pull_up()
        elif action == 'pull_down':
            REMOTE_GPIO.pull_down()
    return jsonify(data)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
