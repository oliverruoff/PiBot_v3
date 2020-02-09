import time
from multiprocessing.pool import ThreadPool
import RPi.GPIO as GPIO

from movement import powertrain
from sensing import mpu6050, hcsr04, microphone, speaker

GPIO.setmode(GPIO.BCM)


class Robot():

    motor_speed_left = 75
    motor_speed_right = 75
    gyro_z_sensor_drift = -1.8

    ultrasonic = None
    powertrain = None
    gyro_accel = None
    microphone = None

    def __init__(self, ultrasonic, powertrain, gyro_accel, microphone, speaker):
        self.ultrasonic = ultrasonic
        self.powertrain = powertrain
        self.gyro_accel = gyro_accel
        self.microphone = microphone
        self.speaker = speaker

        # start speech recognition
        self.listen()

    def listen(self):
        pass
        #t_pool = ThreadPool(1)
        #self.async_result = t_pool.map_async(self.microphone.recognize_speech, ())

    def get_gyro_z_sensor_drift(self, samples=10):
        print('Getting current gyro z sensor drift...')
        mpu = mpu6050.mpu6050(0x68)
        val_sum = 0
        for _ in range(samples):
            val_sum += mpu.get_gyro_data()['z']
            time.sleep(0.1)
        gyro_z_sensor_drift = val_sum/samples
        print('Gyro z sensor drift:', gyro_z_sensor_drift)
        self.gyro_z_sensor_drift = gyro_z_sensor_drift

    def is_moving(self, retries=5):
        '''
        Checks if the robot is currently moving (or might need
        to hand over to unstuck strategy)
        '''
        Z_MOVEMENT_THRESHOLD = 1.1
        mpu = mpu6050.mpu6050(0x68)
        gyro_z = abs(mpu.get_gyro_data()['z'] - self.gyro_z_sensor_drift)
        # print('Gyro z:', gyro_z)
        if gyro_z > Z_MOVEMENT_THRESHOLD:
            return True
        else:
            for _ in range(retries):
                gyro_z = abs(mpu.get_gyro_data()[
                             'z'] - self.gyro_z_sensor_drift)
                # print('Retrying gyro z:', gyro_z)
                if gyro_z > Z_MOVEMENT_THRESHOLD:
                    return True
            return False

    def gyro_turn(self, turn_degree, right=True):
        SLEEP_TIME = 0.1
        GYRO_MULTIPLIER = 1.072  # needs to be applicated
        motor_speed = 50
        self.powertrain.change_speed_left(motor_speed)
        self.powertrain.change_speed_right(motor_speed)

        last_z_turn = 0
        degree_turned = 0
        old_time = 0
        while degree_turned < turn_degree:
            if degree_turned > (turn_degree - (turn_degree / 5)):
                motor_speed = 20
                self.powertrain.change_speed_left(motor_speed)
                self.powertrain.change_speed_right(motor_speed)
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
        motor_speed = 50
        self.powertrain.change_speed_left(motor_speed)
        self.powertrain.change_speed_right(motor_speed)
        # hard stop
        self.powertrain.break_motors()
        self.powertrain.change_speed_left(self.motor_speed_left)
        self.powertrain.change_speed_right(self.motor_speed_right)

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
        self.get_gyro_z_sensor_drift()
        while True:
            try:
                dist = us.get_distance()
                if dist < 20:
                    self.speaker.say_whoa()
                    self.gyro_turn(50, False)
                else:
                    self.powertrain.move_front()
                time.sleep(0.1)
            except KeyboardInterrupt:
                break

    def start(self):
        self.speaker.say_hi()
        while True:
            spoken_words = self.microphone.recognize_speech().lower()
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
        self.drive_around()


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

robot = Robot(us, pt, mpu, mic, speaker)
robot.test()
