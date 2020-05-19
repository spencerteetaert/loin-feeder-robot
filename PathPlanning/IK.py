import numpy as np 
import cv2 
import math 
from Robot import Robot
from Point import Point

canvas = np.zeros([1000, 1000, 3])
otherPt = Point(500, 500)

model = Robot()

def mouseEvent(event, x, y, flags, param):
    global canvas, otherPt
    if event==cv2.EVENT_MOUSEMOVE:
        canvas = np.zeros([1000, 1000, 3])

        model.moveTo(otherPt, Point(x, y))
        model.draw(canvas)
        cv2.circle(canvas, otherPt.toTuple(), 3, (255, 255, 255))
    elif event==cv2.EVENT_LBUTTONDOWN:
        otherPt = Point(x, y)

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