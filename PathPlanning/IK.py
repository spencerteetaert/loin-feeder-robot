import numpy as np 
import cv2 
import math 

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "Point (" + str(self.x) + ", " + str(self.y) + ")"

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)
    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)
    def __mul__(self, factor):
        return Point(self.x * factor, self.y * factor)
    def __truediv__(self, factor):
        return Point(self.x / factor, self.y / factor)
    def __floordiv__(self, factor):
        return Point(self.x // factor, self.y // factor)

    def mag(self):
        return (self.x**2 + self.y**2)**0.5
    def norm(self):
        return Point(self.x / self.mag(), self.y / self.mag())

    def toTuple(self):
        return (round(self.x), round(self.y))

class MainArm:
    def __init__(self, pt, length=100, angle=0):
        self.basePt = pt
        self.length = length
        self.min_length = 50
        self.max_length = 300
        self.angle = angle 
        self.refresh()

    def __repr__(self):
        return "MainArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength " + str(self.length) + "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.otherPt = self.getotherPt()

    def getotherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.basePt.toTuple(), self.otherPt.toTuple(), (255, 255, 255)) 
        cv2.circle(canvas, self.basePt.toTuple(), 3, (255, 255, 255))
    
    def follow(self, x, y):
        dr = Point(x, y) - self.basePt
        if dr.mag() <= self.min_length:
            self.length = self.min_length
        elif dr.mag() <= self.max_length:
            self.length = dr.mag()
        else:
            self.length = self.max_length

        self.otherPt = self.basePt + dr.norm() * self.length

class SecondayArm:
    def __init__(self, pt, length1, length2, angle=0):
        self.basePt = pt
        self.length1 = length1
        self.length2 = length2
        self.angle = angle 
        self.refresh()

    def __repr__(self):
        return "SecondayArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength1 " + str(self.length1) + "\n\tLength2 " + str(self.length2)+ "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.otherPt1 = self.getotherPt1()
        self.otherPt2 = self.getotherPt2()

    def getotherPt1(self):
        return Point(round(self.basePt.x + self.length1 * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length1 * math.sin(math.radians(self.angle))))
    def getotherPt2(self):
        return Point(round(self.basePt.x - self.length2 * math.cos(math.radians(self.angle))), round(self.basePt.y + self.length2 * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.otherPt1.toTuple(), self.otherPt2.toTuple(), (255, 255, 255)) 
        cv2.circle(canvas, self.basePt.toTuple(), 3, (255, 255, 255))

class Robot:
    def __init__(self):
        self.main_arm = MainArm(Point(30, 30), 500) 

s1 = MainArm(Point(500, 500), 200)
s2 = SecondayArm(s1.otherPt, 150, 100, angle=45)
canvas = np.zeros([1000, 1000, 3])

def mouseEvent(event, x, y, flags, param):
    global s1, s2, canvas
    if event==cv2.EVENT_MOUSEMOVE:
        s1.follow(x, y)
        s2.basePt = Point(x, y)

        s2.refresh()

        canvas = np.zeros([1000, 1000, 3])
        s1.draw(canvas)
        s2.draw(canvas)

def main():
    global s1, s2, canvas
    win_name = "Inverse Kinematics"
    cv2.namedWindow(win_name)
    cv2.moveWindow(win_name, 500, 500)
    cv2.setMouseCallback(win_name, mouseEvent)

    while (1):
        cv2.imshow(win_name, canvas)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break

if __name__=="__main__":
    main()