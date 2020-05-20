import math

import cv2
import numpy as np

from .Point import Point
from .. import GlobalParameters

class Carriage:
    def __init__(self, pt:Point, scale, length=100, angle=0):
        self.scale = scale
        self.basePt = pt
        self.width = GlobalParameters.CARRIAGE_WIDTH * scale
        self.length = GlobalParameters.CARRIAGE_LENGTH * scale
        self.angle = angle 
        self.relative_angle = 0
        self.otherPt = self.getOtherPt()

        self.last_angle = self.relative_angle
        self.delta_angle = 0

    def __repr__(self):
        return "Carriage\n\tAngle " + str(round(self.relative_angle, 1)) + "\n\tdA " + str(round(self.delta_angle, 3)) + "\n" 

    def refresh(self, secondary_arm_angle=None):
        # self.angle = (self.otherPt - self.basePt).vector_angle()
        if secondary_arm_angle != None:
            self.relative_angle = (self.angle - secondary_arm_angle + 360) % 360

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

        self.delta_angle = self.relative_angle - self.last_angle
        self.last_angle = self.relative_angle
        
    def moveBase(self, pt:Point, secondary_arm_angle):
        self.refresh(secondary_arm_angle)
        self.basePt = pt
        # self.otherPt = self.getOtherPt()