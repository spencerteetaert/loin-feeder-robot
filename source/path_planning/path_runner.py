from threading import Thread as worker
# from processing import process as worker
from threading import Lock
import sys
from queue import Queue
import time

import cv2
import numpy as np
from scipy import integrate

from ..model.robot import Robot
from ..global_parameters import global_parameters

class PathRunner:
    ''' Class that generates full motion profiles for the robot given start and end points. '''
    def __init__(self, model:Robot):
        self.stopped = False
        self.running = False
        self.model = model
        self.raw_pos_data = np.array([[0]])
        self.constants = []

    def start(self):
        self.t = worker(target=self.run, args=([]))
        self.t.daemon = True
        self.t.start()
        return self

    def stop(self):
        self.stopped = True

    def run(self):
        self.running = True
        start = time.time()
        self.model.clear_history()
        self.model.recording = True
        self.constants = self.model.get_current_state()

        counter = 0
        self.xs = []
        self.xs += [counter / global_parameters['FRAME_RATE']]
        counter += 1
        self.xs += [counter / global_parameters['FRAME_RATE']]
        counter += 1
        while self.model.update():
            self.xs += [counter / global_parameters['FRAME_RATE']]
            counter += 1
            if self.stopped:
                return 
        self.xs += [counter / global_parameters['FRAME_RATE']]
        counter += 1
        self.xs += [counter / global_parameters['FRAME_RATE']]
        counter += 1

        if not self.stopped:
            self.model.recording = False

            # Discrete data as derived from the model
            _, self.raw_pos_data, _ = self.model.get_data()
            self.raw_vel_data = np.gradient(np.asarray(self.raw_pos_data), axis=0)
            self.raw_acc_data = np.gradient(self.raw_vel_data, axis=0)

            # Integrated data. This reflects how the robot will actually move 
            self.int_vel_data = np.asarray([integrate.simps(self.raw_acc_data[0:i+1], axis=0).tolist() for i in range(0, len(self.raw_acc_data))])
            self.int_pos_data = np.add(np.asarray([integrate.simps(self.int_vel_data[0:i+1], axis=0).tolist() for i in range(0, len(self.int_vel_data))]), self.constants)

        self.model.gen_profiles()

        with Lock():
            print(time.time() - start)
        self.running = False      
            
    def read(self):
        if not self.running:
            return self.xs, self.int_pos_data, self.int_vel_data
        else:
            with Lock():
                print("ERROR: Request for data made before results computed")
            return 