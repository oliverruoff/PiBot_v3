import time
from multiprocessing.pool import ThreadPool
import RPi.GPIO as GPIO
from threading import Thread
import os

from movement import powertrain
from sensing import mpu6050, hcsr04, microphone, speaker, camera

GPIO.setmode(GPIO.BCM)


class Robot():

    motor_speed_left = 75
    motor_speed_right = 75
    gyro_z_sensor_drift = -1.8
    is_driving = False

    ultrasonic = None
    powertrain = None
    gyro_accel = None
    microphone = None

    def __init__(self, ultrasonic, powertrain, gyro_accel, microphone, speaker, camera):
        self.ultrasonic = ultrasonic
        self.powertrain = powertrain
        self.gyro_accel = gyro_accel
        self.microphone = microphone
        self.speaker = speaker
        self.camera = camera

        self.is_driving = False

        self.get_gyro_z_sensor_drift()

    def get_gyro_z_sensor_drift(self, samples=10):
        '''
        Fills field variable "self.gyro_z_sensor_drift", which is used in
        gyro sensor functions. (Call this function at startup of robot.)
        '''
        print('Getting current gyro z sensor drift...')
        mpu = mpu6050.mpu6050(0x68)
        val_sum = 0
        for _ in range(samples):
            val_sum += mpu.get_gyro_data()['z']
            time.sleep(0.1)
        gyro_z_sensor_drift = val_sum/samples
        print('Gyro z sensor drift:', gyro_z_sensor_drift)
        self.gyro_z_sensor_drift = gyro_z_sensor_drift

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

        old_speed_left = self.motor_speed_left
        old_speed_right = self.motor_speed_right

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
        old_motor_speed_left = self.motor_speed_left
        old_motor_speed_right = self.motor_speed_right
        sleep_time_s = 0.1
        while self.is_driving:
            gyro_z = self.gyro_accel.get_gyro_data(
            )['z'] - self.gyro_z_sensor_drift
            if forward:
                if gyro_z > 0:
                    self.motor_speed_right += int(abs(gyro_z)/2)
                    self.motor_speed_left -= int(abs(gyro_z)/2)
                else:
                    self.motor_speed_right -= int(abs(gyro_z)/2)
                    self.motor_speed_left += int(abs(gyro_z)/2)
            else:
                if gyro_z > 0:
                    self.motor_speed_right -= int(abs(gyro_z)/2)
                    self.motor_speed_left += int(abs(gyro_z)/2)
                else:
                    self.motor_speed_right += int(abs(gyro_z)/2)
                    self.motor_speed_left -= int(abs(gyro_z)/2)
            # print('_________________________')
            # print('GyroZ:', gyro_z)
            # print('Adjusting Left motor speed:', self.motor_speed_left)
            # print('Adjusting Right motor speed:', self.motor_speed_right)
            # print('_________________________')
            self.powertrain.change_speed_left(self.motor_speed_left)
            self.powertrain.change_speed_right(self.motor_speed_right)
            time.sleep(sleep_time_s)
        self.motor_speed_left = old_motor_speed_left
        self.motor_speed_right = old_motor_speed_right
        self.powertrain.break_motors()

    def get_most_space_direction(self):
        max_dist = 0
        degree = 0
        for i in range(45, 405, 45):
            self.gyro_turn(45, True)
            dist = self.ultrasonic.get_distance()
            if dist > max_dist:
                max_dist = dist
                degree = i
        turn_right = True
        log_str = 'right'  # only needed for print
        turn_degree = degree
        if degree > 180:
            turn_right = False
            turn_degree = 360 - degree
        log_str = 'left'
        print('At degree:', degree,
              'there is the most space, about:', max_dist, 'cm.')
        print('So, I should', turn_degree, 'to the', log_str)
        return (turn_degree, turn_right)

    def drive_around(self):
        while True:
            try:
                dist = us.get_distance()
                if dist < 50:
                    self.speaker.say_whoa()
                    self.powertrain.break_motors()
                    self.powertrain.act_no()
                    self.gyro_turn(70, False)
                else:
                    self.powertrain.move_front()
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

    def start(self):
        self.speaker.say_hi()
        while True:
            spoken_words = self.microphone.recognize_speech().lower()
            print('I understood:', spoken_words)
            if any(ext in spoken_words for ext in ['left']):
                print('Turning left.')
                self.gyro_turn(90, False)
            elif any(ext in spoken_words for ext in ['right']):
                print('Turning right.')
                self.gyro_turn(90, True)
            elif any(ext in spoken_words for ext in ['forward', 'front', 'go', 'drive']):
                print('Moving forward.')
                self.powertrain.move_front()
                time.sleep(3)
                self.powertrain.stop_motors()
            elif any(ext in spoken_words for ext in ['backward', 'back']):
                print('Moving backward.')
                self.powertrain.move_back()
                time.sleep(3)
                self.powertrain.stop_motors()
            elif any(ext in spoken_words for ext in ['auto', 'autonomous']):
                print('Started autonomous driving mode.')
                self.drive_around()
            elif any(ext in spoken_words for ext in ['around']):
                print('Turning around.')
                self.gyro_turn(180, True)
            else:
                print('No recognized command! ->', spoken_words)

    def test(self):
        for _ in range(5):
            self.camera.detect_objects_v2()
            self.gyro_turn(72)

    def _test(self):
        self.gyro_move_start(forward=True)
        time.sleep(4)
        self.gyro_move_stop()


# ultrasonic
US_TRIGGER_PIN = 17
US_ECHO_PIN = 4

# powertrain
POWERTRAIN_IN1_PIN = 19
POWERTRAIN_IN2_PIN = 13
POWERTRAIN_IN3_PIN = 6
POWERTRAIN_IN4_PIN = 5
POWERTRAIN_ENA_PIN = 26
POWERTRAIN_ENB_PIN = 11
MOTORSPEED_LEFT = 75
MOTORSPEED_RIGHT = 75


us = hcsr04.hcsr04(US_TRIGGER_PIN, US_ECHO_PIN)

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
mic = microphone.microphone()
speaker = speaker.speaker()
camera = camera.camera()

robot = Robot(us, pt, mpu, mic, speaker, camera)
robot.test()
