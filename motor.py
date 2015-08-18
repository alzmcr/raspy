import RPi.GPIO as GPIO
from time import time, sleep

class Motor():
    def __init__(self, name, gpio1, gpio2, gpio1_is_fw=True, use_pwm=True):
        self.name = name                # motor name
        self.gpio1 = gpio1              # gpio pin to move in one direction
        self.gpio2 = gpio2              # gpio pin to move in opposite direction
        self.gpio1_is_fw = gpio1_is_fw  # gpio1 is foward?
        self.use_pwm = use_pwm          # use PWM to control speed of motor
        GPIO.setup(gpio1, GPIO.OUT)     # setup GPIO 1
        GPIO.setup(gpio2, GPIO.OUT)     # setup GPIO 1
        if use_pwm:
            # setting PWM
            self.pwm1 = GPIO.PWM(gpio1, 50)
            self.pwm2 = GPIO.PWM(gpio2, 50)

    # stop motor
    def stop(self):
        if self.use_pwm:
            self.pwm1.stop(); self.pwm2.stop()
        else:
            GPIO.output(self.gpio1, False); GPIO.output(self.gpio2, False)

    # spin in one direction
    def spin1(self, seconds, power=100):
        if self.use_pwm:
            self.pwm1.stop(); self.pwm2.start(power)
        else:
            GPIO.output(self.gpio1, False); GPIO.output(self.gpio2, True)
        if seconds is not None: sleep(seconds); self.stop()

    # spin in opposite direction
    def spin2(self, seconds, power=100):
        if self.use_pwm:
            self.pwm1.start(power); self.pwm2.stop()
        else:
            GPIO.output(self.gpio1, True); GPIO.output(self.gpio2, False)
        if seconds is not None: sleep(seconds); self.stop()

    def fw(self, seconds=None, power=100):
        if self.use_pwm:
            if self.gpio1_is_fw: self.pwm1.start(power); self.pwm2.stop()
            else: self.pwm1.stop(); self.pwm2.start(power)
        else:
            GPIO.output(self.gpio1, self.gpio1_is_fw); GPIO.output(self.gpio2, not self.gpio1_is_fw)
        if seconds is not None: sleep(seconds); self.stop()

    def rw(self, seconds=None, power=100):
        if self.use_pwm:
            if self.gpio1_is_fw: self.pwm1.stop(); self.pwm2.start(power)
            else: self.pwm1.start(power); self.pwm2.stop()
        else:
            GPIO.output(self.gpio1, not self.gpio1_is_fw); GPIO.output(self.gpio2, self.gpio1_is_fw)
        if seconds is not None: sleep(seconds); self.stop()
        
    def power(self, seconds=None, power=100):
        # power with range between -100 (rw: 100%) and 100 (fw: 100%)
        if power > 0:
            self.fw(seconds, +power)
        else:
            self.rw(seconds, -power)

