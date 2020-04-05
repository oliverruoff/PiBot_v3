from flask import Flask, request, send_file, Response, render_template
import time
import socket
import os
import io

import cv2

from movement import powertrain
from sensing import mpu6050, camera
from combination import gyro_movement

app = Flask(__name__)
vc = cv2.VideoCapture(0)


@app.route("/")
def hello():
    return "Online!"


@app.route("/turn")
def turn():
    direction = request.args.get('direction')
    degree = int(request.args.get('degree', default=90))
    if direction == 'left':
        sgm.gyro_turn(degree, right=False, motor_speed=90)
        return 'Turned %i degree to the %s.' % (degree, direction)
    elif direction == 'right':
        sgm.gyro_turn(degree, right=True, motor_speed=90)
        return 'Turned %i degree to the %s.' % (degree, direction)
    else:
        return 'Direction not supported!'


@app.route("/move")
def move():
    direction = request.args.get('direction')
    duration = float(request.args.get('duration', default=1))
    motorspeed = int(request.args.get('motorspeed', default=90))
    _dir = True
    if direction == 'forward':
        _dir = True
    elif direction == 'backward':
        _dir = False
    else:
        return 'Direction not supported!'
    sgm.gyro_move_start(_dir, motor_speed=motorspeed)
    time.sleep(duration)
    sgm.gyro_move_stop()
    return 'Moved %f seconds with motorspeed: %i to direction: %s' \
        % (duration, motorspeed, direction)


@app.route("/joystick")
def joystick():
    x = int(request.args.get('x'))
    y = int(request.args.get('y'))

    if x > 100:
        x = 100
    elif x < -100:
        x = -100

    if y > 100:
        y = 100
    elif y < -100:
        y = -100

    print('x:', x)
    print('y:', y)
    abs_y = abs(y)
    abs_x = abs(x)
    if x == 0 and y == 0:
        pt.break_motors()
        return 'Stopped motors.'

    if y > 0:
        pt.move_front()
    elif y < 0:
        pt.move_back()
    else:
        pass
        # pt.stop_motors()

    # Extra logic for better rotating movement
    if y < 15 and y > -15:
        if x > 0:
            pt.turn_left_wheel(True)
            pt.turn_right_wheel(False)
        if x < 0:
            pt.turn_left_wheel(False)
            pt.turn_right_wheel(True)
        pt.change_speed_left(abs(x))
        pt.change_speed_right(abs(x))
        return'Done.'


    if x > 0:
        left = abs_y
        right = int(abs_y - (abs_x*(abs_y/100)))
        print('Left:', left)
        print('Right:', right)
        pt.change_speed_left(left)
        pt.change_speed_right(right)
    elif x < 0:
        right = abs_y
        left = int(abs_y - (abs_x*(abs_y/100)))
        print('Left:', left)
        print('Right:', right)
        pt.change_speed_right(right)
        pt.change_speed_left(left)
    else:
        print('x is 0 -> Doing nothing')
        pass
    return 'Done'

@app.route("/remote")
def remote():
    html_file_path = os.path.join(dir_path, 'remote', 'python server','remote.html')

    return render_template(html_file_path, js_str=js_str)

def prepare_remote():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    print('ip:', ip)

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(dir_path, 'remote', 'python server','remote.html'), 'r') as file:
        html_str = file.read()
    with open(os.path.join(dir_path, 'remote', 'python server','joystick.js'), 'r') as file:
        js_str = file.read()

    html_str = html_str.replace('<<IP>>', ip)
    html_str = html_str.replace('<script src="joystick.js"></script>',
        '<script>' + js_str + '</script>')
    return html_str

def gen():
    """Video streaming generator function."""
    while True:
        rval, frame = vc.read()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        tmp_img_path = os.path.join(dir_path, 'remote', 'python server', 'tmp_photo', 'tmp_img.jpg')
        cv2.imwrite(tmp_img_path, frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open(tmp_img_path, 'rb').read() + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/photo")
def photo():
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #camera.take_picture(
    #    os.path.join(
    #        dir_path, 'remote', 'python server','tmp_photo', 'live_tmp.jpg'))
    image_binary = camera.get_picture()
    return send_file(io.BytesIO(image_binary),
                    attachment_filename='live.jpg',
                    mimetype='image/jpeg')


if __name__ == "__main__":
    # powertrain
    POWERTRAIN_IN1_PIN = 19
    POWERTRAIN_IN2_PIN = 13
    POWERTRAIN_IN3_PIN = 6
    POWERTRAIN_IN4_PIN = 5
    POWERTRAIN_ENA_PIN = 26
    POWERTRAIN_ENB_PIN = 11
    MOTORSPEED_LEFT = 75
    MOTORSPEED_RIGHT = 75

    pt = powertrain.powertrain(
        POWERTRAIN_IN1_PIN,
        POWERTRAIN_IN2_PIN,
        POWERTRAIN_IN3_PIN,
        POWERTRAIN_IN4_PIN,
        POWERTRAIN_ENA_PIN,
        POWERTRAIN_ENB_PIN,
        MOTORSPEED_LEFT,
        MOTORSPEED_RIGHT)

    mpu = mpu6050.mpu6050(0x68)

    gyro_z_sensor_drift = mpu.get_gyro_z_sensor_drift()

    sgm = gyro_movement.gyro_movement(mpu, pt, gyro_z_sensor_drift)

    camera = camera.camera()

    # remote_html = prepare_remote()

    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(dir_path, 'remote', 'python server','joystick.js'), 'r') as file:
        js_str = file.read()

    app.run(host='0.0.0.0')