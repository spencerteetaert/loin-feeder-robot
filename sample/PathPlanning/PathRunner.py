from threading import Thread
from threading import Lock
import sys
from queue import Queue
import time

import cv2
import numpy as np

from ..Model.Robot import Robot

class PathRunner:
    def __init__(self, model):
        self.stopped = False
        self.running = False
        self.model = model
        self.data = np.array([[0]])

    def start(self):
        self.t = Thread(target=self.run, args=())
        self.t.daemon = True
        self.t.start()
        return self

    def stop(self):
        self.stopped = True

    def run(self):
        self.running = True
        self.model.clear_history()
        self.model.recording = True

        while self.model.update():
            if self.stopped:
                return 

        self.model.recording = False
        self.data = np.asarray(self.model.get_data())

        with Lock():
            print("Profile generated.")
        self.running = False 
            
    def read(self):
        if not self.running:
            return self.data
        else:
            return "ERROR: Request for data made before results computed"