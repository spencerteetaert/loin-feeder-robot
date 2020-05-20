import numpy as np 
import cv2 
import math 
from Robot import Robot
from Point import Point
import time

canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)
pt1 = Point(497, 261)
pt2 = Point(501, 504)

model = Robot(Point(300, 500), 200)
points1 = [Point(498, 327, angle=50), Point(496, 406, angle=100), Point(498, 466), Point(500, 517), Point(510, 562), Point(543, 614), Point(582, 640), Point(622, 665)]
points2 = [Point(500, 546), Point(460, 600), Point(417, 632), Point(368, 647), Point(339, 659), Point(316, 662), Point(297, 666), Point(282, 665)]
i = 0

times = []

# out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output8.mp4', 0x7634706d, 60, (1000,1000))

def mouseEvent(event, x, y, flags, param):
    global canvas, pt1, pt2, i, points1, points2, times
    if event==cv2.EVENT_MOUSEMOVE:

        start = time.time()

        pt2.update()
        if not pt1.update():
            if i < len(points1):
                pt1.moveTo(points1[i], 50)
                pt2.moveTo(points2[i], 50)
                i+= 1
            else:
                i = 0

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

    print(points1)
    print(points2)
    print("Avaerage time", np.average(times)) 

if __name__=="__main__":
    main()
    # out.release()