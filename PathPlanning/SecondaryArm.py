from Point import Point
import math
import cv2

import sys
import os
sys.path.insert(1, os.getcwd())
import GlobalParameters as gp

class SecondaryArm:
    def __init__(self, pt:Point, length1, length2, angle=0):
        self.basePt = pt
        self.length1 = length1
        self.length2 = length2
        self.min_length = gp.SECONDARY_MIN_LENGTH
        self.max_length = gp.SECONDARY_MAX_LENGTH
        self.angle = angle 
        self.otherPt1 = self.getotherPt1()
        self.otherPt2 = self.getotherPt2()

    def __repr__(self):
        return "SecondayArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength1 " + str(self.length1) + "\n\tLength2 " + str(self.length2)+ "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.angle = (self.otherPt1 - self.basePt).angle()

    def getotherPt1(self):
        return Point(round(self.basePt.x + self.length1 * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length1 * math.sin(math.radians(self.angle))))
    def getotherPt2(self):
        return Point(round(self.basePt.x - self.length2 * math.cos(math.radians(self.angle))), round(self.basePt.y + self.length2 * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.otherPt1.toTuple(), self.otherPt2.toTuple(), (255, 255, 255), 2) 
        cv2.circle(canvas, self.basePt.toTuple(), 3, (255, 255, 255))

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

    def moveBase(self, pt:Point):
        self.refresh()
        self.basePt = pt
        self.otherPt1 = self.getotherPt1()
        self.otherPt2 = self.getotherPt2()