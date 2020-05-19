from Point import Point
import math
import cv2

import sys
import os
sys.path.insert(1, os.getcwd())
import GlobalParameters as gp
class MainArm:
    def __init__(self, pt:Point, length=100, angle=0):
        self.basePt = pt
        self.length = length
        self.min_length = gp.MAIN_MIN_LENGTH
        self.max_length = gp.MAIN_MAX_LENGTH
        self.angle = angle 
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "MainArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength " + str(self.length) + "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.angle = (self.otherPt - self.basePt).angle()

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.basePt.toTuple(), self.otherPt.toTuple(), (255, 255, 255), 5) 
        # cv2.circle(canvas, self.basePt.toTuple(), 3, (255, 255, 255))
    
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