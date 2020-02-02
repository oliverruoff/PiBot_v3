import math
import time

from bot.movement import motor_controls as mc
from bot import gyro_movement as gm
from bot.sensing import ultrasonic as us

if __name__ == "__main__":

    motor_speed = 75
    mc.change_speed_right(motor_speed)
    mc.change_speed_left(motor_speed)
    gyro_z_sensor_drift = gm.get_gyro_z_sensor_drift()

    while True:
        try:
            dist = us.get_distance()
            if dist < 20:
                max_dist = 0
                degree = 0
                for i in range(45, 405, 45):
                    gm.gyro_turn(45, True, gyro_z_sensor_drift)
                    dist = us.get_median_distance()
                    if dist > max_dist:
                        max_dist = dist
                        degree = i
                turn_right = True
                log_str = 'right' # only needed for print
                if degree > 180:
                    turn_right = False
                    turn_degree = 360 - degree
                    log_str = 'left'
                print('At degree:', degree, 'there is the most space, about:', max_dist, 'cm.')
                print('So, I\'m turning', turn_degree, 'to the', log_str)
                gm.gyro_turn(turn_degree, turn_right, gyro_z_sensor_drift)
            elif not gm.is_moving(gyro_z_sensor_drift):
                print('Looks like I\'m stuck, setting back.')
                mc.move_back()
                time.sleep(0.5)
                gm.gyro_turn(50, False, gyro_z_sensor_drift)
            else:
                mc.move_front()
            time.sleep(0.1)
        except KeyboardInterrupt:
            break