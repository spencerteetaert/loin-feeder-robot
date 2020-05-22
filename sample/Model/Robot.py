import time

import cv2
import numpy as np

from .Point import Point
from .MainTrack import MainTrack
from .MainArm import MainArm 
from .SecondaryArm import SecondaryArm
from .Carriage import Carriage

class Robot:
    def __init__(self, ROBOT_BASE_POINT, scale):
        self.scale = scale
        self.basePt = ROBOT_BASE_POINT
        self.main_track = MainTrack(self.basePt, scale)
        self.main_arm = MainArm(self.main_track.otherPt, scale)
        self.secondary_arm = SecondaryArm(self.main_arm.otherPt, scale, angle=45)
        self.carriage1 = Carriage(self.secondary_arm.otherPt1, scale)
        self.carriage2 = Carriage(self.secondary_arm.otherPt2, scale)

        self.follow_pt1 = Point(0, 0)
        self.follow_pt2 = Point(0, 0)

    def __repr__(self):
        ret = ""
        ret += self.main_track.__repr__()
        ret += self.main_arm.__repr__()
        ret += self.secondary_arm.__repr__()
        ret += self.carriage2.__repr__()
        ret += self.carriage1.__repr__()
        return ret

    def moveTo(self, pt2, pt1):
        self.carriage1.follow(pt1)
        self.carriage2.follow(pt2)
        self.secondary_arm.follow(pt1, pt2)
        self.main_arm.follow(self.secondary_arm.basePt, self.secondary_arm.angle)
        self.main_track.follow(self.main_arm.basePt)

        self.main_track.moveBase(self.basePt)
        self.main_arm.moveBase(self.main_track.otherPt)
        self.secondary_arm.moveBase(self.main_arm.otherPt, self.main_arm.angle)
        self.carriage1.moveBase(self.secondary_arm.otherPt1, self.secondary_arm.angle)
        self.carriage2.moveBase(self.secondary_arm.otherPt2, self.secondary_arm.angle)

    def followPath(self, path1, path2, execution_time):
        self.follow_pt1 = path1[0]
        self.follow_pt2 = path2[0]

        self.follow1_index = 0
        self.follow2_index = 0

        self.path1 = path1
        self.path2 = path2

        self.dt1 = []
        for i in range(0, len(path1)-1):
            self.dt1 += [(path1[i + 1] - path1[i]).mag()]
        self.dt1 = np.divide(np.multiply(self.dt1, execution_time), np.sum(self.dt1))

        self.dt2 = []
        for i in range(0, len(path2)-1):
            self.dt2 += [(path2[i + 1] - path2[i]).mag()]
        self.dt2 = np.divide(np.multiply(self.dt2, execution_time), np.sum(self.dt2))

    def update(self):
        flag1 = self.follow_pt1.update()
        flag2 = self.follow_pt2.update()

        if not flag1:
            self.follow1_index += 1
            if self.follow1_index < len(self.dt1):
                self.follow_pt1.moveTo(self.path1[self.follow1_index+1], self.dt1[self.follow1_index])
        if not flag2:
            self.follow2_index += 1
            if self.follow2_index < len(self.dt2):
                self.follow_pt2.moveTo(self.path2[self.follow2_index+1], self.dt2[self.follow2_index])

        self.moveTo(self.follow_pt1, self.follow_pt2)

    def draw(self, canvas):
        self.main_track.draw(canvas)
        self.main_arm.draw(canvas)
        self.secondary_arm.draw(canvas)
        self.carriage1.draw(canvas, color=(0, 255, 0))
        self.carriage2.draw(canvas, color=(0, 0, 255))

        font = cv2.FONT_HERSHEY_SIMPLEX
        y0, dy = 30, 18
        for i, line in enumerate(self.__repr__().split('\n')):
            y = y0 + i*dy
            try:
                if (line[0] == '\t'):
                    cv2.putText(canvas, line[1:], (25, y), font, 0.6, (150, 150, 0))
                else:
                    cv2.putText(canvas, line, (15, y), font, 0.6, (255, 255, 0))
            except:
                cv2.putText(canvas, line, (15, y), font, 0.6, (255, 255, 0))