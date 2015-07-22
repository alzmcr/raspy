import camera
import numpy as np
from time import sleep, time

class NightWatch():
    def __init__(self, w=320, h=240):
        self.camera = camera.Camera(w=w,h=h)
        self.max_diff = 255 * (self.camera.w * self.camera.h)
        self.tollerance = 0.05
        self.register_framerate = 5

    def check_movement(self, snap1, snap2):
        diff = np.abs((np.array(snap1,dtype=np.int16) - snap2)).sum()
        change_perc = 1. * diff / self.max_diff
        return change_perc

    def vigilate(self, seconds=30, interval=1):
        print "NightWatch: initialized"
        start_time = time(); previous_snap = self.camera.snap()
        while True:
            # wait for the next cycle
            sleep(interval)

            if (time() - start_time) > seconds:
                print "NightWatch: terminated"
                break

            current_snap = self.camera.snap()
            if self.check_movement(current_snap, previous_snap) > self.tollerance:
                print "WHITE WALKER COMING!!!!"
                for _ in range(int(1* self.register_framerate / interval)):
                    self.camera.savesnap()


            previous_snap = current_snap


    def close(self):
        self.camera.close()

