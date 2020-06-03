import time

import numpy as np 
import cv2
from scipy import integrate

from source.vision_identification import bounding_box
from source.vision_identification import meat
from source.model.robot import Robot
from source.model.point import Point
# from source.data_send_receive import data_io
from source import global_parameters

class FrameHandler:
    def __init__(self):
        self.flip_flop = False # False = Left, True = Right 
        self.meats = []
        self.acc_data = []
        self.vel_data = []
        self.pos_data = []
        self.xs = []
        self.constants = []
        self.end_point_1 = global_parameters.END_POINT_1 - Point(global_parameters.LOIN_WIDTH * global_parameters.VIDEO_SCALE, 0)
        self.end_point_2 = global_parameters.END_POINT_2 + Point(global_parameters.LOIN_WIDTH * global_parameters.VIDEO_SCALE, 0)

        self.dt = None
        self.start = 0
        self.model = Robot(global_parameters.ROBOT_BASE_POINT, global_parameters.VIDEO_SCALE)
    def __repr__(self):
        return "FrameHandler Object\n\tModel:" + self.model.__repr__()

    def process_frame(self, frame, read_time, draw=False):
        start = time.time()
        if len(self.meats) == 0:
            self.start = start
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
                    if self.flip_flop:
                        self.meats += [meat.Meat(data[i], side="Right", center=[cX, cY])]
                    else:
                        self.meats += [meat.Meat(data[i], side="Left", center=[cX, cY])]
                    self.flip_flop = not self.flip_flop

                    if len(self.meats) > 1:
                        self.find_path(read_time)
                        if not self.gen_profiles(): # If path creation failed (collision, etc)
                            # self.xs = []
                            return False
                    else:
                        self.xs = []
                        self.vel_data = []

                    break # Ensures only one piece is identified 
        
        return True

    def find_path(self, read_time):
        self.dt = time.time() - self.start
        # Profiler model creates motion profiles, it updates as fast as possible in a separate thread
        if self.model.phase == 0:
            self.dist = (global_parameters.PICKUP_POINT - self.meats[0].get_center_as_point()).y
            self.start_point_1 = self.meats[1].get_center_as_point() + Point(0, self.dist)
            self.start_point_2 = self.meats[0].get_center_as_point() + Point(0, self.dist + self.dt * global_parameters.FRAME_RATE * global_parameters.CONVEYOR_SPEED)

            if self.dist > 0:
                self.meats = []
                self.model.moveMeat(self.start_point_1, self.start_point_2, self.end_point_1, self.end_point_2, self.dist / global_parameters.CONVEYOR_SPEED, phase_1_delay=False)
                
                # Given the start and end conditions, calculate the model motor profiles
                self.run_model(read_time)       

    def run_model(self, read_time):
        self.model.clear_history()
        self.model.recording = True
        # self.constants = self.model.get_current_state()

        counter = 0
        self.xs = []
        self.xs += [read_time - 2 / global_parameters.FRAME_RATE]
        self.xs += [read_time - 1 / global_parameters.FRAME_RATE]
        while self.model.update():
            self.xs += [read_time + counter / global_parameters.FRAME_RATE]
            counter += 1
        self.xs += [read_time + counter / global_parameters.FRAME_RATE]
        counter += 1
        self.xs += [read_time + counter / global_parameters.FRAME_RATE]
        counter += 1

        c = (self.dist / global_parameters.CONVEYOR_SPEED - self.model.phase_1_counter) / global_parameters.FRAME_RATE

        print(self.xs[0])
        self.xs = [self.xs[i] + c for i in range(0, len(self.xs))]
        print(self.xs[0])
        print(time.time(), "\n")

        self.model.recording = False

    def gen_profiles(self):
        # Discrete data as derived from the model
        raw_pos_data = np.asarray(self.model.get_data())
        if len(raw_pos_data) == 0:
            return False
        raw_vel_data = np.gradient(raw_pos_data, axis=0)
        
        # Integrated data. Closer representation of how robot will move 
        self.acc_data = np.gradient(raw_vel_data, axis=0)
        self.vel_data = np.asarray([integrate.simps(self.acc_data[0:i+1], axis=0).tolist() for i in range(0, len(self.acc_data))])
        # self.pos_data = np.add(np.asarray([integrate.simps(self.vel_data[0:i+1], axis=0).tolist() for i in range(0, len(self.vel_data))]), self.constants)

        return True

    def get_results(self):
        return self.xs, self.vel_data

    # def package_data(self):
    #     # vel_data is a list of velocity values for each actuator 
    #     full_data = ""
    #     for i in range(0, len(self.vel_data)):
    #         for j in range(0, len(self.vel_data[i])):
    #             # print(f"{str(round(vel_data[i][j], 5)):<{DATA_CHUNK_SIZE}}")
    #             full_data += f"{str(round(self.vel_data[i][j], 5)):<{global_parameters.DATA_CHUNK_SIZE}}"

    #     encoded_data = full_data.encode('utf-8')

    #     # for i in range(0, len(t), DATA_CHUNK_SIZE):
    #     #     print("T",i,t[i:i+DATA_CHUNK_SIZE])

    #     return encoded_data