import math

import cv2

from .point import Point
from .. import global_parameters

class MainTrack:
    def __init__(self, pt:Point, scale, length=0.1):
        self.scale = scale
        self.basePt = pt
        self.length = length * scale
        self.last_pos = self.length/self.scale
        self.delta_pos = 0
        self.min_length = global_parameters.MAIN_TRACK_MIN_LENGTH * scale
        self.max_length = global_parameters.MAIN_TRACK_MAX_LENGTH * scale
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "Main Track\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n"

    def getOtherPt(self):
        return Point(self.basePt.x, self.basePt.y - self.length)

    def get_min_pt_vector(self):
        return Point(round(self.basePt.x), round(self.basePt.y - self.min_length))
    def get_max_pt_vector(self):
        return Point(round(self.basePt.x), round(self.basePt.y - self.max_length))

    def draw(self, canvas):
        cv2.line(canvas, self.get_max_pt_vector().toTuple(), self.basePt.toTuple(), (255, 255, 255), 8) 
        cv2.line(canvas, self.get_max_pt_vector().toTuple(), self.get_min_pt_vector().toTuple(), (0, 0, 0), 3) 
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

        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_pos = self.length/self.scale

    def moveBase(self, pt:Point):
        self.basePt = pt
        self.otherPt = self.getOtherPt()