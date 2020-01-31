import RPi.GPIO as GPIO
from time import sleep
import motor_controls as mc

print("\n")
print("The default speed & direction of motor is STOP & Forward.....")
print("s-stop f-forward b-backward r-right l-left e-exit")
print("\n")

while(1):

    x = input()

    if x == 's':
        print("stop")
        mc.stop_motors()

    elif x == 'f':
        print("forward")
        mc.move_front()

    elif x == 'b':
        print("backward")
        mc.move_back()

    elif x == 'r':
        print('right')
        mc.turn_right()

    elif x == 'l':
        print('left')
        mc.turn_left

    elif x == 'e':
        GPIO.cleanup()
        break

    else:
        print("<<<  wrong input  >>>")
        print("please enter the defined data to continue.....")
