"""
Holds functionality for the ultra sonic sensor.
"""
import RPi.GPIO as GPIO
import time


class hcsr04:

    trigger_pin = None
    echo_pin = None

    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)

    def get_distance(self):
        """Triggers the ultra sonic sensor and measures the distance.

        Returns:
            float -- Distance measured in cm.
        """
        GPIO.output(self.trigger_pin, True)

        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        start_time = time.time()
        stop_time = time.time()

        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()

        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()

        time_elapsed = stop_time - start_time
        # multiplay with speed of sound (34300 cm/s)
        # divide by 2 (since double distance)
        distance = (time_elapsed * 34300) / 2

        return round(distance)
