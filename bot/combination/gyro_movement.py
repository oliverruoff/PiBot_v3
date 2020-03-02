from movement import powertrain
from sensing import mpu6050

from threading import Thread
import time

class gyro_movement:

    def __init__(self, gyro_accel, powertrain):
        self.gyro_accel
        self.powertrain
        self.is_driving = False

    def gyro_turn(self, turn_degree, right=True, motor_speed=75):
        """Turns robot by specified degree, always use this function to turn
        robot precisely. Uses gyro sensor.

        Arguments:
            turn_degree {int} -- Degree to turn, has to be positive, 
            direction is controlled via "right" argument.

        Keyword Arguments:
            right {bool} -- Turns right if true, else left. (default: {True})
            motor_speed {int} -- Defines how fast robot turns around (0-100) (default: {75})
        """
        SLEEP_TIME = 0.1
        GYRO_MULTIPLIER = 1.21869252  # needs to be applicated
        _motor_speed = motor_speed
        self.powertrain.change_speed_left(_motor_speed)
        self.powertrain.change_speed_right(_motor_speed)

        old_speed_left = self.powertrain.motor_speed_left
        old_speed_right = self.powertrain.motor_speed_right

        last_z_turn = 0
        degree_turned = 0
        old_time = 0
        while degree_turned < turn_degree:
            if degree_turned > (turn_degree - (turn_degree / 5)):
                _motor_speed = 20
                self.powertrain.change_speed_left(_motor_speed)
                self.powertrain.change_speed_right(_motor_speed)
            if right:
                self.powertrain.turn_right()
            else:
                self.powertrain.turn_left()
            time.sleep(SLEEP_TIME)
            passed_time = SLEEP_TIME if old_time == 0 else time.time() - old_time
            gyro_z_scaled = abs((self.gyro_accel.get_gyro_data()[
                                'z'] - self.gyro_z_sensor_drift) * passed_time)
            old_time = time.time()
            last_z_turn = gyro_z_scaled
            degree_turned += gyro_z_scaled * GYRO_MULTIPLIER
            remaining_degree = turn_degree - degree_turned
            remaining_seconds_to_turn = SLEEP_TIME / last_z_turn * remaining_degree
            if remaining_degree < last_z_turn:
                if remaining_seconds_to_turn > 0:
                    time.sleep(remaining_seconds_to_turn)
                break
        _motor_speed = motor_speed
        self.powertrain.change_speed_left(_motor_speed)
        self.powertrain.change_speed_right(_motor_speed)
        # hard stop
        self.powertrain.break_motors()
        self.powertrain.change_speed_left(old_speed_left)
        self.powertrain.change_speed_right(old_speed_right)

    def gyro_move_start(self, forward):
        '''
        Moves robot forward or backward, stabilized with gyro sensor.
        Always use this function to move robot! 
        To stop movement, call "gyro_move_stop()".
        Uses self.is_driving field variable.
        '''
        if forward:
            self.powertrain.move_front()
        else:
            self.powertrain.move_back()
        self.is_driving = True
        movement_thread = Thread(
            target=self._gyro_supported_movement, args=(forward, ))
        movement_thread.start()

    def gyro_move_stop(self):
        """Use this function some time after calling 'gyro_move_start()',
        to stop the robot. The robot will automatically break (not only stop
        spinning motors). Sets field variable 'self.is_driving'
        """
        self.is_driving = False

    def _gyro_supported_movement(self, forward):
        """Do not use this function! To move the robot, call the functions 'gyro_move_start()'
        and 'gyro_move_stop()'.

        Arguments:
            forward {bool} -- Moves forward if True, else backward.
        """
        old_motor_speed_left = self.powertrain.motor_speed_left
        old_motor_speed_right = self.powertrain.motor_speed_right
        sleep_time_s = 0.1
        while self.is_driving:
            gyro_z = self.gyro_accel.get_gyro_data(
            )['z'] - self.gyro_z_sensor_drift
            if forward:
                if gyro_z > 0:
                    motor_speed_right += int(abs(gyro_z)/2)
                    motor_speed_left -= int(abs(gyro_z)/2)
                else:
                    motor_speed_right -= int(abs(gyro_z)/2)
                    motor_speed_left += int(abs(gyro_z)/2)
            else:
                if gyro_z > 0:
                    motor_speed_right -= int(abs(gyro_z)/2)
                    motor_speed_left += int(abs(gyro_z)/2)
                else:
                    motor_speed_right += int(abs(gyro_z)/2)
                    motor_speed_left -= int(abs(gyro_z)/2)

            motor_speed_left = 100 if motor_speed_left > 100 else motor_speed_left
            motor_speed_left = 0 if motor_speed_left < 0 else motor_speed_left

            motor_speed_right = 100 if motor_speed_right > 100 else motor_speed_right
            motor_speed_right = 0 if motor_speed_right < 0 else motor_speed_right


            # print('_________________________')
            # print('GyroZ:', gyro_z)
            # print('Adjusting Left motor speed:', self.motor_speed_left)
            # print('Adjusting Right motor speed:', self.motor_speed_right)
            # print('_________________________')
            self.powertrain.change_speed_left(motor_speed_left)
            self.powertrain.change_speed_right(motor_speed_right)
            time.sleep(sleep_time_s)
        self.powertrain.break_motors()