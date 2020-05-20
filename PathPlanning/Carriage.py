from Point import Point
import math
import cv2
<<<<<<< HEAD
=======
import numpy as np
>>>>>>> path_planning2

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
<<<<<<< HEAD
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "MainArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength " + str(self.length) + "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.angle = (self.otherPt - self.basePt).angle()
=======
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
>>>>>>> path_planning2

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
<<<<<<< HEAD
        cv2.rectangle(canvas, (self.basePt - Point(self.width/2, self.length/2)).toTuple(), (self.basePt + Point(self.width/2, self.length/2)).toTuple(), (255, 255, 255))
        # cv2.circle(canvas, self.basePt.toTuple(), 3, (255, 255, 255))
    
    def follow(self, pt:Point):
        pass
        # dr = pt - self.basePt
        # if dr.mag() <= self.min_length:
        #     self.length = self.min_length
        # elif dr.mag() <= self.max_length:
        #     self.length = dr.mag()
        # else:
        #     self.length = self.max_length

        # self.otherPt = pt
        # self.basePt = self.otherPt - dr.norm() * self.length

    def moveBase(self, pt:Point):
        # self.refresh()
=======
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
>>>>>>> path_planning2
        self.basePt = pt
        # self.otherPt = self.getOtherPt()