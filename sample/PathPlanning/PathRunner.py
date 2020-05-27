from threading import Thread
from threading import Lock
import sys
from queue import Queue
import time

import cv2
import numpy as np
from scipy import integrate

from ..Model.Robot import Robot
from .. import GlobalParameters

class PathRunner:
    def __init__(self, model:Robot):
        self.stopped = False
        self.running = False
        self.model = model
        self.raw_pos_data = np.array([[0]])
        self.constants = []

    def start(self):
        self.t = Thread(target=self.run, args=([]))
        self.t.daemon = True
        self.t.start()
        return self

    def stop(self):
        self.stopped = True

    def run(self):
        self.running = True
        self.model.clear_history()
        self.model.recording = True
        counter = 0
        self.xs = []
        self.xs += [counter]
        self.constants = self.model.get_current_state()

        # print("1")
        while self.model.update():
            self.xs += [counter / GlobalParameters.FRAME_RATE]
            counter += 1
            if self.stopped:
                return 

        # print("2")
        if not self.stopped:
            self.model.recording = False

            self.raw_pos_data = np.asarray(self.model.get_data())
            self.raw_vel_data = np.gradient(self.raw_pos_data, axis=0)
            self.raw_acc_data = np.gradient(self.raw_vel_data, axis=0)

            temp = np.asarray([integrate.simps(self.raw_acc_data[0:i+2], axis=0).tolist() for i in range(0, len(self.raw_acc_data))])
            self.int_pos_data = np.add(np.asarray([integrate.simps(temp[0:i+2], axis=0).tolist() for i in range(0, len(temp))]), self.constants)

        self.running = False      
            
    def read(self):
        if not self.running:
            return self.xs, self.raw_pos_data, self.int_pos_data
        else:
            with Lock():
                print("ERROR: Request for data made before results computed")
            return 