import math
import time

from movement import motor_controls as mc
from sensing import mpu6050


if __name__ == "__main__":
    SENSOR_DRIFT = -1.8378
    SLEEP_TIME = 0.1
    MOTOR_SPEED = 30
    TURN_DEGREE = 90
    mc.change_speed_left(MOTOR_SPEED)
    mc.change_speed_right(MOTOR_SPEED)

    degree_turned = 0
    while degree_turned < TURN_DEGREE:
        mc.turn_left()
        time.sleep(SLEEP_TIME)
        mpu = mpu6050.mpu6050(0x68)
        gyro_data = mpu.get_gyro_data()
        gyro_z = gyro_data['z']
        gyro_z_scaled = gyro_z * SLEEP_TIME - SENSOR_DRIFT
        degree_turned += gyro_z_scaled
        print('Turned: ', degree_turned)
    mc.stop_motors()