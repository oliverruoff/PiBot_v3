import RPi.GPIO as GPIO
from time import sleep
import bot.movement.powertrain as powertrain

print("\n")
print("The default speed & direction of motor is STOP & Forward.....")
print("s-stop f-forward b-backward r-right l-left e-exit")
print("\n")

pt = powertrain.powertrain(0x68)

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
