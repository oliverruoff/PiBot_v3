import time
from multiprocessing.pool import ThreadPool
import RPi.GPIO as GPIO
from threading import Thread
import os
from datetime import datetime

from movement import powertrain
from sensing import mpu6050, hcsr04, microphone_hotword as microphone, speaker, camera
from combination import gyro_movement

GPIO.setmode(GPIO.BCM)


class Robot():
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

        self.gyro_z_sensor_drift = self.gyro_accel.get_gyro_z_sensor_drift()

        self.gm = gyro_movement.gyro_movement(
            self.gyro_accel, self.powertrain, self.gyro_z_sensor_drift)

    def start(self):
        self.speaker.say_hi()
        while True:
            spoken_words = self.microphone.recognize_speech().lower()
            print('I understood:', spoken_words)
            if any(ext in spoken_words for ext in ['links']):
                print('Turning left.')
                self.gm.gyro_turn(90, False)
            elif any(ext in spoken_words for ext in ['rechts']):
                print('Turning right.')
                self.gm.gyro_turn(90, True)
            elif any(ext in spoken_words for ext in ['vorwärts', 'vor', 'los', 'fahr']):
                print('Moving forward.')
                self.powertrain.move_front()
                time.sleep(3)
                self.powertrain.stop_motors()
            elif any(ext in spoken_words for ext in ['rückwärts', 'zurück', 'hinter']):
                print('Moving backward.')
                self.powertrain.move_back()
                time.sleep(3)
                self.powertrain.stop_motors()
            elif any(ext in spoken_words for ext in ['herum']):
                print('Turning around.')
                self.gm.gyro_turn(180, True)
            elif any(ext in spoken_words for ext in ['suche', 'finde']):
                print('Searching object.')
                self.search_object('potted plant')
            else:
                print('No recognized command! ->', spoken_words)

    def turn_look_for_object(self, gyro_movement, object_name):
        for _ in range(9):
            x_diff, box_img_ratio = self.camera.look_for_object(object_name)
            if x_diff != 0 and box_img_ratio != 0:
                return x_diff, box_img_ratio
            gyro_movement.gyro_turn(40, motor_speed=100)
        return 0, 0

    def search_object(self, search_object):
        self.speaker.say_eva()

        # Precision of how precise the robot will focus the object.
        # Don't make this too small, or the robot will continuouosly try
        # to focus the object, since it can't make precise enough movements.
        DEGREE_PRECISION = 8
        # Robot will stop approaching object, when rectangle around obj is 
        # at this ratio. Increase to make robot approach closer.
        OBJECT_RATIO_FOR_APPROACHING = 0.8

        while True:
            x_diff, box_img_ratio = self.turn_look_for_object(
                self.gm, search_object)
            if x_diff == 0 and box_img_ratio == 0:
                print('Lost object!')
                return
            self.speaker.say_whoa()
            if (abs(x_diff)) > DEGREE_PRECISION:
                right = True if x_diff < 0 else False
                self.gm.gyro_turn(abs(x_diff), right)
            else:
                if box_img_ratio < OBJECT_RATIO_FOR_APPROACHING:
                    self.gm.gyro_move_start(True, 90)
                    time.sleep(1)
                    self.gm.gyro_move_stop()
                else:
                    print('Found you!')
                    return
                

    def _test(self):
        self.microphone.start_listening()
            

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
mic = microphone.microphone('models/Wall-e.pmdl')
speaker = speaker.speaker()
camera = camera.camera()

robot = Robot(us, pt, mpu, mic, speaker, camera)
robot._test()
