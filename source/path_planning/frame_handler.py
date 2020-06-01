import time

import numpy as np 
import cv2

from source.vision_identification import bounding_box
from source.vision_identification.video_reader import FileVideoStream
from source.vision_identification import meat
from source.model.robot import Robot
from source.model.point import Point
from source.path_planning.path_runner import PathRunner
from source.path_planning import graphing_tools
from source import global_parameters

class FrameHandler:
    def __init__(self):
        self.flip_flop = True # False = Left, True = Right 
        self.meats = []

        self.model = Robot(Point(280, 600), global_parameters.VIDEO_SCALE)
    def __repr__(self):
        pass

    def process_frame(self, frame):
        frame = bounding_box.scale(frame)
        frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        iH, _, _ = frame.shape
        data, _, _ = bounding_box.get_bbox(frame)

        if (data != 0):
            for i in range(0, len(data)):
                cX = int(data[i][1]["m10"] / data[i][1]["m00"])
                cY = int(data[i][1]["m01"] / data[i][1]["m00"])

                if iH / 6 < cY and iH / 2 > cY:
                    if flip_flop:
                        self.meats += [meat.Meat(data[i], side="Right", center=[cX, cY])]
                    else:
                        self.meats += [meat.Meat(data[i], side="Left", center=[cX, cY])]
                    self.flip_flop = not self.flip_flop

                    if len(self.meat) > 1:
                        self.find_path()

                    break # Ensures only one piece is identified 

    def find_path(self):
        ep1 = Point(625, 735, angle=90)
        ep2 = Point(250, 735, angle=90)
                
        # Profiler model creates motion profiles, it updates as fast as possible in a separate thread
        if profile_model.phase == 0:
            dist = (global_parameters.PICKUP_POINT - self.meats[0].get_center_as_point()).y

            if dist > 0:
                sp1 = self.meats[0].get_center_as_point() + Point(0, dist)
                sp2 = self.meats[1].get_center_as_point() + Point(0, dist)
                self.meats = []

                profile_model.moveMeat(sp1, sp2, ep1, ep2, dist / global_parameters.CONVEYOR_SPEED, phase_1_delay=False)
                
                # Given the start and end conditions, calculate the profile_model motor profiles
                self.run_model()
                self.gen_profiles()

    def run_model(self):
        self.model.clear_history()
        self.model.recording = True
        constants = self.model.get_current_state()

        counter = 0
        self.xs = []
        self.xs += [counter / global_parameters.FRAME_RATE]
        counter += 1
        self.xs += [counter / global_parameters.FRAME_RATE]
        counter += 1
        while self.model.update():
            self.xs += [counter / global_parameters.FRAME_RATE]
            counter += 1
        self.xs += [counter / global_parameters.FRAME_RATE]
        counter += 1
        self.xs += [counter / global_parameters.FRAME_RATE]
        counter += 1

        self.model.recording = False

    def gen_profiles(self):
        # Discrete data as derived from the model
        raw_pos_data = np.asarray(model.get_data())
        raw_vel_data = np.gradient(raw_pos_data, axis=0)

        # Integrated data. Closer representation of how robot will move 
        self.acc_data = np.gradient(raw_vel_data, axis=0)
        self.vel_data = np.asarray([integrate.simps(self.acc_data[0:i+1], axis=0).tolist() for i in range(0, len(self.acc_data))])
        self.pos_data = np.add(np.asarray([integrate.simps(self.vel_data[0:i+1], axis=0).tolist() for i in range(0, len(self.vel_data))]), constants)

    def get_results(self):
        return self.xs, self.pos_data, self.vel_data, self.acc_data