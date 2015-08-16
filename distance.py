import time
import RPi.GPIO as GPIO

if GPIO.getmode() == -1: GPIO.setmode(GPIO.BOARD)

class Distance():
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

    def measure(self):
        GPIO.output(self.trig, True); time.sleep(0.00001); GPIO.output(self.trig, False)
        while GPIO.input(self.echo)==0: pulse_start = time.time()
        while GPIO.input(self.echo)==1: pulse_end = time.time()
        return round(( pulse_end - pulse_start) * 17150,2)

dist = Distance(16, 12)