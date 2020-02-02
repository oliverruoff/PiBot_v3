import RPi.GPIO as GPIO
from time import sleep

IN1 = 19
IN2 = 13
IN3 = 6
IN4 = 5
ENA = 26
ENB = 11

GPIO.setmode(GPIO.BCM)

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

GPIO.output(IN1, GPIO.LOW)
GPIO.output(IN2, GPIO.LOW)
GPIO.output(IN3, GPIO.LOW)
GPIO.output(IN4, GPIO.LOW)

# right motor
p_a = GPIO.PWM(ENA, 1000)
p_a.start(0)
# left motor
p_b = GPIO.PWM(ENB, 1000)
p_b.start(0)

p_a.ChangeDutyCycle(75)
p_b.ChangeDutyCycle(75)


def change_speed_left(speed):
    p_b.ChangeDutyCycle(speed)


def change_speed_right(speed):
    p_a.ChangeDutyCycle(speed)


def turn_left_wheel(forward=True):
    if forward:
        GPIO.output(IN3, GPIO.HIGH)
        GPIO.output(IN4, GPIO.LOW)
    else:
        GPIO.output(IN3, GPIO.LOW)
        GPIO.output(IN4, GPIO.HIGH)


def turn_right_wheel(forward=True):
    if forward:
        GPIO.output(IN1, GPIO.HIGH)
        GPIO.output(IN2, GPIO.LOW)
    else:
        GPIO.output(IN1, GPIO.LOW)
        GPIO.output(IN2, GPIO.HIGH)


def turn_left():
    turn_right_wheel()
    turn_left_wheel(False)


def turn_right():
    turn_right_wheel(False)
    turn_left_wheel()


def move_front():
    turn_right_wheel()
    turn_left_wheel()


def move_back():
    turn_right_wheel(False)
    turn_left_wheel(False)


def stop_motors():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)


def turn_degree(degree):
    if degree < 180:
        print('Turning', degree, '° to the right :)')
        turn_right()
    else:
        degree = 360 - degree
        print('Turning', degree, '° to the left :)')
        turn_left()
    sleep(degree/360*2.5)  # times to, since bot takes around 2.5s for 360°
    stop_motors()


def say_no():
    for i in range(2):
        turn_right()   
        time.sleep(0.4
        turn_left()
        time.sleep(0.4