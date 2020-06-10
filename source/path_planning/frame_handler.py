import time

import numpy as np 
import cv2

from ..vision_identification import bounding_box
from ..vision_identification import meat
from ..model.robot import Robot
from ..model.point import Point
from ..global_parameters import global_parameters

class FrameHandler:
    def __init__(self):
        self.flip_flop = False # False = Left, True = Right 
        self.meats = []
        self.constants = []
        self.end_pt1 = (global_parameters['END_POINT1'] - Point(global_parameters['LOIN_WIDTH'], 0)) * global_parameters['VIDEO_SCALE']
        self.end_pt2 = (global_parameters['END_POINT2'] + Point(global_parameters['LOIN_WIDTH'], 0)) * global_parameters['VIDEO_SCALE']

        self.dt = None
        self.start = 0
        self.model = Robot(global_parameters['ROBOT_BASE_POINT'], global_parameters['VIDEO_SCALE'])
    def __repr__(self):
        return "FrameHandler Object\n\tModel:" + self.model.__repr__()

    def process_frame(self, frame, read_time, draw=False):
        start = time.time()
        self.frame = bounding_box.scale(frame)
        self.frame = cv2.copyMakeBorder(self.frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        if draw:
            cv2.imshow("Temp", self.frame)

        iH, _, _ = self.frame.shape
        data, _, _ = bounding_box.get_bbox(self.frame)

        if (data != 0):
            for i in range(0, len(data)):
                cX = int(data[i][1]["m10"] / data[i][1]["m00"])
                cY = int(data[i][1]["m01"] / data[i][1]["m00"])

                if iH / 6 < cY and iH / 2 > cY:
                    if len(self.meats) == 0: # Marks the time of the first of two meats 
                        self.start = start
                    if self.flip_flop:
                        self.meats += [meat.Meat(data[i], global_parameters['VIDEO_SCALE'], side="Right", center=[cX, cY])]
                    else:
                        self.meats += [meat.Meat(data[i], global_parameters['VIDEO_SCALE'], side="Left", center=[cX, cY])]
                    self.flip_flop = not self.flip_flop

                    if len(self.meats) > 1:
                        self.find_path(read_time)
                        if not self.model.gen_profiles(): # If path creation failed (collision, etc)
                            # self.xs = []
                            return False
                        print(self.model)
                    break # Ensures only one piece is identified 
        
        return True

    def find_path(self, read_time):
        self.dt = time.time() - self.start
        # Profiler model creates motion profiles, it updates as fast as possible in a separate thread
        if self.model.phase == 0:
            s1 = self.meats[0].get_center_as_point()
            s2 = self.meats[1].get_center_as_point() + Point(0, self.dt * global_parameters['FRAME_RATE'] * global_parameters['CONVEYOR_SPEED'] * global_parameters['VIDEO_SCALE'])

            self.model.move_meat(s1, s2, self.end_pt1, self.end_pt2, self.meats[0].width, self.meats[1].width, phase_1_delay=False)
            self.meats = []
            # Given the start and end conditions, calculate the model motor profiles
            self.model.run(read_time) 

    def get_results(self):
        if len(self.meats) == 0:
            xs, _, vels = self.model.get_data()
            return xs, vels
        else:
            return [], []