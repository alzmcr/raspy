import smbus
import numpy as np
from time import time, sleep
from threading import Thread

class Accel():
    def __init__(self):
        self.b = smbus.SMBus(1)
        self.setUp()
        self.continue_sampling = True
        self.samples = []
        self.thread = None

    def setUp(self):
        self.b.write_byte_data(0x1D,0x16,0x55)  # Setup the Mode
        self.b.write_byte_data(0x1D,0x10,0)     # Calibrate
        self.b.write_byte_data(0x1D,0x11,0)     # Calibrate
        self.b.write_byte_data(0x1D,0x12,0)     # Calibrate
        self.b.write_byte_data(0x1D,0x13,0)     # Calibrate
        self.b.write_byte_data(0x1D,0x14,0)     # Calibrate
        self.b.write_byte_data(0x1D,0x15,0)     # Calibrate

    def getValueX(self):
        try: return self.b.read_byte_data(0x1D,0x06)
        except: return np.nan

    def getValueY(self):
        try: return self.b.read_byte_data(0x1D,0x07)
        except: return np.nan

    def getValueZ(self):
        try: return self.b.read_byte_data(0x1D,0x08)
        except: return np.nan

    def getXYZ(self):
        return time(), self.getValueX(), self.getValueY(), self.getValueZ()

    def _sampler(self, seconds=5, interval=0.010, verbose=False):
        itime = time(); counter = 0
        while self.continue_sampling:
            if (time() - itime) > seconds: break
            self.samples.append(self.getXYZ())
            counter += 1
            rtime = (counter * interval) - (time() - itime)
            rtime = rtime if rtime > 0 else 0
            sleep(rtime)

        self.continue_sampling = True
        return self.samples

    def sampler(self, seconds=5, interval=0.010, verbose=False):
        self.thread = Thread(target = self._sampler, args = (seconds, interval, verbose))
        self.thread.start()

    def stop_sampling(self):
        self.continue_sampling = False
        self.thread.join()

    def get_samples(self):
        self.stop_sampling()
        return self.samples

if __name__ == "__main__":
    acc = Accel()
    acc.sampler(seconds = 30, interval=0.250)