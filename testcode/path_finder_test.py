import time

import numpy as np 
import cv2

from context import sample
from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample import GlobalParameters

from sample.PathPlanning.Path import PathFinder

path = []
pf = PathFinder()
sp = Point(400,200, angle=0)
ep = Point(0, 0, angle=0)
canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)

def on_mouse(event, pX, pY, flags, param):
    global path, pf, sp, canvas
    if event == cv2.EVENT_MOUSEMOVE:
        ep = Point(pX, pY, angle=215)
        path = pf(sp, ep, 30)
        
        canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)
        for i in range(0, len(GlobalParameters.SAFE_ENVIRONMENT)):
            cv2.line(canvas, (GlobalParameters.SAFE_ENVIRONMENT[i][0][0], GlobalParameters.SAFE_ENVIRONMENT[i][0][1]), (GlobalParameters.SAFE_ENVIRONMENT[i][1][0], GlobalParameters.SAFE_ENVIRONMENT[i][1][1]), (50, 50, 50))
        for i in range(1, len(path)-1):
            path[i].draw(canvas, color=(255, 255, 255))

        sp.draw(canvas, color=(0, 255, 0))
        ep.draw(canvas, color=(0, 0, 255))


def main():
    global path, sp, ep, canvas

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    while True:
        cv2.imshow(win, canvas)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break

main()