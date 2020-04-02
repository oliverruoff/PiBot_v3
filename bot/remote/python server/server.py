from flask import Flask
from flask import request

from PiBot.bot.movement import powertrain
from PiBot_v3.bot.sensing import mpu6050
from PiBot_v3.bot.combination import gyro_movement

app = Flask(__name__)


@app.route("/")
def hello():
    return "Online!"


@app.route("/turn")
def turn():
    global pt
    global mpu
    direction = request.args.get('direction')
    if direction == 'left':
        sgm.gyro_turn(90, right=False, motor_speed=90)
    elif direction == 'right':
        sgm.gyro_turn(90, right=True, motor_speed=90)
    else:
        return 'Direction not supported!'


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

    sgm = gyro_movement.gyro_movement(mpu, powertrain, gyro_z_sensor_drift)
    app.run()
