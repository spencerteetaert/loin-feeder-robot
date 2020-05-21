'''
Altered from bbox example on opencv documentation site 
https://docs.opencv.org/3.4/da/d0c/tutorial_bounding_rects_circles.html 
'''
import time
import argparse 
import random
import time

import numpy as np
import cv2

from . import image_sizing
from .. import GlobalParameters

random.seed(12345)

THRESHOLD = 255

def get_bbox(img, threshold=THRESHOLD, draw=False, lower_mask=GlobalParameters.LOWER_MASK, upper_mask=GlobalParameters.UPPER_MASK, source="Image"):
    '''
    Returns single bounding polygon for the given middle image
    A larger threshold value will result in larger bbox
    '''
    # img = preprocess(img)
    #Masks meat 
    temp = gen_mask(img, lower_mask=lower_mask, upper_mask=upper_mask)

    #Add border to ensure full hull is created 
    temp = cv2.copyMakeBorder(temp, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    bound_poly = thresh_callback(threshold, temp)

    drawing = 0

    if draw:
        drawing = draw_results(temp, bound_poly, source)
        # cv2.imshow(source, drawing)

    return bound_poly, temp, drawing

def preprocess(img):
    '''
    Crops image
    Scales image
    Filters out red channel (makes contour finding easier for meats for bbox later)
    Grayscales image to reduce computation time
    '''
    ret = img.copy()
    # ret = image_sizing.crop(ret)
    ret = image_sizing.scale(ret)

    ret = cv2.copyMakeBorder(ret, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

    return ret 

def gen_mask(img, lower_mask=GlobalParameters.LOWER_MASK, upper_mask=GlobalParameters.UPPER_MASK, bitwise_and=False, process=True):
    '''
    Masks input img based off HSV colour ranges provided 
    '''
    iH, iW, _ = img.shape
    ret = img.copy()

    #Masks colour ranges provided
    hsv = cv2.cvtColor(ret, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_mask, upper_mask)

    # t1 = cv2.inRange(hsv, temp1, temp2)
    # t2 = cv2.inRange(hsv, temp3, temp4)

    # mask = t1 + t2

    cv2.bitwise_not(mask)

    if process:
        mask = cv2.copyMakeBorder(mask, 0, 0, 100, 100, cv2.BORDER_CONSTANT, value=0)

        kernel = np.ones([round(iW*0.013),round(iH*0.013)])
        refined = cv2.dilate(mask, kernel)

        kernel = np.ones([round(iW*0.02),round(iH*0.02)])
        refined = cv2.erode(refined, kernel)

        kernel = np.ones([round(iW*0.035),round(iH*0.035)])
        refined = cv2.dilate(refined, kernel)
        refined = cv2.erode(refined, kernel)

        # kernel = np.ones([round(iW*0.08),round(iH*0.08)])
        # refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)

        # kernel = np.ones([round(iW*0.1),round(iH*0.1)])
        # refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)
    else:
        refined = mask

    if bitwise_and:
        return cv2.bitwise_and(ret, ret, mask=refined)
    return refined[:,101:-101]

def thresh_callback(val, img):
    '''
    Returns single convex hull of all contours of img 

    '''
    threshold = val #Threshold value for contours 
    canny_output = cv2.Canny(img, threshold, threshold * 2)
    
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if (len(contours) == 0):
        return 0

    # contours = np.concatenate(contours)
    hulls = [cv2.convexHull(contours[i]) for i in range(0, len(contours)) if cv2.contourArea(cv2.convexHull(contours[i])) > GlobalParameters.MINIMUM_AREA]

    if (len(hulls) == 0):
        return 0

    # Removes hulls that are contained within others. This allows for multiple pieces of meat to be detected
    filt = []
    for i in range(0, len(hulls)):
        flag = True
        for j in range(0, len(hulls)):
            if (cv2.pointPolygonTest(hulls[j], (hulls[i][0][0][0], hulls[i][0][0][1]), measureDist=False) == 1):
                flag = False
            
        filt += [flag]

    ret = [hulls[i] for i in range(0, len(hulls)) if filt[i]==True]

    return ret