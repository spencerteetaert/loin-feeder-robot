from Point import Point
from MainTrack import MainTrack
from MainArm import MainArm 
from SecondaryArm import SecondaryArm
from Carriage import Carriage
import cv2

class Robot:
    def __init__(self, ROBOT_BASE_POINT):
        self.basePt = ROBOT_BASE_POINT
        self.main_track = MainTrack(self.basePt, 100)
        self.main_arm = MainArm(self.main_track.otherPt, 200)
        self.secondary_arm = SecondaryArm(self.main_arm.otherPt, 150, 100, angle=45)
        self.carriage1 = Carriage(self.secondary_arm.otherPt1)
        self.carriage2 = Carriage(self.secondary_arm.otherPt2)

    def moveTo(self, pt1, pt2):
        self.secondary_arm.follow(pt1, pt2)
        self.main_arm.follow(self.secondary_arm.basePt)
        self.main_track.follow(self.main_arm.basePt)

        self.main_track.moveBase(self.basePt)
        self.main_arm.moveBase(self.main_track.otherPt)
        self.secondary_arm.moveBase(self.main_arm.otherPt)
        self.carriage1.moveBase(self.secondary_arm.otherPt1)
        self.carriage2.moveBase(self.secondary_arm.otherPt2)

    def draw(self, canvas):
        self.main_track.draw(canvas)
        self.main_arm.draw(canvas)
        self.secondary_arm.draw(canvas)
        self.carriage1.draw(canvas)
        self.carriage2.draw(canvas)

        font = cv2.FONT_HERSHEY_SIMPLEX
        y0, dy = 30, 21
        for i, line in enumerate(self.__repr__().split('\n')):
            y = y0 + i*dy
            try:
                if (line[0] == '\t'):
                    cv2.putText(canvas, line[1:], (25, y), font, 0.7, (0, 100, 255))
                else:
                    cv2.putText(canvas, line, (15, y), font, 0.7, (255, 255, 0))
            except:
                cv2.putText(canvas, line, (15, y), font, 0.7, (255, 255, 0))

    def __repr__(self):
        ret = ""
        ret += self.main_track.__repr__()
        ret += self.main_arm.__repr__()
        ret += self.secondary_arm.__repr__()
        return ret
