import math
from copy import deepcopy

import cv2
import numpy as np

class Point:
    def __init__(self, x, y, angle=None, steps=0, vec=None):
        self.x = x
        self.y = y
        self.angle = angle
        self.steps_remaining = steps
        self.update_vec = vec
        self.delay = 0

    def __repr__(self):
        ret = "Point(" + str(self.x) + ", " + str(self.y)
        if self.angle != None:
            ret += ", angle=" + str(self.angle)
        ret += ")"
        return ret

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y, angle=self.angle, steps=self.steps_remaining, vec=self.update_vec)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, angle=self.angle, steps=self.steps_remaining, vec=self.update_vec)
    def __mul__(self, factor):
        return Point(self.x * factor, self.y * factor, angle=self.angle, steps=self.steps_remaining, vec=self.update_vec)
    def __truediv__(self, factor):
        return Point(self.x / factor, self.y / factor, angle=self.angle, steps=self.steps_remaining, vec=self.update_vec)
    def __floordiv__(self, factor):
        return Point(self.x // factor, self.y // factor, angle=self.angle, steps=self.steps_remaining, vec=self.update_vec)

    def mag(self):
        return (self.x**2 + self.y**2)**0.5
    def norm(self):
        return Point(self.x / self.mag(), self.y / self.mag(), angle=self.angle, steps=self.steps_remaining, vec=self.update_vec)
    def vector_angle(self):
        if self.x < 0:
            return (math.degrees(math.atan((-1*self.y)/self.x)) + 180 + 360) % 360
        elif self.x == 0:
            if self.y < 0:
                return 90
            else:
                return 270
        else:
            return (math.degrees(math.atan((-1*self.y)/self.x)) + 360) % 360
    def rotate(self, angle, ref_pt):
        temp = Point(self.x, self.y)
        temp -= ref_pt

        angle_r = math.radians(angle)

        ret = Point(temp.x * math.cos(angle_r) - temp.y * math.sin(angle_r), 
           temp.x * math.sin(angle_r) + temp.y * math.cos(angle_r))

        ret += ref_pt
        
        self.x = ret.x
        self.y = ret.y

    def draw(self, canvas, color=(0, 0, 255), size=3):
        cv2.circle(canvas, self.toTuple(), size, color)
        if self.angle != None:
            cv2.line(canvas, self.toTuple(), (int(round(self.x + 20*math.cos(math.radians(self.angle)))), int(round(self.y - 20*math.sin(math.radians(self.angle))))), color)
    def toTuple(self):
        return (int(round(self.x)), int(round(self.y)))
    def toArray(self):
        return np.array([self.x, self.y])
    def copy(self):
        ret = Point(self.x, self.y, angle=self.angle)
        ret.steps_remaining = self.steps_remaining
        ret.update_vec = self.update_vec
        return ret


    def moveTo(self, otherPt, dt, delay=0):
        dX = (otherPt.x - self.x)/dt
        dY = (otherPt.y - self.y)/dt
        dA = 0
        if self.angle != None and otherPt.angle != None:
            temp = otherPt.angle - self.angle
            if temp > 180:
                dA = -1*(360 - temp)/dt
            elif temp < -180:
                dA = -1*(360 + temp)/dt
            else:
                dA = temp/dt

        self.update_vec = Point(dX, dY, angle=dA)
        self.steps_remaining = dt
        self.delay = delay
        
    def update(self):
        if self.steps_remaining > 0:
            if self.delay > 0:
                self.delay -= 1
                return True 
            self.x += self.update_vec.x
            self.y += self.update_vec.y
            if self.angle != None:
                self.angle += self.update_vec.angle
            self.steps_remaining -= 1
            if self.steps_remaining <= 0:
                return False
            return True
        return False