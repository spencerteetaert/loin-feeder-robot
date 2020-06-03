import math

import cv2
import numpy as np

from .point import Point
from .. import global_parameters

class MainArm:
    def __init__(self, pt:Point, scale, length=0.75, angle=180):
        self.scale = scale
        self.basePt = pt
        self.length = length * scale
        self.min_length = global_parameters.MAIN_ARM_MIN_LENGTH * scale
        self.max_length = global_parameters.MAIN_ARM_MAX_LENGTH * scale
        self.angle = angle 
        self.otherPt = self.getOtherPt()
        self.refresh()

        self.last_pos = 0
        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_angle = 0
        self.delta_angle = self.angle - self.last_angle

    def __repr__(self):
        return "Main Arm\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n\tAngle " + str(round(self.angle, 1)) + "\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n\tdA " + str(round(self.delta_angle, 3)) + "\n" 

    def refresh(self):
        self.angle = ((self.otherPt - self.basePt).vector_angle() + 180) % 360

    def getOtherPt(self):
        return Point(round(self.basePt.x - self.length * math.cos(math.radians(self.angle))), round(self.basePt.y + self.length * math.sin(math.radians(self.angle))))

    def get_min_pt_vector(self):
        return Point(round(self.basePt.x - self.min_length * math.cos(math.radians(self.angle))), round(self.basePt.y + self.min_length * math.sin(math.radians(self.angle))))
    def get_max_pt_vector(self):
        return Point(round(self.basePt.x - self.max_length * math.cos(math.radians(self.angle))), round(self.basePt.y + self.max_length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.get_max_pt_vector().toTuple(), self.basePt.toTuple(), (255, 255, 255), 8) 
        cv2.line(canvas, self.get_max_pt_vector().toTuple(), self.get_min_pt_vector().toTuple(), (0, 0, 0), 3) 
        cv2.circle(canvas, self.otherPt.toTuple(), self.scale//15, (255, 255, 255))
    
    def follow(self, pt:Point, secondary_arm_angle):
        dr = pt - self.basePt
        if dr.mag() <= self.min_length:
            self.length = self.min_length
        elif dr.mag() <= self.max_length:
            self.length = dr.mag()
        else:
            self.length = self.max_length

        self.otherPt = pt
        self.basePt = self.otherPt - dr.norm() * self.length

        # Rotational bounds 
        self.refresh()
        rel_angle = (secondary_arm_angle - self.angle + 360) % 360 
        if rel_angle < global_parameters.MAIN_ARM_MIN_ANGLE:
            self.basePt.rotate(global_parameters.MAIN_ARM_MIN_ANGLE - rel_angle, self.otherPt)
        elif rel_angle > global_parameters.MAIN_ARM_MAX_ANGLE:
            self.basePt.rotate(global_parameters.MAIN_ARM_MAX_ANGLE - rel_angle, self.otherPt)

        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_pos = self.length/self.scale
        self.delta_angle = self.angle - self.last_angle
        self.last_angle = self.angle

    def moveBase(self, pt:Point):
        self.refresh()
        self.basePt = pt
        self.otherPt = self.getOtherPt()

    def get_collision_bounds(self):
        p = np.add(self.basePt.toArray(), [global_parameters.MAIN_ARM_WIDTH, global_parameters.MAIN_ARM_WIDTH])
        r1 = np.array([0, -1000])
        r2 = np.array([-1000, 0])

        return [[p, r1], [p, r2]]