import keypad
from time import time, sleep
from imu import Imu
from datetime import datetime

def interp(x,x0,x1,y0,y1): return y0 + (y1-y0) * (float(x-x0)/(x1-x0))

class Rover():
    def __init__(self, m1, m2, jib=None, dist=None, verbose=False):
        self.m1 = m1
        self.m2 = m2
        self.imu = Imu()
        self.dist = dist
        self.jib = jib
        self.motorlog = []
        # CURRENT STATE
        self.state = 'stop'
        self.power = 0
        self.minpower = 30
        self.steerpower = 0
        self.maxsteerpower = 3
        # DEBUG
        self.verbose = verbose
        print "Hi, I'm Rover... hopefully I won't roll over!"

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
            increase = 10 if self.steerpower == 0 else 0
            self.power = min(100, max(self.minpower, self.power + increase)); self.steerpower = 0
            self._fw(seconds, power=self.power)
        else: self._fw(seconds)

    def rw(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            if self.state == 'fw': self.power = 0
            increase = 10 if self.steerpower == 0 else 0
            self.power = min(100, max(self.minpower, self.power + increase)); self.steerpower = 0
            self._rw(seconds, power=self.power)
        else: self._rw(seconds)

    def left(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            self.steerpower = max(0, min(self.maxsteerpower, self.steerpower + 1))
            self._left(seconds, steerpower=self.steerpower)
        else: self._left(seconds)

    def right(self, seconds=None):
        if m1.use_pwm and m2.use_pwm:
            self.steerpower = max(0, min(self.maxsteerpower, self.steerpower + 1))
            self._right(seconds, steerpower=self.steerpower)
        else: self._right(seconds)

    def _fw(self, seconds=None, power=100):
        self.m1.fw(power=power); self.m2.fw(power=power); self.state = 'fw'
        self.motorlog.append([time(),'fw',power,power])
        if self.verbose: print "fw: %i%% |  m1.fw: %i | m2.fw: %i" % (power,power,power)
        if seconds is not None:
            sleep(seconds); self.stop()

    def _rw(self, seconds=None, power=100):
        self.m1.rw(power=power); self.m2.rw(power=power); self.state = 'rw'
        self.motorlog.append([time(),'rw',power,power])
        if self.verbose: print "rw: %i%% | m1.rw: %i | m2.rw %i" % (power,power,power)
        if seconds is not None:
            sleep(seconds); self.stop()

    def _left(self, seconds=None, steerpower=1):
        if m1.use_pwm and m2.use_pwm:
            if self.state == 'stop': steerpower = 3; self.state = 'fw'
            if self.power < 100:
                # hard turn if speed is below 100%
                steerpower = self.maxsteerpower

            if steerpower == self.maxsteerpower:
                # HARD TURN (reverse direction motors)
                m1power = 100; m2power = 100
                if self.state == 'fw':
                    self.m1.rw(power=m1power); m1dir = 'rw'
                    self.m2.fw(power=m2power); m2dir = 'fw'
                else:
                    self.m1.fw(power=m1power); m1dir = 'fw'
                    self.m2.rw(power=m2power); m2dir = 'rw'
            else:
                # SOFTER TURN (same direction motors)
                m1power = 100 - (steerpower * 15); m2power = self.power
                if self.state == 'fw':
                    self.m1.fw(power=m1power); m1dir = 'fw'
                    self.m2.fw(power=m2power); m2dir = 'fw'
                else:
                    self.m1.rw(power=m1power); m1dir = 'rw'
                    self.m2.rw(power=m2power); m2dir = 'rw'
            if self.verbose: print "left: %i%% | m1.%s: %i | m2.%s %i" % (steerpower,m1dir,m1power,m2dir,m2power)
        else:
            self.m1.rw(power=self.power); self.m2.fw(power=self.power)
            m1power, m2power = self.power, self.power
        # log motor
        self.motorlog.append([time(),'left',m1power,m2power])
        if seconds is not None:
            sleep(seconds); self.stop()

    def _right(self, seconds=None, steerpower=1):
        if m1.use_pwm and m2.use_pwm:
            if self.state == 'stop': steerpower = 3; self.state = 'fw'
            if self.power < 100:
                # hard turn if speed is below 100%
                steerpower = self.maxsteerpower

            if steerpower == self.maxsteerpower:
                # HARD TURN (reverse direction motors)
                m1power = 100; m2power = 100
                if self.state == 'rw':
                    self.m1.rw(power=m1power); m1dir = 'rw'
                    self.m2.fw(power=m2power); m2dir = 'fw'
                else:
                    self.m1.fw(power=m1power); m1dir = 'fw'
                    self.m2.rw(power=m2power); m2dir = 'rw'
            else:
                # SOFTER TURN (same direction motors)
                m2power = 100 - (steerpower * 15); m1power = self.power
                if self.state == 'fw':
                    self.m1.fw(power=m1power); m1dir = 'fw'
                    self.m2.fw(power=m2power); m2dir = 'fw'
                else:
                    self.m1.rw(power=m1power); m1dir = 'rw'
                    self.m2.rw(power=m2power); m2dir = 'rw'
            if self.verbose: print "right: %i%% | m1.%s: %i | m2.%s %i" % (steerpower,m1dir,m1power,m2dir,m2power)
        else:
            self.m1.rw(power=self.power); self.m2.fw(power=self.power)
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
        dist = self.distance()[1]
        if dist is None: print "Distance Measurement not initialized"
        else: print "Distance: %.2fcm" % dist

    # LOGGING
    def init_log(self, seconds=3600, interval=0.010):
        self.motorlog = []; self.imu.samples = []   # reset motor logger
        self.stop()                                 # stop car
        self.imu.sampler(seconds, interval)         # start reading accelerometer

    def save_log(self, savepath=None):
        self.stop()
        acclog = self.imu.get_samples()

        import pandas as pd
        acclog = pd.DataFrame(acclog, columns=['time','pitch','roll','heading','ax','ay','az','mx','my','mz','gx','gy','gz']).set_index('time')
        carlog = pd.DataFrame(self.motorlog, columns=['time','action','m1','m2']).set_index('time')
        carlog['seq'] = range(len(carlog))
        data = pd.merge(acclog, carlog, how='outer', left_index=True, right_index=True)
        # reset data with star date
        data.index = data.index.values - data.index.values.min()

        if savepath is not None:
            if savepath == True: savepath = ''
            data.to_csv(datetime.now().strftime(savepath+'carlog_%Y%m%d_%H%M%S.csv'))

        return data

from motor import Motor
from camera import jib, s1, s2
from distance import dist

m1 = Motor('left',35,37,True)
m2 = Motor('left',38,40,True)

r = Rover(m1,m2, jib, dist, verbose=True)

