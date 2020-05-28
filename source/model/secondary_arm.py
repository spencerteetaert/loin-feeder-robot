import math

import cv2

from .point import Point
from .. import global_parameters

class SecondaryArm: #0.47
    def __init__(self, pt:Point, scale, length1=0.354, length2=0.354, angle=90):
        self.scale = scale
        self.basePt = pt
        self.length1 = length1 * scale
        self.length2 = length2 * scale
        self.min_length = global_parameters.SECONDARY_ARM_MIN_LENGTH * scale
        self.max_length = global_parameters.SECONDARY_ARM_MAX_LENGTH * scale
        self.angle = angle 
        self.relative_angle = 90
        self.otherPt1 = self.getotherPt1()
        self.otherPt2 = self.getotherPt2()
        self.refresh()

        self.last_pos = self.length1/self.scale
        self.delta_pos = 0
        self.last_angle = self.angle
        self.delta_angle = 0

    def __repr__(self):
        return "Seconday Arm\n\tLength1 " + str(round(self.length1/self.scale, 3)) + "m\n\tLength2 " + str(round(self.length2/self.scale, 3))+ "m\n\tAngle " + str(round(self.relative_angle, 1)) + "\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n\tdA " + str(round(self.delta_angle, 3)) + "\n"

    def refresh(self, main_arm_angle=None):
        self.angle = (self.otherPt1 - self.basePt).vector_angle()
        if main_arm_angle != None:
            self.relative_angle = (self.angle - main_arm_angle + 360 + 180) % 360

    def getotherPt1(self):
        return Point(round(self.basePt.x + self.length1 * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length1 * math.sin(math.radians(self.angle))))
    def getotherPt2(self):
        return Point(round(self.basePt.x - self.length2 * math.cos(math.radians(self.angle))), round(self.basePt.y + self.length2 * math.sin(math.radians(self.angle))))

    def get_max_pt_vector(self):
        return self.basePt - Point(round(self.basePt.x + self.max_length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.max_length * math.sin(math.radians(self.angle))))
    def get_min_pt_vector(self):
        return self.basePt - Point(round(self.basePt.x + self.min_length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.min_length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, (self.basePt + self.get_max_pt_vector()).toTuple(), (self.basePt - self.get_max_pt_vector()).toTuple(), (255, 255, 255), 8) 
        cv2.line(canvas, (self.basePt + self.get_max_pt_vector()).toTuple(), (self.basePt + self.get_min_pt_vector()).toTuple(), (0, 0, 0), 3) 
        cv2.line(canvas, (self.basePt - self.get_max_pt_vector()).toTuple(), (self.basePt - self.get_min_pt_vector()).toTuple(), (0, 0, 0), 3) 
        cv2.circle(canvas, self.otherPt1.toTuple(), self.scale//20, (255, 255, 255))
        cv2.circle(canvas, self.otherPt2.toTuple(), self.scale//20, (255, 255, 255))

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
            
        self.basePt = pt1 - dr * half_dist
        self.otherPt1 = self.basePt + dr * self.length1
        self.otherPt2 = self.basePt - dr * self.length2

        self.refresh()

        self.delta_pos = self.length1/self.scale - self.last_pos
        self.last_pos = self.length1/self.scale
        self.delta_angle = self.angle - self.last_angle
        self.last_angle = self.angle

    def moveBase(self, pt:Point, main_arm_angle):
        self.refresh(main_arm_angle)
        self.basePt = pt
        self.otherPt1 = self.getotherPt1()
        self.otherPt2 = self.getotherPt2()

    def get_collision_bounds(self):
        p = self.otherPt1.toArray()
        r = (self.otherPt2 - self.otherPt1).toArray()
        return [[p, r]]