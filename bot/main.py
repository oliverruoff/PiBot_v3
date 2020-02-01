import math
import time

from movement import motor_controls as mc
from sensing import mpu6050


if __name__ == "__main__":
    SENSOR_DRIFT = -1.8378
    SLEEP_TIME = 0.1
    TURN_DEGREE = 90

    motor_speed = 30
    mc.change_speed_left(motor_speed)
    mc.change_speed_right(motor_speed)
    mpu = mpu6050.mpu6050(0x68)

    degree_turned = 0
    while degree_turned < TURN_DEGREE:
        if degree_turned > (TURN_DEGREE - (TURN_DEGREE / 10)):
            motor_speed = 20
            mc.change_speed_left(motor_speed)
            mc.change_speed_right(motor_speed)
        mc.turn_left()
        time.sleep(SLEEP_TIME)
        gyro_z_scaled =  mpu.get_gyro_data()['z'] * SLEEP_TIME - SENSOR_DRIFT
        degree_turned += gyro_z_scaled
        print('Turned: ', degree_turned)

    mc.turn_right()
    time.sleep(0.1)
    mc.stop_motors()
