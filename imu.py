# Inertial Measurement Unit
from pyberryimu.client import BerryIMUClient
from time import time, sleep
from threading import Thread

class Imu():
    def __init__(self):
        self.c = BerryIMUClient(bus=1)
        self.continue_sampling = True
        self.samples = []
        self.thread = None

    def acc(self): return self.c.read_accelerometer()
    def gyro(self): return self.c.read_gyroscope()
    def magnet(self): return self.c.read_magnetometer()
    def pressure(self): return self.c.read_pressure()
    def temperature(self): return self.c.read_temperature()

    def read(self):
        return [time()] + list(self.acc()) + list(self.gyro()) + list(self.magnet())

    def _sampler(self, seconds=None, interval=0.025, verbose=False):
        itime = time(); counter = 0
        while self.continue_sampling:
            if (time() - itime) > seconds: break
            self.samples.append(self.read())
            counter += 1
            rtime = (counter * interval) - (time() - itime)
            rtime = rtime if rtime > 0 else 0
            sleep(rtime)

        self.continue_sampling = True
        return self.samples

    def sampler(self, seconds=None, interval=0.025, verbose=False):
        self.thread = Thread(target = self._sampler, args = (seconds, interval, verbose))
        self.thread.start()

    def stop_sampling(self):
        self.continue_sampling = False
        self.thread.join()

    def get_samples(self):
        self.stop_sampling()
        return self.samples
