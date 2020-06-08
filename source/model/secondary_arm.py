import math

import cv2

from .point import Point
from ..global_parameters import global_parameters

class SecondaryArm:
    def __init__(self, pt:Point, scale, length1=0.354, length2=0.354, angle=90, relative_angle=90):
        self.scale = scale
        self.base_pt = pt
        self.length1 = length1 * scale
        self.length2 = length2 * scale
        self.min_length = global_parameters['SECONDARY_ARM_MIN_LENGTH'] * scale
        self.max_length = global_parameters['SECONDARY_ARM_MAX_LENGTH'] * scale
        self.angle = angle 
        self.relative_angle = relative_angle
        self.other_pt1 = self.get_other_pt1()
        self.other_pt2 = self.get_other_pt2()
        self.refresh()

        self.last_pos = self.length1/self.scale
        self.delta_pos = 0
        self.last_angle = self.angle
        self.delta_angle = 0

    def __repr__(self):
        return "Seconday Arm\n\tLength1 " + str(round(self.length1/self.scale, 3)) + "m\n\tLength2 " + str(round(self.length2/self.scale, 3))+ "m\n\tAngle " + str(round(self.relative_angle, 1)) + "\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n\tdA " + str(round(self.delta_angle, 3)) + "\n"

    def refresh(self, main_arm_angle=None):
        self.angle = (self.other_pt1 - self.base_pt).vector_angle()
        if main_arm_angle != None:
            self.relative_angle = (self.angle - main_arm_angle + 360 + 180) % 360

    def get_other_pt1(self):
        return Point(round(self.base_pt.x + self.length1 * math.cos(math.radians(self.angle))), round(self.base_pt.y - self.length1 * math.sin(math.radians(self.angle))))
    def get_other_pt2(self):
        return Point(round(self.base_pt.x - self.length2 * math.cos(math.radians(self.angle))), round(self.base_pt.y + self.length2 * math.sin(math.radians(self.angle))))

    def get_max_pt_vector(self):
        return self.base_pt - Point(round(self.base_pt.x + self.max_length * math.cos(math.radians(self.angle))), round(self.base_pt.y - self.max_length * math.sin(math.radians(self.angle))))
    def get_min_pt_vector(self):
        return self.base_pt - Point(round(self.base_pt.x + self.min_length * math.cos(math.radians(self.angle))), round(self.base_pt.y - self.min_length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, (self.base_pt + self.get_max_pt_vector()).to_tuple(), (self.base_pt - self.get_max_pt_vector()).to_tuple(), (255, 255, 255), 8) 
        cv2.line(canvas, (self.base_pt + self.get_max_pt_vector()).to_tuple(), (self.base_pt + self.get_min_pt_vector()).to_tuple(), (0, 0, 0), 3) 
        cv2.line(canvas, (self.base_pt - self.get_max_pt_vector()).to_tuple(), (self.base_pt - self.get_min_pt_vector()).to_tuple(), (0, 0, 0), 3) 
        cv2.circle(canvas, self.other_pt1.to_tuple(), self.scale//20, (255, 255, 255))
        cv2.circle(canvas, self.other_pt2.to_tuple(), self.scale//20, (255, 255, 255))

    def follow(self, pt1:Point, pt2:Point):
        half_dist = (pt1-pt2).mag()/2
        dr = (pt1 - pt2).norm()

        if half_dist > self.max_length:
            self.length1 = self.max_length
            self.length2 = self.max_length
        elif half_dist < self.min_length:
            self.length1 = self.min_length
            self.length2 = self.min_length
        else:
            self.length1 = (dr * half_dist).mag()
            self.length2 = self.length1
            
        self.base_pt = pt1 - dr * half_dist
        self.other_pt1 = self.base_pt + dr * self.length1
        self.other_pt2 = self.base_pt - dr * self.length2

        self.refresh()

        self.delta_pos = self.length1/self.scale - self.last_pos
        self.last_pos = self.length1/self.scale
        self.delta_angle = self.angle - self.last_angle
        self.last_angle = self.angle

    def move_base(self, pt:Point, main_arm_angle):
        self.refresh(main_arm_angle)
        self.base_pt = pt
        self.other_pt1 = self.get_other_pt1()
        self.other_pt2 = self.get_other_pt2()

    def get_collision_bounds(self):
        p = self.other_pt1.to_array()
        r = (self.other_pt2 - self.other_pt1).to_array()
        return [[p, r]]

    def set_model_state(self, state):
        '''
            0: Main arm other pt
            1: Main arm angle
            2: Length1
            3: Length2
            4: Angle
        '''
        angle = (state[4] + state[1] + 180 + 720) % 360
        self.__init__(state[0], self.scale, length1=state[2], length2=state[3], angle=angle, relative_angle=state[1])