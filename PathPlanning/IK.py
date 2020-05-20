import numpy as np 
import cv2 
import math 
from Robot import Robot
from Point import Point
<<<<<<< HEAD

canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)
otherPt = Point(500, 500)

model = Robot(Point(300, 500), 200)

# out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output8.mp4', 0x7634706d, 60, (1000,1000))

def mouseEvent(event, x, y, flags, param):
    global canvas, otherPt
    if event==cv2.EVENT_MOUSEMOVE:
        canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)

        model.moveTo(otherPt, Point(x, y))
        model.draw(canvas)
        cv2.circle(canvas, otherPt.toTuple(), 3, (255, 255, 255))

        # out.write(canvas)
    elif event==cv2.EVENT_LBUTTONDOWN:
        otherPt = Point(x, y)

def main():
    global canvas
=======
import time

canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)

model = Robot(Point(300, 500), 200)
points1 = [Point(497, 261, angle=0), Point(498, 327, angle=15), Point(496, 406, angle=30), Point(498, 466, angle=45), Point(500, 517, angle=60), Point(561, 591, angle=75), Point(622, 665, angle=90)]
points2 = [Point(501, 504, angle=180), Point(500, 546, angle=165), Point(460, 600, angle=150), Point(417, 632, angle=135), Point(368, 647, angle=120), Point(339, 659, angle=105), Point(282, 665, angle=90)]
i = 0
pt1 = Point(497, 261, angle=0)
pt2 = Point(501, 504, angle=180)
times = []

# out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output10.mp4', 0x7634706d, 120, (1000,1000))

def mouseEvent(event, x, y, flags, param):
    global canvas, i, pt1, pt2, points1, points2, times
    if event==cv2.EVENT_MOUSEMOVE:
        start = time.time()

        pt2.update()
        if not pt1.update():
            if i < len(points1):
                pt1.moveTo(points1[i], 50)
                pt2.moveTo(points2[i], 50)
                i+= 1
            else:
                pt1.moveTo(points1[0], 150)
                pt2.moveTo(points2[0], 150)
                i = 1

        model.moveTo(pt1, pt2)

        times += [time.time() - start]

        canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)
        model.draw(canvas)

        for j in range(0, len(points1)):
            points1[j].draw(canvas)
            points2[j].draw(canvas, color=(0, 255, 255))

        # out.write(canvas)
    elif event==cv2.EVENT_LBUTTONDOWN:
        pass

def main():
    global canvas, points1, points2, times
>>>>>>> path_planning2
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

<<<<<<< HEAD
=======
    print("Average time", np.average(times)) 

>>>>>>> path_planning2
if __name__=="__main__":
    main()
    # out.release()