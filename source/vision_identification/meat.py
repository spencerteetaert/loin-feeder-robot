import math

import numpy as np
import cv2

from ..model.point import Point 
from ..global_parameters import global_parameters
from .. import vector_tools

font = cv2.FONT_HERSHEY_SIMPLEX

class Meat():
    def __init__(self, data, conveyor_speed=global_parameters['CONVEYOR_SPEED'] * global_parameters['RUNTIME_FACTOR'], side="Left", center=(0,0)):
        self.conveyor_speed = conveyor_speed
        self.side = side
        self.bbox = data[0]
        self.center = center
        self.width = 0

        if (self.bbox == []):
            print("ERR: Meat object created with empty bbox.")
        else:
            self.gen_significant_lines()

    def __repr__(self):
        t1 = self.side + " piece\n"
        t2 = "Velocity: " + str(self.conveyor_speed) + "px/frame\n"
        # t3 = repr(self.bbox) + "\n"
        return t1 + t2 #+ t3

    def step(self):
        '''
        Tranlsates every stored point by the conveyor speed
        '''
        step_vec = np.array([0, self.conveyor_speed])
        # print(step_vec)
        self.bbox = self.bbox + step_vec
        self.loin_line = self.loin_line + step_vec
        # self.shoulder_line = self.shoulder_line + step_vec
        # self.ham_line = self.ham_line + step_vec
        # self.belly_line = self.belly_line + step_vec
        self.cut_line = self.cut_line + step_vec
        self.center = self.center + step_vec

        # self.lines = [self.loin_line, self.shoulder_line, self.ham_line, self.belly_line, self.cut_line]

    def gen_significant_lines(self):

        # One will be short, one medium, one long
        dist1 = (self.bbox[1] - self.bbox[0])[0]**2 + (self.bbox[1] - self.bbox[0])[1]**2
        dist2 = (self.bbox[2] - self.bbox[0])[0]**2 + (self.bbox[2] - self.bbox[0])[1]**2
        dist3 = (self.bbox[3] - self.bbox[0])[0]**2 + (self.bbox[3] - self.bbox[0])[1]**2
        max_distance = max(dist1, dist2, dist3)
        min_distance = min(dist1, dist2, dist3)
        self.width = min_distance ** 0.5

        if max_distance == dist1:
            if min_distance == dist2:
                long_line_indeces = [[1, 2], [0, 3]]
                # short_line_indeces = [[0, 2], [1, 3]]
            else:
                long_line_indeces = [[1, 3], [0, 2]]
                # short_line_indeces = [[0, 3], [1, 2]]
        elif max_distance == dist2:
            if min_distance == dist1:
                long_line_indeces = [[1, 2], [0, 3]]
                # short_line_indeces = [[0, 1], [2, 3]]
            else:
                long_line_indeces = [[2, 3], [0, 1]]
                # short_line_indeces = [[0, 3], [1, 2]]
        else:
            if min_distance == dist1:
                long_line_indeces = [[1, 3], [0, 2]]
                # short_line_indeces = [[0, 1], [2, 3]]
            else:
                long_line_indeces = [[0, 1], [2, 3]]
                # short_line_indeces = [[0, 2], [1, 3]]

        # short_avg_x_0 = (self.bbox[short_line_indeces[0][0]][0] + self.bbox[short_line_indeces[0][1]][0])/2
        # short_avg_x_1 = (self.bbox[short_line_indeces[1][0]][0] + self.bbox[short_line_indeces[1][1]][0])/2

        # if short_avg_x_0 > short_avg_x_1:
        #     self.ham_line = [self.bbox[short_line_indeces[0][0]], self.bbox[short_line_indeces[0][1]]]
        #     self.shoulder_line = [self.bbox[short_line_indeces[1][0]], self.bbox[short_line_indeces[1][1]]]
        # else:
        #     self.shoulder_line = [self.bbox[short_line_indeces[0][0]], self.bbox[short_line_indeces[0][1]]]
        #     self.ham_line = [self.bbox[short_line_indeces[1][0]], self.bbox[short_line_indeces[1][1]]]

        long_avg_y_0 = (self.bbox[long_line_indeces[0][0]][1] + self.bbox[long_line_indeces[0][1]][1])/2
        long_avg_y_1 = (self.bbox[long_line_indeces[1][0]][1] + self.bbox[long_line_indeces[1][1]][1])/2
    
        if long_avg_y_0 > long_avg_y_1:
            if self.side == "Left":
                # self.belly_line = [self.bbox[long_line_indeces[1][0]], self.bbox[long_line_indeces[1][1]]]
                self.loin_line = [self.bbox[long_line_indeces[0][0]], self.bbox[long_line_indeces[0][1]]]
            else:
                # self.belly_line = [self.bbox[long_line_indeces[0][0]], self.bbox[long_line_indeces[0][1]]]
                self.loin_line = [self.bbox[long_line_indeces[1][0]], self.bbox[long_line_indeces[1][1]]]
        else:
            if self.side == "Left":
                # self.belly_line = [self.bbox[long_line_indeces[0][0]], self.bbox[long_line_indeces[0][1]]]
                self.loin_line = [self.bbox[long_line_indeces[1][0]], self.bbox[long_line_indeces[1][1]]]
            else:
                # self.belly_line = [self.bbox[long_line_indeces[1][0]], self.bbox[long_line_indeces[1][1]]]
                self.loin_line = [self.bbox[long_line_indeces[0][0]], self.bbox[long_line_indeces[0][1]]]

        x = vector_tools.get_normal_unit(self.loin_line[0], self.loin_line[1])
        
        if self.side == "Left":
            x *= -1

        dir_vect = x * global_parameters['LOIN_WIDTH'] * global_parameters['VIDEO_SCALE']
        self.cut_line = self.loin_line + dir_vect

        # Return 
        # self.lines = [self.loin_line, self.shoulder_line, self.ham_line, self.belly_line, self.cut_line]

    def get_center_as_point(self):
        dy = self.loin_line[1][1] - self.loin_line[0][1]
        dx = self.loin_line[1][0] - self.loin_line[0][0]

        return Point(self.center[0], self.center[1], angle=Point(dx, dy).vector_angle()) 

    def get_lines(self):
        return self.lines
    def get_bbox(self):
        return self.bbox
    def get_side(self):
        return self.side

    def draw(self, img, color=(0, 255, 0)):
        # try:
        #Draws convex hull
        self.get_center_as_point().draw(img, color=(255, 255, 255))
        cv2.drawContours(img, [self.bbox.astype(int)], 0, color, 2)
        y0, dy = int(self.center[1] - 50), 18
        for i, line in enumerate(self.__repr__().split('\n')):
            y = y0 + i*dy
            cv2.putText(img, line, (int(self.center[0] + 120), y), font, 0.7, (255, 255, 0))

        #Draws identified lines of interest
        # line_pts = self.get_lines()

        #Red - Loin
        # cv2.line(img, (int(round(line_pts[0][0][0])),int(round(line_pts[0][0][1]))), (int(round(line_pts[0][1][0])),int(round(line_pts[0][1][1]))), (0, 0, 255), thickness=2)
        #Yellow - Shoulder
        # cv2.line(img, (int(round(line_pts[1][0][0])),int(round(line_pts[1][0][1]))), (int(round(line_pts[1][1][0])),int(round(line_pts[1][1][1]))), (0, 255, 255), thickness=2)
        #Blue - Ham
        # cv2.line(img, (int(round(line_pts[2][0][0])),int(round(line_pts[2][0][1]))), (int(round(line_pts[2][1][0])),int(round(line_pts[2][1][1]))), (255, 0, 0), thickness=2)
        #Magenta - Belly 
        # cv2.line(img, (int(round(line_pts[3][0][0])),int(round(line_pts[3][0][1]))), (int(round(line_pts[3][1][0])),int(round(line_pts[3][1][1]))), (255, 0, 255), thickness=2)
        # White - Cut 
        # cv2.line(img, (int(round(line_pts[4][0][0])),int(round(line_pts[4][0][1]))), (int(round(line_pts[4][1][0])),int(round(line_pts[4][1][1]))), (100, 205, 205), thickness=2)
        # except TypeError as err:
        #     print("Error: {0}".format(err))
