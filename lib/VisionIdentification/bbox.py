'''
Altered from bbox example on opencv documentation site 
https://docs.opencv.org/3.4/da/d0c/tutorial_bounding_rects_circles.html 
'''

import numpy as np
import cv2
import argparse 
import random as r 
import image_sizing as imgsz 

r.seed(12345)

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\left middle.jpg"
THRESHOLD = 120

def get_bbox(img, threshold=THRESHOLD, draw=False):
    '''
    Returns single bounding box for the given middle image
    A larger threshold value will result in larger bbox
    '''
    temp = preprocess(img)
    boundRect, contours_poly, canny_output, contours = thresh_callback(threshold, temp)
    boundRect = filter_outliers(boundRect)
    boundRect = find_large_bbox(boundRect)

    if draw:
        draw_results(temp, canny_output, contours_poly, contours, boundRect)

    return boundRect

def preprocess(img):
    '''
    Crops image
    Scales image
    Filters out red channel (makes contour finding easier for meats for bbox later)
    Grayscales image to reduce computation time
    '''
    ret = imgsz.crop(img)
    ret = imgsz.scale(ret)

    # Convert image to gray and blur it -- removes noise
    ret[:,:,2] = np.zeros([ret.shape[0], ret.shape[1]])
    ret = cv2.cvtColor(ret, cv2.COLOR_BGR2GRAY)
    # ret = cv2.blur(ret, (3,3))
    return ret 

def thresh_callback(val, temp):
    '''
    Finds all image contours within a given threshold. 

    '''
    threshold = val #Threshold value for contours 
    canny_output = cv2.Canny(temp, threshold, threshold * 2)
    
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
    for i, c in enumerate(contours):
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])

    return boundRect, contours_poly, canny_output, contours
    
def filter_outliers(boundRect, m=1):
    '''
    Filters out all bounding boxes with center X or Y coordinates further than
    m standard deviations from average. 
    '''
    centersX = [int(boundRect[i][0]+boundRect[i][2]/2) for i in range(0, len(boundRect))]
    centersY = [int(boundRect[i][1]+boundRect[i][3]/2) for i in range(0, len(boundRect))]

    avgX, stdX = np.average(centersX), np.std(centersX)
    avgY, stdY = np.average(centersY), np.std(centersY)

    filt = []

    for i in range(0, len(boundRect)):
        if (abs(centersX[i] - avgX) < stdX * m):
            filt+=[True]
        elif (abs(centersY[i] - avgY) < stdY * m):
            filt+=[True]
        else:
            filt+=[False]

    ret = [boundRect[i] for i in range(0, len(boundRect)) if filt[i]==True]
    return ret

def find_large_bbox(boundRects):
    '''
    Given a list of small bboxes, finds the smallest bbox that contains
    all small bboxes.
    '''
    minX = 100000
    maxX = 0
    minY = 100000
    maxY = 0

    for i in range(0, len(boundRects)):
        if boundRects[i][0] < minX:
            minX = boundRects[i][0]
        if boundRects[i][1] < minY:
            minY = boundRects[i][1]
        if boundRects[i][0]+boundRects[i][2] > maxX:
            maxX = boundRects[i][0]+boundRects[i][2]
        if boundRects[i][1]+boundRects[i][3] > maxY:
            maxY = boundRects[i][1]+boundRects[i][3]
    
    return [(minX, minY, maxX - minX, maxY - minY)]

def draw_results(img, canny_output, contours_poly, contours, boundRect):
    drawing = img

    for i in range(len(boundRect)):
        color = (r.randint(0,256), r.randint(0,256), r.randint(0,256))
        cv2.rectangle(drawing, (int(boundRect[i][0]), int(boundRect[i][1])), 
          (int(boundRect[i][0]+boundRect[i][2]), int(boundRect[i][1]+boundRect[i][3])), color, 2)
    
    cv2.imshow('Bbox', drawing)
    cv2.waitKey(0)


def main(input_path=DATA_PATH):
    og = cv2.imread(input_path)
    get_bbox(og, draw=True)

if __name__=="__main__":
    main() 