import RPi.GPIO as GPIO
from time import sleep
import bot.movement.powertrain as powertrain

print("\n")
print("The default speed & direction of motor is STOP & Forward.....")
print("s-stop f-forward b-backward r-right l-left e-exit")
print("\n")

# powertrain
POWERTRAIN_IN1_PIN = 19
POWERTRAIN_IN2_PIN = 13
POWERTRAIN_IN3_PIN = 6
POWERTRAIN_IN4_PIN = 5
POWERTRAIN_ENA_PIN = 26
POWERTRAIN_ENB_PIN = 11
MOTORSPEED_LEFT = 75
MOTORSPEED_RIGHT = 75

pt = powertrain.powertrain(
    POWERTRAIN_IN1_PIN,
    POWERTRAIN_IN2_PIN,
    POWERTRAIN_IN3_PIN,
    POWERTRAIN_IN4_PIN,
    POWERTRAIN_ENA_PIN,
    POWERTRAIN_ENB_PIN,
    MOTORSPEED_LEFT,
    MOTORSPEED_RIGHT)

while(1):

    x = input()

    if x == 's':
        print("stop")
        pt.stop_motors()

    elif x == 'f':
        print("forward")
        pt.move_front()

    elif x == 'b':
        print("backward")
        pt.move_back()

    elif x == 'r':
        print('right')
        pt.turn_right()

    elif x == 'l':
        print('left')
        pt.turn_left()

    elif x == 'e':
        GPIO.cleanup()
        break

    else:
        print("<<<  wrong input  >>>")
        print("please enter the defined data to continue.....")
