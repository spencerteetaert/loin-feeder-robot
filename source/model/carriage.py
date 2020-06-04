import math

import cv2
import numpy as np

from .point import Point
from ..global_parameters import global_parameters
from .. import vector_tools

class Carriage:
    def __init__(self, pt:Point, scale, angle=0):
        self.scale = scale
        self.basePt = pt
        self.width = global_parameters['CARRIAGE_WIDTH'] * scale
        self.length = global_parameters['CARRIAGE_LENGTH'] * scale
        self.angle = angle 
        self.relative_angle = 90
        self.otherPt = self.getOtherPt()

        self.last_angle = self.relative_angle
        self.delta_angle = 0

        self.hyp_dist = math.sqrt(self.length**2 + self.width**2)/2
        self.update_points()
        
    def __repr__(self):
        return "Carriage\n\tAngle " + str(round(self.relative_angle, 1)) + "\n\tdA " + str(round(self.delta_angle, 3)) + "\n" 

    def refresh(self, secondary_arm_angle=None):
        # self.angle = (self.otherPt - self.basePt).vector_angle()
        if secondary_arm_angle != None:
            self.relative_angle = (self.angle - secondary_arm_angle + 360 + 180) % 360

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))/2), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))/2))

    def draw(self, canvas, color=(255, 255, 255)):      
        contour = np.array(self.points).reshape((-1, 1, 2)).astype(np.int32)
        cv2.drawContours(canvas, [contour], 0, color, 2)

    def follow(self, pt:Point):
        if pt.angle != None:
            self.angle = pt.angle

        self.delta_angle = self.relative_angle - self.last_angle
        self.last_angle = self.relative_angle
        
    def moveBase(self, pt:Point, secondary_arm_angle):
        self.refresh(secondary_arm_angle)
        self.basePt = pt
        self.update_points()

    def update_points(self):
        self.points = []

        k = np.array([self.length*math.cos(math.radians(self.angle))/2, -1 * self.length*math.sin(math.radians(self.angle))/2])
        x = vector_tools.get_normal_unit([0, 0], k)
        x *= self.width/2

        self.points += [(self.basePt.toArray() + k + x)] # top right
        self.points += [(self.basePt.toArray() + k - x)] # top left
        self.points += [(self.basePt.toArray() - k - x)] # bottom left
        self.points += [(self.basePt.toArray() - k + x)] # bottom right 
        self.otherPt = self.getOtherPt()

    def get_collision_bounds(self):
        r1 = np.subtract(self.points[1], self.points[2])
        r2 = np.subtract(self.points[1], self.points[0]) 
        r3 = np.subtract(self.points[3], self.points[2])
        r4 = np.subtract(self.points[3], self.points[0])
        
        return [[self.points[1], r3], [self.points[1], r4], [self.points[3], r1], [self.points[3], r2]]