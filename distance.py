import numpy as np
import RPi.GPIO as GPIO
from threading import Thread
from time import time, sleep
import signal

def terminator(*args): pass

if GPIO.getmode() == -1: GPIO.setmode(GPIO.BOARD)

class Distance():
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        GPIO.setup(trig, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)
        # sampler
        self.continue_sampling = True
        self.samples = []
        self.thread = None
        # setting alarm and timeout: 500 cm maximum measure (30ms)
        self.timeout = 500. / 17014
        signal.signal(signal.SIGALRM, terminator)

    def _measure(self):
        # this is the main measure function, it has a timeout in case we run into a hiccups
        signal.setitimer(signal.ITIMER_REAL, self.timeout)
        GPIO.output(self.trig, True); sleep(0.00001); GPIO.output(self.trig, False)
        GPIO.wait_for_edge(self.echo, GPIO.BOTH); pulse_start = time()
        GPIO.wait_for_edge(self.echo, GPIO.BOTH); pulse_end = time()
        # remove timer - we've got results before the timeout time
        signal.setitimer(signal.ITIMER_REAL, 0)
        return round(( pulse_end - pulse_start) * 17150,2)

    def measure(self, times=3):
        # measure
        distances = []
        for _ in range(times):
            try:
                distances.append(self._measure())
            except:
                distances.append(np.nan)
        return time(), np.mean(distances)

    def _sampler(self, seconds=None, interval=0.100, verbose=False):
        itime = time(); counter = 0
        while self.continue_sampling:
            if (time() - itime) > seconds: break
            self.samples.append(self.measure())
            counter += 1
            rtime = (counter * interval) - (time() - itime)
            rtime = rtime if rtime > 0 else 0
            sleep(rtime)

        self.continue_sampling = True
        return self.samples

    def sampler(self, seconds=None, interval=0.100, verbose=False):
        self.thread = Thread(target = self._sampler, args = (seconds, interval, verbose))
        self.thread.start()

    def stop_sampling(self):
        self.continue_sampling = False
        self.thread.join()

    def get_samples(self):
        self.stop_sampling()
        return self.samples


dist = Distance(16, 12)