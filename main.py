import math
import time

from bot.movement import motor_controls as mc
from bot import gyro_movement as gm
from bot.sensing import ultrasonic as us

if __name__ == "__main__":

    while True:
        try:
            dist = us.get_distance()
            med_dist = us.get_median_distance()
            print('Dist:', dist, '| med_dist:', med_dist)
            if dist < 20:
                mc.stop_motors()
                gm.gyro_turn(50, False)
            else:
                mc.move_front()
        except KeyboardInterrupt:
            break