import numpy as np
import cv2
import math

class Meat():
    def __init__(self, bbox, conveyor_speed=6, side="Left"):
        self.conveyor_speed = conveyor_speed
        self.side = side
        self.bbox = bbox
        # self.area = cv2.contourArea(self.bbox)

        if (self.bbox == []):
            print("ERR: Meat object created with empty bbox.")
        else:
            self.loin_line = self.gen_significant_lines("loin")
            self.shoulder_line = self.gen_significant_lines("shoulder")
            self.ham_line = self.gen_significant_lines("ham")
            self.flank_line = self.gen_significant_lines("flank")
            self.cut_line = self.gen_significant_lines("cut")

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
        self.flank_line = self.flank_line + step_vec
        self.cut_line = self.cut_line + step_vec

    def gen_significant_lines(self, line):
        xs = self.bbox[:,0,0]
        ys = self.bbox[:,0,1]

        min_x_index = np.where(xs == min(xs))[0][0]
        min_y_index = np.where(ys == min(ys))[0][0]
        max_x_index = np.where(xs == max(xs))[0][0]
        max_y_index = np.where(ys == max(ys))[0][0]

        start_index = 0 
        threshold = 50 

        # print(min(xs))

        # print("min_x_index",min_x_index)
        # print("min_y_index",min_y_index)
        # print("max_x_index",max_x_index)
        # print("max_y_index",max_y_index)
        # print("xs", xs)
        # print("ys", ys)

        if line == "loin":
            threshold = 100 
            if self.side == "Left":
                start_index = max_y_index
            else:
                start_index = min_y_index
        elif line == "shoulder":
            start_index = min_x_index
        elif line == "ham":
            start_index = max_x_index
        elif line == "flank":
            threshold = 100 
            if self.side == "Left":
                start_index = min_y_index
            else:
                start_index = max_y_index
        elif line == "cut":
            pass
        else:
            print("ERR: Meat line generation failed. No line specified.")

        rotated_index = (start_index + len(self.bbox) - 1) % len(self.bbox)
        temp = start_index

        while(self.distance(self.bbox[start_index], self.bbox[rotated_index]) < threshold):
            start_index = (start_index + len(self.bbox) - 1) % len(self.bbox)
            rotated_index = (start_index + len(self.bbox) - 1) % len(self.bbox)

            if temp == start_index:
                threshold -= 5

        ret = self.find_line_from_points(self.bbox[start_index], self.bbox[rotated_index])

        return ret

    def find_line_from_points(self, pt1, pt2):
        # print("P1: ", pt1, "P2:",pt2)
        dy = pt2[0][1] - pt1[0][1]
        dx = pt2[0][0] - pt1[0][0]

        ret_pt1 = (pt2[0][0] + dx * 1000, pt2[0][1] + dy * 1000)
        ret_pt2 = (pt2[0][0] - dx * 1000, pt2[0][1] - dy * 1000)

        return [ret_pt1, ret_pt2]

    def get_lines(self):
        ret = []
        ret += [self.loin_line]
        ret += [self.shoulder_line]
        ret += [self.ham_line]
        ret += [self.flank_line]

        return ret

    def get_bbox(self):
        return self.bbox

    def distance(self, pt1, pt2):
        return math.sqrt((pt2[0][1] - pt1[0][1])**2 + (pt2[0][0] - pt1[0][0])**2)