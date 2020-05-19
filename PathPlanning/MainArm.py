from Point import Point
import math
import cv2

import sys
import os
sys.path.insert(1, os.getcwd())
import GlobalParameters as gp
class MainArm:
    def __init__(self, pt:Point, scale, length=100, angle=0):
        self.scale = scale
        self.basePt = pt
        self.length = length
        self.min_length = gp.MAIN_ARM_MIN_LENGTH * scale
        self.max_length = gp.MAIN_ARM_MAX_LENGTH * scale
        self.angle = angle 
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "Main Arm\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n\tAngle " + str(round(self.angle, 1)) + "\n"

    def refresh(self):
        self.angle = (self.otherPt - self.basePt).angle()

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))
    def get_max_pt_vector(self):
        return Point(round(self.basePt.x + self.max_length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.max_length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.get_max_pt_vector().toTuple(), self.basePt.toTuple(), (255, 255, 255), 8) 
        cv2.circle(canvas, self.otherPt.toTuple(), self.scale//15, (255, 255, 255))
    
    def follow(self, pt:Point):
        dr = pt - self.basePt
        if dr.mag() <= self.min_length:
            self.length = self.min_length
        elif dr.mag() <= self.max_length:
            self.length = dr.mag()
        else:
            self.length = self.max_length

        self.otherPt = pt
        self.basePt = self.otherPt - dr.norm() * self.length

    def moveBase(self, pt:Point):
        self.refresh()
        self.basePt = pt
        self.otherPt = self.getOtherPt()