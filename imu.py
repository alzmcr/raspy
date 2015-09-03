# Inertial Measurement Unit
from berryimu import Imu as BerryImu
from time import time, sleep
from threading import Thread

class Imu(BerryImu):
    def __init__(self):
        super(Imu, self).__init__()
        self.continue_sampling = True
        self.samples = []
        self.thread = None

    def _sampler(self, seconds=None, interval=0.020, verbose=False):
        itime = time(); counter = 0
        while self.continue_sampling:
            if (time() - itime) > seconds: break
            self.samples.append(self.reading())
            counter += 1
            rtime = (counter * interval) - (time() - itime)
            rtime = rtime if rtime > 0 else 0
            sleep(rtime)

        self.continue_sampling = True
        return self.samples

    def sampler(self, seconds=None, interval=0.020, verbose=False):
        self.thread = Thread(target = self._sampler, args = (seconds, interval, verbose))
        self.thread.start()

    def stop_sampling(self):
        self.continue_sampling = False
        self.thread.join()

    def get_samples(self):
        self.stop_sampling()
        return self.samples
