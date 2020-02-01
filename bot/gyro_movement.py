import time

from bot.movement import motor_controls as mc
from bot.sensing import mpu6050


def gyro_turn(turn_degree, right=True, sensor_drift=-1.8378):
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