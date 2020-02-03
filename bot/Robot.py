import time

from movement import powertrain
from sensing import mpu6050,hcsr04

class Robot():

    motor_speed_left = 75
    motor_speed_right = 75
    gyro_z_sensor_drift = -1.8

    ultrasonic = None
    powertrain = None
    gyro_accel = None


    def __init__(self, ultrasonic, powertrain, gyro_accel):
        self.ultrasonic = ultrasonic
        self.powertrain = powertrain
        self.gyro_accel = gyro_accel


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
        Z_MOVEMENT_THRESHOLD = 1.2
        mpu = mpu6050.mpu6050(0x68)
        gyro_z = abs(mpu.get_gyro_data()['z'] - self.gyro_z_sensor_drift)
        # print('Gyro z:', gyro_z)
        if gyro_z > Z_MOVEMENT_THRESHOLD:
            return True
        else:
            for _ in range(retries):
                gyro_z = abs(mpu.get_gyro_data()['z'] - self.gyro_z_sensor_drift)
                # print('Retrying gyro z:', gyro_z)
                if gyro_z > Z_MOVEMENT_THRESHOLD:
                    return True
            return False

    def gyro_turn(self, turn_degree, right=True):
        SLEEP_TIME = 0.1
        motor_speed = 50
        self.powertrain.change_speed_left(motor_speed)
        self.powertrain.change_speed_right(motor_speed)
        mpu = mpu6050.mpu6050(0x68)

        last_z_turn = 0
        degree_turned = 0
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
            gyro_z_scaled =  abs(mpu.get_gyro_data()['z'] * SLEEP_TIME - self.gyro_z_sensor_drift)
            last_z_turn = gyro_z_scaled
            degree_turned += gyro_z_scaled
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
        if right:
            self.powertrain.turn_left()
        else:
            self.powertrain.turn_left()
        time.sleep(0.1)
        self.powertrain.stop_motors()
        self.powertrain.change_speed_left(self.motor_speed_left)
        self.powertrain.change_speed_right(self.motor_speed_right)

    def start(self):
        self.get_gyro_z_sensor_drift()
        while True:
            try:
                dist = us.get_distance()
                if dist < 20:
                    max_dist = 0
                    degree = 0
                    for i in range(45, 405, 45):
                        self.gyro_turn(45, True)
                        dist = self.ultrasonic.get_distance()
                        if dist > max_dist:
                            max_dist = dist
                            degree = i
                    turn_right = True
                    log_str = 'right' # only needed for print
                    turn_degree = degree
                    if degree > 180:
                        turn_right = False
                        turn_degree = 360 - degree
                        log_str = 'left'
                    print('At degree:', degree, 'there is the most space, about:', max_dist, 'cm.')
                    print('So, I\'m turning', turn_degree, 'to the', log_str)
                    self.gyro_turn(turn_degree, turn_right)
                elif not self.is_moving(self.gyro_z_sensor_drift):
                    print('Looks like I\'m stuck, setting back.')
                    self.powertrain.move_back()
                    time.sleep(0.5)
                    self.gyro_turn(50, False)
                else:
                    self.powertrain.move_front()
                time.sleep(0.1)
            except KeyboardInterrupt:
                break


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

robot = Robot(us, pt, mpu)
robot.start()