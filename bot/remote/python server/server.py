from flask import Flask
from flask import request
import time

from movement import powertrain
from sensing import mpu6050
from combination import gyro_movement

app = Flask(__name__)


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
    if y > 0:
        pt.move_front()
    elif y < 0:
        pt.move_back()
    else:
        pt.stop_motors()
    if x > 0:
        pt.change_speed_left(x)
        pt.change_speed_right(100-x)
    elif x < 0:
        pt.change_speed_right(abs(x))
        pt.change_speed_left(100-abs(x))
    else:
        print('x is 0 -> Doing nothing')
        pass


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
    app.run(host='0.0.0.0')
