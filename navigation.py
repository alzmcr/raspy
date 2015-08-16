import keypad
import RPi.GPIO as GPIO
from time import time, sleep
from accelerometer import Accel
from datetime import datetime

if GPIO.getmode() == -1: GPIO.setmode(GPIO.BOARD)

def interp(x,x0,x1,y0,y1): return y0 + (y1-y0) * (float(x-x0)/(x1-x0))

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

class Rover():
    def __init__(self, m1, m2, jib=None, dist=None, verbose=False):
        self.m1 = m1
        self.m2 = m2
        self.acc = Accel()
        self.dist = dist
        self.jib = jib
        self.motorlog = []
        # CURRENT STATE
        self.state = 'stop'
        self.power = 0
        self.steerpower = 0
        # DEBUG
        self.verbose = verbose

    def keycontrol(self):
        mapping = {
            # KEY BINDINGS: key to function (with default value)
            # ROVER KEYS
            'w': 'fw', 's': 'rw', 'a': 'left', 'd': 'right',
            ' ': 'stop', 'r': 'init_log', 't': 'save_log',
            # JIB KEYS
            'i': 'jib.moveup', 'j': 'jib.moveleft',
            'k': 'jib.movedw', 'l': 'jib.moveright',
            # MEASURE DISTANCE
            'm': 'print_distance'
        }
        print "ROVER KEYPAD: initialized"
        keypad.keypad(self, mapping)
        print "ROVER KEYPAD: terminated"

    # DIRECTION
    def stop(self):
        self.m1.stop(); self.m2.stop(); self.state = 'stop'; self.power = 0
        self.motorlog.append([time(),'stop',0,0])
        if self.verbose: print "stop | m1: %i | m2: %i" % (0,0)

    def fw(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            if self.state == 'rw': self.power = 0
            self.power = min(100, max(30, self.power + 10)); self.steerpower = 0
            self._fw(seconds, power=self.power)
        else: self._fw(seconds)

    def rw(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            if self.state == 'fw': self.power = 0
            self.power = min(100, max(30, self.power + 10)); self.steerpower = 0
            self._rw(seconds, power=self.power)
        else: self._fw(seconds)

    def left(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            self.steerpower = min(100, max(30, self.steerpower + 10))
            self._left(seconds, steerpower=self.steerpower)
        else: self._left(seconds)

    def right(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            self.steerpower = min(100, max(30, self.steerpower + 10))
            self._right(seconds, steerpower=self.steerpower)
        else: self._right(seconds)

    def _fw(self, seconds=None, power=100):
        self.m1.fw(power=power); self.m2.fw(power=power); self.state = 'fw'
        self.motorlog.append([time(),'fw',power,power])
        if self.verbose: print "fw | m1.fw: %i | m2.fw: %i" % (power,power)
        if seconds is not None:
            sleep(seconds); self.stop()

    def _rw(self, seconds=None, power=100):
        self.m1.rw(power=power); self.m2.rw(power=power); self.state = 'rw'
        self.motorlog.append([time(),'rw',power,power])
        if self.verbose: print "rw | m1.rw: %i | m2.rw %i" % (power,power)
        if seconds is not None:
            sleep(seconds); self.stop()

    def _left(self, seconds=None, steerpower=100):
        if m1.use_pwm and m2.use_pwm:
            # if the rover is not moving, rotating power is forced to 100
            if self.state == 'stop': steerpower = 100; self.power = 100; self.state ='fw'
            m2power = self.power
            self.m2.rw(power=m2power) if self.state == 'rw' else self.m2.fw(power=m2power)
            if steerpower >=50:
                # STRONG TURN (inverted direction on motors)
                m1power = ((steerpower-50)*2/100.)*self.power
                #m1power = interp(steerpower, 0, 100, 30, 100)
                self.m1.rw(power=m1power) if self.state == 'fw' else self.m1.fw(power=m1power)
                #self.m2.fw(power=(power-50)*2) if self.state == 'rw' else self.m2.rw(power=(power-50)*2)
            else:
                # LIGHT TURN  (same direction, but slower motors)
                m1power = ((50-steerpower)*2/100.)*self.power
                self.m1.fw(power=m1power) if self.state == 'fw' else self.m1.rw(power=m1power)
                #self.m2.rw(power=(50-power)*2) if self.state == 'rw' else self.m2.fw(power=(50-power)*2)
        else:
            self.m1.rw(power=self.power); self.m2.fw(power=self.power)
            m1power, m2power = self.power, self.power
        # log motor
        self.motorlog.append([time(),'left',m1power,m2power])
        if seconds is not None:
            sleep(seconds); self.stop()

    def _right(self, seconds=None, steerpower=100):
        if m1.use_pwm and m2.use_pwm:
            # if the rover is not moving, rotating power is forced to 100
            if self.state == 'stop': steerpower = 100; self.power = 100; self.state ='fw'
            m1power = self.power
            self.m1.fw(power=m1power) if self.state == 'fw' else self.m1.rw(power=m1power)
            if steerpower >=50:
                # STRONG TURN (inverted direction on motors)
                m2power = ((steerpower-50)*2/100.)*self.power
                self.m2.fw(power=m2power) if self.state == 'rw' else self.m2.rw(power=m2power)
                #self.m2.rw(power=(power-50)*2) if self.state == 'fw' else self.m2.fw(power=(power-50)*2)
            else:
                # LIGHT TURN  (same direction, but slower motors)
                m2power = ((50-steerpower)*2/100.)*self.power
                self.m2.fw(power=m2power) if self.state == 'fw' else self.m2.rw(power=m2power)
                #self.m2.fw(power=(50-power)*2) if self.state == 'fw' else self.m2.rw(power=(50-power)*2)
        else:
            self.m1.fw(power=self.power); self.m2.rw(power=self.power)
            m1power, m2power = self.power, self.power
        # log motor
        self.motorlog.append([time(),'right',m1power,m2power])

        if seconds is not None:
            sleep(seconds); self.stop()

    def distance(self):
        if self.dist is not None:
            return self.dist.measure()
        else: return None

    def print_distance(self):
        dist = self.measure()
        if dist is None: print "Distance Measurement not initialized"
        else: print "Distance: %.2fcm" % dist

    # LOGGING
    def init_log(self, seconds=3600, interval=0.010):
        self.motorlog = []; self.acc.samples = []   # reset motor logger
        self.stop()                                 # stop car
        self.acc.sampler(seconds, interval)         # start reading accelerometer

    def save_log(self, savepath=None):
        self.stop()
        acclog = self.acc.get_samples()

        import pandas as pd
        acclog = pd.DataFrame(acclog, columns=['time','x','y','z']).set_index('time')
        carlog = pd.DataFrame(self.motorlog, columns=['time','action']).set_index('time')
        carlog['seq'] = range(len(carlog))
        data = pd.merge(acclog, carlog, how='outer', left_index=True, right_index=True)
        # reset data with star date
        data.index = data.index.values - data.index.values.min()

        if savepath is not None:
            if savepath == True: savepath = ''
            data.to_csv(datetime.now().strftime(savepath+'carlog_%Y%m%d_%H%M%S.csv'))

        return data

from camera import jib, s1, s2
from distance import dist

m1 = Motor('left',35,37,True)
m2 = Motor('left',38,40,True)

r = Rover(m1,m2, jib, dist)

