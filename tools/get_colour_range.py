import threading as threading
import math

import cv2
import numpy as np

class Point(object):
    def __init__(self, x=0,y=0):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

def mouse_event(event, pX, pY, flags, param):
    global img, points

    if event == cv2.EVENT_LBUTTONUP:
        cv2.rectangle(img, (pX - 2, pY - 2), (pX + 2, pY + 2), (0, 255, 200), -1)
        points += [[pX, pY]]

def display():
    global img, i, points

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouse_event)
    while True:
        cv2.imshow("Image", img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('n'):
            cv2.destroyWindow("Image")
            break
        elif k == ord('d'):
            points = points[:-1]

hB = [180, 0]
sB = [255, 0]
vB = [255, 0]

for i in range(0, 10):
    img = cv2.imread(r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\test"+str(i)+".png")
    # temp = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_NV21)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    img_h, img_w = img.shape[:2]
    points = []

    # Creates a new thread with target function 
    t = threading.Thread(target = display, args=[])
    
    # Sets priority level of thread. Daemon threads do not stop the main
    # program from running and are closed when main is
    t.daemon = True

    #Starts thread
    t.start()
    #Pauses here until thread is completed
    t.join()

    if len(points) > 2:
        contour = np.array(points).reshape((-1, 1, 2)).astype(np.int32)
        temp1 = np.array([[0 if cv2.pointPolygonTest(contour, (x,y), False) != 1 else 255 for x in range(0, img.shape[1])] for y in range(0, img.shape[0])], dtype=np.int8)
        temp2 = cv2.bitwise_not(temp1)
        temp2 = cv2.bitwise_and(hsv, hsv, mask=temp2)
    

        h_vals = [temp2[y][x][0] for y in range(0, img_h) for x in range(0, img_w) if not (temp2[y][x] == np.array([0,0,0])).all()]
        s_vals = [temp2[y][x][1] for y in range(0, img_h) for x in range(0, img_w) if not (temp2[y][x] == np.array([0,0,0])).all()]
        v_vals = [temp2[y][x][2] for y in range(0, img_h) for x in range(0, img_w) if not (temp2[y][x] == np.array([0,0,0])).all()]

        h_vals.sort()
        s_vals.sort()
        v_vals.sort()

        h_bounds = [h_vals[math.floor(len(h_vals)*0.1)], h_vals[math.ceil(len(h_vals)*0.9)]]
        s_bounds = [s_vals[math.floor(len(s_vals)*0.1)], s_vals[math.ceil(len(s_vals)*0.9)]]
        v_bounds = [v_vals[math.floor(len(v_vals)*0.1)], v_vals[math.ceil(len(v_vals)*0.9)]]

        if h_bounds[0] < hB[0]:
            hB[0] = h_bounds[0]
        if s_bounds[0] < sB[0]:
            sB[0] = s_bounds[0]
        if v_bounds[0] < vB[0]:
            vB[0] = v_bounds[0]

        if h_bounds[1] > hB[1]:
            hB[1] = h_bounds[1]
        if s_bounds[1] > sB[1]:
            sB[1] = s_bounds[1]
        if v_bounds[1] > vB[1]:
            vB[1] = v_bounds[1]

        # cv2.drawContours(temp2, [contour], 0, (31, 255, 49), 2)
        # cv2.imshow("Image",temp2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
    print(hB, sB, vB)

print("Final",hB, sB, vB)