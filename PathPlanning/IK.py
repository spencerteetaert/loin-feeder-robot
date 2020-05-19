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
    def angle(self):
        if self.x < 0:
            return math.degrees(math.atan((-1*self.y)/self.x)) + 180
        elif self.x == 0:
            if self.y < 0:
                return 90
            else:
                return -90
        else:
            return math.degrees(math.atan((-1*self.y)/self.x))

    def toTuple(self):
        return (round(self.x), round(self.y))

class MainArm:
    def __init__(self, pt, length=100, angle=0):
        self.basePt = pt
        self.length = length
        self.min_length = 50
        self.max_length = 75
        self.angle = angle 
        self.otherPt = self.getOtherPt()

    def __repr__(self):
        return "MainArm with:\n\tBase (" + str(self.basePt.x) + ", " + str(self.basePt.y) + ")\n\tLength " + str(self.length) + "\n\tAngle " + str(self.angle) + "°"

    def refresh(self):
        self.angle = (self.otherPt - self.basePt).angle()

    def getOtherPt(self):
        return Point(round(self.basePt.x + self.length * math.cos(math.radians(self.angle))), round(self.basePt.y - self.length * math.sin(math.radians(self.angle))))

    def draw(self, canvas):
        cv2.line(canvas, self.basePt.toTuple(), self.otherPt.toTuple(), (255, 255, 255)) 
        cv2.circle(canvas, self.basePt.toTuple(), 3, (255, 255, 255))
    
    def follow(self, pt):
        dr = pt - self.basePt
        if dr.mag() <= self.min_length:
            self.length = self.min_length
        elif dr.mag() <= self.max_length:
            self.length = dr.mag()
        else:
            self.length = self.max_length

        self.otherPt = pt
        self.basePt = self.otherPt - dr.norm() * self.length

    def moveBase(self, pt):
        self.refresh()
        self.basePt = pt
        self.otherPt = self.getOtherPt()

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
        self.main_arm = MainArm(Point(500, 500), 200) 
        self.secondary_arm = SecondayArm(self.main_arm.otherPt, 150, 100, angle=45)

count = 5
s = []
for i in range(0, count):
    s += [MainArm(Point(500, 500), 50)]

# s2 = SecondayArm(s1.otherPt, 150, 100, angle=45)
canvas = np.zeros([1000, 1000, 3])

def mouseEvent(event, x, y, flags, param):
    global s, canvas
    if event==cv2.EVENT_MOUSEMOVE:
        s[0].follow(Point(x, y))
        for i in range(1, count):
            s[i].follow(s[i-1].basePt)

        s[count-1].moveBase(Point(500, 500))
        for i in range(count-2, -1, -1):
            s[i].moveBase(s[i+1].otherPt)


        # s2.basePt = Point(x, y)

        # s2.refresh()

        canvas = np.zeros([1000, 1000, 3])

        for i in range(0, count):
            s[i].draw(canvas)

        # s2.draw(canvas)

def main():
    global canvas
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