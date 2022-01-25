import RPi.GPIO as GPIO
import time

GPIO.cleanup()
GPIO.setmode(GPIO.BCM)


def clear():
    GPIO.cleanup()


class control_components:
    class output_pin:
        def enable(self):
            self.status = True

        def disable(self):
            self.status = False

        def __init__(self, pin_num, active=None):
            self.status = None
            self.active = active
            if pin_num == "":
                self.disable()
            elif type(pin_num) == int:
                self.enable()
                self.pin_num = pin_num
                GPIO.setup(self.pin_num, GPIO.OUT)

        def set_active(self,active):
            self.active = active

        def set_pin(self, num):
            self.pin_num = num
            GPIO.setup(self.pin_num, GPIO.OUT)

        def on(self):
            if self.status:
                GPIO.output(self.pin_num, self.active)

        def off(self):
            if self.status:
                GPIO.output(self.pin_num, not self.active)

    class input_pin:
        def enable(self):
            self.status = True

        def disable(self):
            self.status = False

        def __init__(self, pin_num, active=None):
            self.status = None
            self.active = active
            if pin_num == "":
                self.disable()
            elif type(pin_num) == int:
                self.enable()
                self.pin_num = pin_num
                GPIO.setup(self.pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        def set_active(self,active):
            self.active = active

        def set_pin(self, num):
            self.pin_num = num
            GPIO.setup(self.pin_num, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        def get_value(self):
            if self.status and self.active:
                return GPIO.input(self.pin_num) == GPIO.HIGH  # return True or False
            elif self.status and not self.active:
                return not GPIO.input(self.pin_num) == GPIO.HIGH  # return True or False

    class ultrasonic:
        def __init__(self, trig=18, echo=24):
            self.trig = trig
            self.echo = echo
            GPIO.setup(self.trig, GPIO.OUT)
            GPIO.setup(self.echo, GPIO.IN)

        def distanceultra(self):
            # set Trigger to HIGH
            GPIO.output(self.trig, True)

            # set Trigger after 0.01ms to LOW
            time.sleep(0.00001)
            GPIO.output(self.trig, False)

            StartTime = time.time()
            StopTime = time.time()

            # save StartTime
            while GPIO.input(self.echo) == 0:
                StartTime = time.time()

            # save time of arrival
            while GPIO.input(self.echo) == 1:
                StopTime = time.time()

            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            distance = (TimeElapsed * 34300) / 2

            return distance
