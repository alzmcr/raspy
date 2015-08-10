import camera
import numpy as np
import multiprocessing
from time import sleep, time
from scipy import misc
from datetime import datetime


class NightWatch():
    def __init__(self, w=320, h=240):
        self.camera = camera.Camera(w=w,h=h)
        self.max_diff = 255 * (self.camera.w * self.camera.h)
        self.tollerance = 0.05
        self.record_framerate = 5

    def check_movement(self, snap1, snap2):
        diff = np.abs((np.array(snap1,dtype=np.int16) - snap2)).sum()
        change_perc = 1. * diff / self.max_diff
        return change_perc

    def vigilate(self, seconds=30, interval=1):
        print "NightWatch: initialized"
        start_time = time(); previous_snap = self.camera.snap(); recording = False
        while True:
            # wait for the next cycle
            sleep(0 if recording else interval); cycle_start_time = time()

            if (time() - start_time) > seconds:
                print "NightWatch: terminated"
                break

            current_snap = self.camera.snap()
            if self.check_movement(current_snap, previous_snap) > self.tollerance:
                recording = True
                print "WHITE WALKER COMING!!!!"
                while (time() - cycle_start_time) < interval:
                    self.savesnap(current_snap)                     # save current snap
                    sleep(1.* interval / self.record_framerate)     # normalize to current frame rate
                    current_snap = self.camera.snap()               # take new snap to record
            else:
                recording = False

            previous_snap = current_snap

    def savesnap(self, snap, path='recording', fname=None):
        if fname is None:
            fname = datetime.now().strftime('%Y%m%d_%H%M%S.%f.jpg')
        # save to file
        misc.imsave(path+'/'+fname, snap)




    def close(self):
        self.camera.close()

