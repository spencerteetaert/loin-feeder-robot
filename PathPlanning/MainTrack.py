from Point import Point
import math
import cv2

import sys
import os
sys.path.insert(1, os.getcwd())
import GlobalParameters as gp

class MainTrack:
    def __init__(self, pt:Point, scale, length=100):
        self.scale = scale
        self.basePt = pt
        self.length = length
        self.min_length = gp.MAIN_TRACK_MIN_LENGTH * scale
        self.max_length = gp.MAIN_TRACK_MAX_LENGTH * scale
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "Main Track\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n"

    def getOtherPt(self):
        return Point(self.basePt.x, self.basePt.y - self.length)

    def draw(self, canvas):
        cv2.line(canvas, self.basePt.toTuple(), Point(self.basePt.x, self.basePt.y - self.max_length).toTuple(), (255, 255, 255), 1) 
        cv2.circle(canvas, self.otherPt.toTuple(), self.scale//10, (255, 255, 255))
    
    def follow(self, pt:Point):
        dr = self.basePt.y - pt.y 
        if dr <= self.min_length:
            self.length = self.min_length
        elif dr <= self.max_length:
            self.length = dr
        else:
            self.length = self.max_length

        self.otherPt = Point(self.basePt.x, pt.y)
        self.basePt = Point(self.otherPt.x, self.otherPt.y + self.length)

    def moveBase(self, pt:Point):
        self.basePt = pt
        self.otherPt = self.getOtherPt()