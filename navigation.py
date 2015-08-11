import RPi.GPIO as GPIO
from time import time, sleep
from accelerometer import Accel
from datetime import datetime

GPIO.setmode(GPIO.BOARD)

class Motor():
    def __init__(self, name, gpio1, gpio2, gpio1_is_fw=True):
        self.name = name                # motor name
        self.gpio1 = gpio1              # gpio pin to move in one direction
        self.gpio2 = gpio2              # gpio pin to move in opposite direction
        self.gpio1_is_fw = gpio1_is_fw  # gpio1 is foward?
        GPIO.setup(gpio1, GPIO.OUT)     # setup GPIO 1
        GPIO.setup(gpio2, GPIO.OUT)     # setup GPIO 1

    # stop motor
    def stop(self):
        GPIO.output(self.gpio1, False); GPIO.output(self.gpio2, False)

    # spin in one direction
    def spin1(self, seconds):
        GPIO.output(self.gpio1, False); GPIO.output(self.gpio2, True)
        if seconds is not None: sleep(seconds); self.stop()

    # spin in opposite direction
    def spin2(self, seconds):
        GPIO.output(self.gpio1, True); GPIO.output(self.gpio2, False)
        if seconds is not None: sleep(seconds); self.stop()

    def fw(self, seconds=None):
        GPIO.output(self.gpio1, self.gpio1_is_fw); GPIO.output(self.gpio2, not self.gpio1_is_fw)
        if seconds is not None: sleep(seconds); self.stop()

    def rw(self, seconds=None):
        GPIO.output(self.gpio1, not self.gpio1_is_fw); GPIO.output(self.gpio2, self.gpio1_is_fw)
        if seconds is not None: sleep(seconds); self.stop()


class Rover():
    def __init__(self, m1, m2):
        self.m1 = m1
        self.m2 = m2
        self.acc = Accel()
        self.motorlog = []

    def stop(self):
        self.m1.stop(); self.m2.stop()
        self.motorlog.append([time(),'stop'])

    def fw(self, seconds=None):
        self.m1.fw(); self.m2.fw()
        self.motorlog.append([time(),'fw'])
        if seconds is not None:
            sleep(seconds); self.stop()

    def rw(self, seconds=None):
        self.m1.rw(); self.m2.rw()
        self.motorlog.append([time(),'rw'])
        if seconds is not None:
            sleep(seconds); self.stop()

    def left(self, seconds=None, motor=None):
        if motor is None: self.m1.rw(); self.m2.fw()
        elif motor == 1: self.m1.rw()
        elif motor == 2: self.m2.fw()
        else: raise Exception('Wrong motor specified: %s' %motor)
        self.motorlog.append([time(),'left'])
        if seconds is not None:
            sleep(seconds); self.stop()

    def right(self, seconds=None, motor=None):
        if motor is None: self.m1.fw(); self.m2.rw()
        elif motor == 1: self.m1.fw()
        elif motor == 2: self.m2.rw()
        else: raise Exception('Wrong motor specified: %s' %motor)
        self.motorlog.append([time(),'right'])
        if seconds is not None:
            sleep(seconds); self.stop()

    # LOGGING
    def init_log(self, seconds=60, interval=0.010):
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



m1 = Motor('left',35,37,False)
m2 = Motor('left',38,40,True)

r = Rover(m1,m2)


if __name__ == '__main__':
    r.init_log()
    sleep(1)
    r.left(1.25); sleep(2.5)     # turn left for 1.25 sec
    r.right(1.25); sleep(2.5)    # turn right for 1.25 sec
    r.fw(3); sleep(2.5)
    r.right(1.25*4); sleep(2.5)    # turn right for 1.25*4 sec
    r.left(1.25*4);  sleep(2.5)    # turn right for 1.25*4 sec
    r.rw(3);
    r.save_log()
