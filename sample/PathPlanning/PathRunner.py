from threading import Thread
from threading import Lock
import sys
from queue import Queue
import time

import cv2
import numpy as np
# from statsmodels.nonparametric.kernel_regression import KernelReg

from ..Model.Robot import Robot
from .. import GlobalParameters

class PathRunner:
    def __init__(self, model:Robot):
        self.stopped = False
        self.running = False
        self.model = model
        self.pos_data = np.array([[0]])

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
        counter = 0
        self.xs = []

        while self.model.update():
            self.xs += [counter / GlobalParameters.FRAME_RATE]
            counter += 1
            if self.stopped:
                return 

        if not self.stopped:
            self.model.recording = False

            # k = [KernelReg(temp[:,i], self.xs, 'c') for i in range(0, 8)]
            # y_preds = [k[i].fit(self.xs)[0] for i in range(0, 8)]

            self.pos_data = np.asarray(self.model.get_data())
            self.vel_data = np.gradient(self.pos_data, axis=0)
            self.acc_data = np.gradient(self.vel_data, axis=0)

        self.running = False 
            
    def read(self):
        if not self.running:
            return self.xs, self.pos_data, self.vel_data, self.acc_data
        else:
            with Lock():
                print("ERROR: Request for data made before results computed")
            return 