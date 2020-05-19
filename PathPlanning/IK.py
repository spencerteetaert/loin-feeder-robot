import numpy as np 
import cv2 
import math 
from Robot import Robot
from Point import Point

canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)
otherPt = Point(500, 500)

model = Robot(Point(300, 500), 243)

# out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output8.mp4', 0x7634706d, 60, (1000,1000))

def mouseEvent(event, x, y, flags, param):
    global canvas, otherPt
    if event==cv2.EVENT_MOUSEMOVE:
        canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)

        model.moveTo(otherPt, Point(x, y))
        model.draw(canvas)
        # cv2.circle(canvas, otherPt.toTuple(), 3, (255, 255, 255))

        # out.write(canvas)
    elif event==cv2.EVENT_LBUTTONDOWN:
        otherPt = Point(x, y)

def main():
    global canvas
    model.draw(canvas)
    win_name = "Inverse Kinematics"
    cv2.namedWindow(win_name)
    cv2.moveWindow(win_name, 500, 500)
    cv2.setMouseCallback(win_name, mouseEvent)

    while (1):
        cv2.imshow(win_name, canvas)

        k = cv2.waitKey(33) & 0xFF
        if k == ord('q'):
            break

if __name__=="__main__":
    main()
    # out.release()