import RPi.GPIO as GPIO
from time import sleep


class powertrain:

    in1 = None
    in2 = None
    in3 = None
    in4 = None
    ena = None
    enb = None

    motor_speed_left = 75
    motor_speed_right = 75

    def __init__(self,
                 in1,
                 in2,
                 in3,
                 in4,
                 ena,
                 enb,
                 motor_speed_left=75,
                 motor_speed_right=75):
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.ena = ena
        self.enb = enb
        self.motor_speed_left = motor_speed_left
        self.motor_speed_right = motor_speed_right

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(in3, GPIO.OUT)
        GPIO.setup(in4, GPIO.OUT)
        GPIO.setup(ena, GPIO.OUT)
        GPIO.setup(enb, GPIO.OUT)

        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
        GPIO.output(in3, GPIO.LOW)
        GPIO.output(in4, GPIO.LOW)

        # right motor
        self.p_a = GPIO.PWM(ena, 1000)
        self.p_a.start(0)
        # left motor
        self.p_b = GPIO.PWM(enb, 1000)
        self.p_b.start(0)

        self.p_a.ChangeDutyCycle(75)
        self.p_b.ChangeDutyCycle(75)

    def change_speed_left(self, speed):
        self.p_b.ChangeDutyCycle(speed)

    def change_speed_right(self, speed):
        self.p_a.ChangeDutyCycle(speed)

    def turn_left_wheel(self, forward=True):
        if forward:
            GPIO.output(self.in3, GPIO.HIGH)
            GPIO.output(self.in4, GPIO.LOW)
        else:
            GPIO.output(self.in3, GPIO.LOW)
            GPIO.output(self.in4, GPIO.HIGH)

    def break_motors(self):
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.HIGH)
        GPIO.output(self.in3, GPIO.HIGH)
        GPIO.output(self.in4, GPIO.HIGH)
        sleep(0.5)
        self.stop_motors()

    def turn_right_wheel(self, forward=True):
        if forward:
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)
        else:
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.HIGH)

    def turn_left(self):
        self.turn_right_wheel()
        self.turn_left_wheel(False)

    def turn_right(self):
        self.turn_right_wheel(False)
        self.turn_left_wheel()

    def move_back(self):
        self.turn_right_wheel()
        self.turn_left_wheel()

    def move_front(self):
        self.turn_right_wheel(False)
        self.turn_left_wheel(False)

    def stop_motors(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.in3, GPIO.LOW)
        GPIO.output(self.in4, GPIO.LOW)

    def say_no(self):
        for _ in range(2):
            self.turn_right()
            sleep(0.2)
            self.turn_left()
            sleep(0.2)
