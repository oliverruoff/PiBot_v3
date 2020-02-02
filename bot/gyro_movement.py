import time

from bot.movement import motor_controls as mc
from bot.sensing import mpu6050


def get_gyro_z_sensor_drift(samples=10):
    print('Getting current gyro z sensor drift...')
    mpu = mpu6050.mpu6050(0x68)
    val_sum = 0
    for _ in range(samples):
        val_sum += mpu.get_gyro_data()['z']
        time.sleep(0.1)
    gyro_z_sensor_drift = val_sum/samples
    print('Gyro z sensor drift:', gyro_z_sensor_drift)
    return gyro_z_sensor_drift


def is_moving(gyro_z_sensor_drift=-1.8):
    '''
    Checks if the robot is currently moving (or might need
    to hand over to unstuck strategy)
    '''
    Z_MOVEMENT_THRESHOLD = 1.2
    mpu = mpu6050.mpu6050(0x68)
    gyro_z = abs(mpu.get_gyro_data()['z'] - gyro_z_sensor_drift)
    # print('Gyro z:', gyro_z)
    if gyro_z > Z_MOVEMENT_THRESHOLD:
        return True
    else:
        for _ in range(3):
            gyro_z = abs(mpu.get_gyro_data()['z'] - gyro_z_sensor_drift)
            # print('Retrying gyro z:', gyro_z)
            if gyro_z > Z_MOVEMENT_THRESHOLD:
                return True
        return False

def gyro_turn(turn_degree, right=True, sensor_drift=-1.8):
    SLEEP_TIME = 0.1
    motor_speed = 50
    mc.change_speed_left(motor_speed)
    mc.change_speed_right(motor_speed)
    mpu = mpu6050.mpu6050(0x68)

    last_z_turn = 0
    degree_turned = 0
    while degree_turned < turn_degree:
        if degree_turned > (turn_degree - (turn_degree / 5)):
            motor_speed = 20
            mc.change_speed_left(motor_speed)
            mc.change_speed_right(motor_speed)
        if right:
            mc.turn_right()
        else:
            mc.turn_left()
        time.sleep(SLEEP_TIME)
        gyro_z_scaled =  abs(mpu.get_gyro_data()['z'] * SLEEP_TIME - sensor_drift)
        last_z_turn = gyro_z_scaled
        degree_turned += gyro_z_scaled
        remaining_degree = turn_degree - degree_turned
        remaining_seconds_to_turn = SLEEP_TIME / last_z_turn * remaining_degree
        if remaining_degree < last_z_turn:
            if remaining_seconds_to_turn > 0:
                time.sleep(remaining_seconds_to_turn)
            break
    motor_speed = 50
    mc.change_speed_left(motor_speed)
    mc.change_speed_right(motor_speed)
    # hard stop
    if right:
        mc.turn_left()
    else:
        mc.turn_left()
    time.sleep(0.1)
    mc.stop_motors()