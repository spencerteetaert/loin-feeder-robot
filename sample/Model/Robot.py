from threading import Thread
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

        dt1 = []
        for i in range(0, len(path1)-1):
            dt1 += [(path1[i + 1] - path1[i]).mag()]
        np.divide(dt1 * execution_time, np.sum(dt1))

        dt2 = []
        for i in range(0, len(path2)-1):
            dt2 += [(path2[i + 1] - path2[i]).mag()]
        np.divide(dt2 * execution_time, np.sum(dt2))

        follow1 = Thread(target=self.auto_step, args=(path1, dt1, 1))
        follow2 = Thread(target=self.auto_step, args=(path2, dt2, 2))
        
        follow1.start()
        follow2.start()
        # Start two threads, one to update each follow point 

    def auto_step(self, pts, dts, number):
        start = time.time()
        i = 0
        while i < len(dts):
            if (time.time() - start) % 0.0333 == 0:
                if number == 1:
                    flag = self.follow_pt1.update()
                    if flag == False:
                        self.follow_pt1.moveTo(pts[i], dts[i])
                        i += 1
                elif number == 2:
                    flag = self.follow_pt2.update()
                    if flag == False:
                        self.follow_pt2.moveTo(pts[i], dts[i])
                        i += 1

    def draw(self, canvas):
        self.main_track.draw(canvas)
        self.main_arm.draw(canvas)
        self.secondary_arm.draw(canvas)
        self.carriage1.draw(canvas)
        self.carriage2.draw(canvas)

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

    def __repr__(self):
        ret = ""
        ret += self.main_track.__repr__()
        ret += self.main_arm.__repr__()
        ret += self.secondary_arm.__repr__()
        ret += self.carriage2.__repr__()
        ret += self.carriage1.__repr__()
        return ret
