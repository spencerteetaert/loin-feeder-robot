from Point import Point
from MainTrack import MainTrack
from MainArm import MainArm 
from SecondaryArm import SecondaryArm

########################
### Robot Parameters ###
########################

ROBOT_BASE_POINT = Point(300, 500)

########################

class Robot:
    def __init__(self):
        self.basePt = ROBOT_BASE_POINT
        self.main_track = MainTrack(self.basePt, 100)
        self.main_arm = MainArm(self.main_track.otherPt, 200)
        self.secondary_arm = SecondaryArm(self.main_arm.otherPt, 150, 100, angle=45)

    def moveTo(self, pt1, pt2):
        self.secondary_arm.follow(pt1, pt2)
        self.main_arm.follow(self.secondary_arm.basePt)
        self.main_track.follow(self.main_arm.basePt)

        self.main_track.moveBase(self.basePt)
        self.main_arm.moveBase(self.main_track.otherPt)
        self.secondary_arm.moveBase(self.main_arm.otherPt)
        
    def draw(self, canvas):
        self.main_track.draw(canvas)
        self.main_arm.draw(canvas)
        self.secondary_arm.draw(canvas)
        