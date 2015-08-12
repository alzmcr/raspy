import picamera
import numpy as np
import io
from scipy import misc
from datetime import datetime
from time import time, sleep

class Camera():
    def __init__(self, w=320, h=240):
        self.camera = picamera.PiCamera(resolution=(w,h))
        self.closed = self.camera.closed
        self.resolution(w, h)
        self.stream = io.BytesIO()

    def snap(self, use_video_port=True):
        if self.camera.closed:
            self.camera = picamera.PiCamera(resolution=(self.w,self.h))

        # take a snapshot
        self.camera.capture(self.stream, format='yuv', use_video_port=use_video_port)
        # save it to stream
        self.stream.truncate(self.fw*self.fh)
        self.stream.seek(0)
        # transform image
        image = np.fromstring(self.stream.getvalue(), dtype=np.uint8).reshape((self.fh, self.fw))[:self.h,:self.w]
        # reset stream
        self.stream.truncate(0)

        return image

    def savesnap(self, fname=None, use_video_port=True):
        if fname is None:
            fname = datetime.now().strftime('%Y%m%d_%H%M%S.%f.jpg')
        # save to file
        misc.imsave(fname, self.snap(use_video_port))

    def resolution(self, w, h):
        self.w, self.h = w, h
        self.fw = (w + 31) // 32 * 32
        self.fh = (h + 15) // 16 * 16
        self.camera.resolution = (w, h)

    def close(self):
        self.camera.close()
        self.closed = self.camera.closed

    def __repr__(self):
        return "Camera instance: resolution (%ix%i)" % (self.w, self.h)




