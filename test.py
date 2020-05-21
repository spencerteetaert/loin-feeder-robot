import time

import numpy as np 
import cv2

from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample import GlobalParameters

from sample.PathPlanning.Path import PathFinder

env = [[[440, 190], [440, 730]], [[145, 735], [665, 735]], [[440, 600], [300, 735]], [[440, 600], [580, 735]]]

pf = PathFinder(env)

sp = Point(400,200, angle=0)
ep = Point(700, 740, angle=270)

start = time.time()
path = pf(sp, ep, 50)
print("Runtime", time.time() - start)

canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)

win = "Window"
cv2.namedWindow(win)

for i in range(0, len(env)):
    cv2.line(canvas, (env[i][0][0], env[i][0][1]), (env[i][1][0], env[i][1][1]), (50, 50, 50))
for i in range(1, len(path)-1):
    path[i].draw(canvas, color=(255, 255, 255))

sp.draw(canvas, color=(0, 255, 0))
ep.draw(canvas, color=(0, 0, 255))

cv2.imshow(win, canvas)

cv2.waitKey(0)