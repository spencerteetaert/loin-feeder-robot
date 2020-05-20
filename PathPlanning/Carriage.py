from Point import Point
import math
import cv2
import numpy as np

import sys
import os
sys.path.insert(1, os.getcwd())
import GlobalParameters as gp
class Carriage:
    def __init__(self, pt:Point, scale, length=100, angle=0):
        self.scale = scale
        self.basePt = pt
        self.width = gp.CARRIAGE_WIDTH * scale
        self.length = gp.CARRIAGE_LENGTH * scale
        self.angle = angle 
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "MainArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength " + str(self.length) + "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.angle = (self.otherPt - self.basePt).vector_angle()

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        points = []

        k = np.array([self.length*math.cos(math.radians(self.angle))/2, -1 * self.length*math.sin(math.radians(self.angle))/2])
        x = np.array([(k / np.linalg.norm(k))[1] * self.width/2, -1 * self.width * (k / np.linalg.norm(k))[0]/2])  # Find perpendicular normal

        points += [(self.basePt.toArray() + k + x)]
        points += [(self.basePt.toArray() + k - x)]
        points += [(self.basePt.toArray() - k - x)]
        points += [(self.basePt.toArray() - k + x)]

        
        contour = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
        cv2.drawContours(canvas, [contour], 0, (255, 255, 255))

    def follow(self, pt:Point):
        if pt.angle != None:
            self.angle = pt.angle
        
    def moveBase(self, pt:Point):
        # self.refresh()
        self.basePt = pt
        # self.otherPt = self.getOtherPt()