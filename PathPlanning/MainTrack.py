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
<<<<<<< HEAD
=======
        self.last_pos = self.length/self.scale
        self.delta_pos = 0
>>>>>>> path_planning2
        self.min_length = gp.MAIN_TRACK_MIN_LENGTH * scale
        self.max_length = gp.MAIN_TRACK_MAX_LENGTH * scale
        self.otherPt = self.getOtherPt()

    def __repr__(self):
<<<<<<< HEAD
        return "Main Track\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n"
=======
        return "Main Track\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n"
>>>>>>> path_planning2

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

<<<<<<< HEAD
=======
        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_pos = self.length/self.scale

>>>>>>> path_planning2
    def moveBase(self, pt:Point):
        self.basePt = pt
        self.otherPt = self.getOtherPt()