import numpy as np 
import cv2

from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample import GlobalParameters

from sample.PathPlanning.Path import Path

env = [[[440, 190], [440, 730]], [[145, 735], [665, 735]]]

PathFinder = Path(env)
path = PathFinder(Point(400,200), Point(670, 740), 50)

canvas = np.zeros([1000, 1000, 3], dtype=np.uint8)

win = "Window"
cv2.namedWindow(win)

for i in range(0, len(path)):
    path[i].draw(canvas)

cv2.imshow(win, canvas)

cv2.waitKey(0)