import math
import time

from movement import motor_controls as mc
from sensing import mpu6050


if __name__ == "__main__":
    SLEEP_TIME = 0.1
    mc.change_speed_left(40)
    mc.change_speed_right(40)
    degree_turned = 0

    while degree_turned < 90:
        mc.turn_left()
        time.sleep(SLEEP_TIME)
        mpu = mpu6050.mpu6050(0x68)
        gyro_data = mpu.get_gyro_data()
        gyro_z = gyro_data['z']
        gyro_z_scaled = gyro_z * SLEEP_TIME
        degree_turned += gyro_z_scaled
        print('Turned: ', degree_turned)
    mc.stop_motors()