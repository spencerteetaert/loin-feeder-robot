import math

import numpy as np
import cv2

from ..model.point import Point 
from .. import global_parameters

font = cv2.FONT_HERSHEY_SIMPLEX

class Meat():
    def __init__(self, data, conveyor_speed=global_parameters.CONVEYOR_SPEED * global_parameters.RUNTIME_FACTOR, side="Left", center=(0,0)):
        self.conveyor_speed = conveyor_speed
        self.side = side
        self.bbox = data[0]
        self.center = center

        if (self.bbox == []):
            print("ERR: Meat object created with empty bbox.")
        else:
            self.loin_line = self.gen_significant_lines("loin")
            self.shoulder_line = self.gen_significant_lines("shoulder")
            self.ham_line = self.gen_significant_lines("ham")
            self.belly_line = self.gen_significant_lines("belly")
            self.cut_line = self.gen_significant_lines("cut")

            self.lines = [self.loin_line, self.shoulder_line, self.ham_line, self.belly_line, self.cut_line]

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
        self.shoulder_line = self.shoulder_line + step_vec
        self.ham_line = self.ham_line + step_vec
        self.belly_line = self.belly_line + step_vec
        self.cut_line = self.cut_line + step_vec
        self.center = self.center + step_vec

        self.lines = [self.loin_line, self.shoulder_line, self.ham_line, self.belly_line, self.cut_line]

    def gen_significant_lines(self, line):
        xs = self.bbox[:][0]
        ys = self.bbox[:][1]

        min_x_index = np.where(xs == min(xs))[0]
        min_y_index = np.where(ys == min(ys))[0]
        max_x_index = np.where(xs == max(xs))[0]
        max_y_index = np.where(ys == max(ys))[0]

        start_index = 0 
        direction = -1

        # print(min(xs))

        # print("min_x_index",min_x_index)
        # print("min_y_index",min_y_index)
        # print("max_x_index",max_x_index)
        # print("max_y_index",max_y_index)
        # print("xs", xs)
        # print("ys", ys)

        thresh_factor = 1
        if line == "loin": # Red
            if self.side == "Left":
                start_index = max_y_index
                if xs[start_index] > self.center[0]:
                    direction = 1
            else:
                start_index = min_y_index
                if xs[start_index] < self.center[0]:
                    direction = 1
        elif line == "shoulder": # Yellow
            start_index = min_x_index
            thresh_factor = global_parameters.SHORT_END_FACTOR
            if ys[start_index] > self.center[1]:
                direction = 1
        elif line == "ham": # Blue
            start_index = max_x_index
            thresh_factor = global_parameters.SHORT_END_FACTOR
            if ys[start_index] < self.center[1]:
                direction = 1
        elif line == "belly": # Magenta 
            if self.side == "Left":
                start_index = min_y_index
                if xs[start_index] < self.center[0]:
                    direction = 1
            else:
                start_index = max_y_index
                if xs[start_index] > self.center[0]:
                    direction = 1
        elif line == "cut":
            k = np.subtract(self.belly_line[0], self.belly_line[1])
            x = np.array([(k / np.linalg.norm(k))[1], -1*(k / np.linalg.norm(k))[0]])  # Find perpendicular normal
            
            if self.side == "Left":
                x *= -1

            dir_vect = x * global_parameters.LOIN_WIDTH
            ret = np.around(self.loin_line + dir_vect).astype(int)

            return ret
        else:
            print("ERR: Meat line generation failed. No line specified.")

        rotated_index = (start_index + len(self.bbox) + direction) % len(self.bbox)
        temp = start_index
        threshold = global_parameters.LINE_THRESHOLD * thresh_factor

        while(self.distance(self.bbox[start_index], self.bbox[rotated_index]) < threshold):
            if global_parameters.CHANGING_START_INDEX:
                start_index = rotated_index
            rotated_index = (rotated_index + len(self.bbox) + direction) % len(self.bbox)

            if temp == start_index:
                threshold -= 5

        ret = self.find_line_from_points(self.bbox[start_index], self.bbox[rotated_index])

        return ret

    def find_line_from_points(self, pt1, pt2):
        # print("P1: ", pt1, "P2:",pt2)
        dy = pt2[0][1] - pt1[0][1]
        dx = pt2[0][0] - pt1[0][0]

        ret_pt1 = [pt2[0][0] + dx * 100, pt2[0][1] + dy * 100]
        ret_pt2 = [pt2[0][0] - dx * 100, pt2[0][1] - dy * 100]

        # Ensure all point sets go left to right
        if ret_pt1[0] < ret_pt2[0]:
            return [ret_pt1, ret_pt2]
        else:
            return [ret_pt2, ret_pt1]

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

    def distance(self, pt1, pt2):
        return math.sqrt((pt2[0][1] - pt1[0][1])**2 + (pt2[0][0] - pt1[0][0])**2)

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
        line_pts = self.get_lines()

        #Red - Loin
        # cv2.line(img, (int(round(line_pts[0][0][0])),int(round(line_pts[0][0][1]))), (int(round(line_pts[0][1][0])),int(round(line_pts[0][1][1]))), (0, 0, 255), thickness=2)
        #Yellow - Shoulder
        # cv2.line(img, (int(round(line_pts[1][0][0])),int(round(line_pts[1][0][1]))), (int(round(line_pts[1][1][0])),int(round(line_pts[1][1][1]))), (0, 255, 255), thickness=2)
        #Blue - Ham
        # cv2.line(img, (int(round(line_pts[2][0][0])),int(round(line_pts[2][0][1]))), (int(round(line_pts[2][1][0])),int(round(line_pts[2][1][1]))), (255, 0, 0), thickness=2)
        #Magenta - Belly 
        # cv2.line(img, (int(round(line_pts[3][0][0])),int(round(line_pts[3][0][1]))), (int(round(line_pts[3][1][0])),int(round(line_pts[3][1][1]))), (255, 0, 255), thickness=2)
        #White - Cut 
        # cv2.line(img, (int(round(line_pts[4][0][0])),int(round(line_pts[4][0][1]))), (int(round(line_pts[4][1][0])),int(round(line_pts[4][1][1]))), (100, 205, 205), thickness=2)
        # except TypeError as err:
        #     print("Error: {0}".format(err))
