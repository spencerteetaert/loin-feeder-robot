import numpy as np
import cv2
import math

loin_width = 100
class Meat():
    def __init__(self, bbox, conveyor_speed=6, side="Left", center=(0,0)):
        self.conveyor_speed = conveyor_speed
        self.side = side
        self.bbox = bbox
        self.center = center
        # self.area = cv2.contourArea(self.bbox)

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
        xs = self.bbox[:,0,0]
        ys = self.bbox[:,0,1]

        min_x_index = np.where(xs == min(xs))[0][0]
        min_y_index = np.where(ys == min(ys))[0][0]
        max_x_index = np.where(xs == max(xs))[0][0]
        max_y_index = np.where(ys == max(ys))[0][0]

        start_index = 0 
        threshold = 10
        direction = -1

        # print(min(xs))

        # print("min_x_index",min_x_index)
        # print("min_y_index",min_y_index)
        # print("max_x_index",max_x_index)
        # print("max_y_index",max_y_index)
        # print("xs", xs)
        # print("ys", ys)

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
            if ys[start_index] > self.center[1]:
                direction = 1
        elif line == "ham": # Blue
            start_index = max_x_index
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

            temp = self.loin_line

            x = np.random.randn(2)  # take a random vector
            # print("1",x)
            x -= x.dot(k) * k       # make it orthogonal to k
            # print("2",x)
            x /= np.linalg.norm(x)  # normalize it
            # print("3",x)
            
            if self.side == "Left":
                x *= -1
            # print("3",x)

            dir_vect = x * loin_width
            # print("4", dir_vect)

            ret = np.around(temp + dir_vect).astype(int)
            # print("5", ret)

            return ret
        else:
            print("ERR: Meat line generation failed. No line specified.")

        rotated_index = (start_index + len(self.bbox) + direction) % len(self.bbox)
        temp = start_index

        while(self.distance(self.bbox[start_index], self.bbox[rotated_index]) < threshold):
            start_index = (start_index + len(self.bbox) + direction) % len(self.bbox)
            rotated_index = (start_index + len(self.bbox) + direction) % len(self.bbox)

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

    def get_center(self):
        return self.center

    def get_lines(self):
        return self.lines

    def get_bbox(self):
        return self.bbox

    def get_side(self):
        return self.side

    def distance(self, pt1, pt2):
        return math.sqrt((pt2[0][1] - pt1[0][1])**2 + (pt2[0][0] - pt1[0][0])**2)