from threading import Thread as worker
# from processing import process as worker
import sys
from queue import Queue
import time

import cv2

class FileVideoStream:
    '''
        This allows the program to read the video on a separate thread than
        the calculations are being done on. This increases runtime by 48%. 

        Note: If max queue size is reached this durastically slows the program
        and if 0 queue size is reached it will kill the program. Change sleep_time
        manually based on queue size either on this thread or your other thread, 
        depending on which one is the limiting factor. 
    '''
    def __init__(self, path, queueSize=128):
        self.stream = cv2.VideoCapture(path)
        self.stopped = False
        self.Q = Queue(maxsize=queueSize)
        self.sleep_time = 0.001
        self.running = False

    def start(self):
        self.t = worker(target=self.update, args=())
        self.t.daemon = True
        self.t.start()
        return self

    def stop(self):
        self.stopped = True
        self.running = False

    def update(self):
        self.running = True
        while True:
            time.sleep(self.sleep_time)
            if self.stopped:
                return 
            
            if not self.Q.full():
                (grabbed, frame) = self.stream.read()

                if not grabbed:
                    self.stop()
                    return 

                self.Q.put(frame)

    def read(self):
        return self.Q.get()

    def more(self):
        return self.Q.qsize() > 0