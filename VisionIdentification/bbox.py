'''Altered from bbox example on opencv documentation site 
https://docs.opencv.org/3.4/da/d0c/tutorial_bounding_rects_circles.html 
'''

import numpy as np
import cv2
import argparse 
import random as r 
import image_sizing as imgsz 

r.seed(12345)

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\right middle.jpg"
THRESHOLD = 130

def show(img):
    cv2.imshow("",img)
    cv2.waitKey(0)

def thresh_callback(val, temp):
    threshold = val #Threshold value for contours 
    canny_output = cv2.Canny(temp, threshold, threshold * 2)
    
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])

    return boundRect, contours_poly, canny_output, contours
    
def draw_results(img, canny_output, contours_poly, contours, boundRect):
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    
    for i in range(len(contours)):
        color = (r.randint(0,256), r.randint(0,256), r.randint(0,256))
        cv2.drawContours(drawing, contours_poly, i, color)
        cv2.rectangle(drawing, (int(boundRect[i][0]), int(boundRect[i][1])), \
          (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, 2)
    
    cv2.imshow('Original Image', img)
    cv2.imshow('Bbox', drawing)
    cv2.waitKey(0)

def preprocess(img):
    ret = imgsz.crop(img)
    ret = imgsz.scale(ret)

    # Convert image to gray and blur it -- removes noise
    ret[:,:,2] = np.zeros([ret.shape[0], ret.shape[1]])
    # show(ret)
    ret = cv2.cvtColor(ret, cv2.COLOR_BGR2GRAY)
    # show(ret)
    # ret = cv2.blur(ret, (3,3))
    # show(ret)
    return ret 

def get_bbox(img, threshold=THRESHOLD, draw=False):
    temp = preprocess(img)
    boundRect, contours_poly, canny_output, contours = thresh_callback(threshold, temp)

    if draw:
        draw_results(temp, canny_output, contours_poly, contours, boundRect)
    return boundRect

def main(input_path=DATA_PATH):
    og = cv2.imread(input_path)

    get_bbox(og, draw=True)

if __name__=="__main__":
    main() 

    