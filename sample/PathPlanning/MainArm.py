import math

import cv2

from .Point import Point
from .. import GlobalParameters

class MainArm:
    def __init__(self, pt:Point, scale, length=100, angle=0):
        self.scale = scale
        self.basePt = pt
        self.length = length
        self.min_length = GlobalParameters.MAIN_ARM_MIN_LENGTH * scale
        self.max_length = GlobalParameters.MAIN_ARM_MAX_LENGTH * scale
        self.angle = angle 
        self.otherPt = self.getOtherPt()

        self.last_pos = 0
        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_angle = 0
        self.delta_angle = self.angle - self.last_angle

    def __repr__(self):
        return "Main Arm\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n\tAngle " + str(round(self.angle, 1)) + "\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n\tdA " + str(round(self.delta_angle, 3)) + "\n" 

    def refresh(self):
        self.angle = (self.otherPt - self.basePt).vector_angle()

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))

    def get_max_pt_vector(self):
        return Point(round(self.basePt.x + self.max_length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.max_length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.get_max_pt_vector().toTuple(), self.basePt.toTuple(), (255, 255, 255), 8) 
        cv2.circle(canvas, self.otherPt.toTuple(), self.scale//15, (255, 255, 255))
    
    def follow(self, pt:Point, secondary_arm_angle):
        dr = pt - self.basePt
        if dr.mag() <= self.min_length:
            self.length = self.min_length
        elif dr.mag() <= self.max_length:
            self.length = dr.mag()
        else:
            self.length = self.max_length

        self.otherPt = pt
        self.basePt = self.otherPt - dr.norm() * self.length

        # Rotational bounds 
        self.refresh()
        rel_angle = (secondary_arm_angle - self.angle + 360) % 360 
        if rel_angle < GlobalParameters.MAIN_ARM_MIN_ANGLE:
            self.basePt.rotate(GlobalParameters.MAIN_ARM_MIN_ANGLE - rel_angle, self.otherPt)
        elif rel_angle > GlobalParameters.MAIN_ARM_MAX_ANGLE:
            self.basePt.rotate(GlobalParameters.MAIN_ARM_MAX_ANGLE - rel_angle, self.otherPt)

        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_pos = self.length/self.scale
        self.delta_angle = self.angle - self.last_angle
        self.last_angle = self.angle

    def moveBase(self, pt:Point):
        self.refresh()
        self.basePt = pt
        self.otherPt = self.getOtherPt()