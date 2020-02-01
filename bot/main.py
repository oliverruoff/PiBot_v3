import math
import time

from movement import motor_controls as mc
from sensing import mpu6050


def gyro_turn(turn_degree, right=True, sensor_drift=-1.8378):
    SLEEP_TIME = 0.1
    motor_speed = 50
    mc.change_speed_left(motor_speed)
    mc.change_speed_right(motor_speed)
    mpu = mpu6050.mpu6050(0x68)

    last_z_turn = 0
    degree_turned = 0
    while degree_turned < turn_degree:
        print('---------------------')
        if degree_turned > (turn_degree - (turn_degree / 5)):
            print('Slowing down motors')
            motor_speed = 20
            mc.change_speed_left(motor_speed)
            mc.change_speed_right(motor_speed)
        mc.turn_left()
        time.sleep(SLEEP_TIME)
        gyro_z_scaled =  mpu.get_gyro_data()['z'] * SLEEP_TIME - sensor_drift
        last_z_turn = gyro_z_scaled
        print('Last z turn:', last_z_turn)
        degree_turned += gyro_z_scaled
        remaining_degree = turn_degree - degree_turned
        print('Remaining degree:', remaining_degree)
        remaining_seconds_to_turn = SLEEP_TIME / last_z_turn * remaining_degree
        print('Predicted remaining seconds to turn:', remaining_seconds_to_turn)
        print('Turned: ', degree_turned)
        print('---------------------')
        if remaining_degree < last_z_turn:
            print('Detecting that I should stop, only continuing for ', remaining_seconds_to_turn, 'seconds!')
            time.sleep(remaining_seconds_to_turn)
            break
    motor_speed = 50
    mc.change_speed_left(motor_speed)
    mc.change_speed_right(motor_speed)
    mc.turn_right()
    time.sleep(0.1)
    mc.stop_motors()

if __name__ == "__main__":
    gyro_turn(90, True)
