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
from .. import global_parameters

random.seed(12345)

THRESHOLD = 255

def get_bbox(img, threshold=THRESHOLD, lower_mask=global_parameters.LOWER_MASK, upper_mask=global_parameters.UPPER_MASK, source="Image"):
    '''
    Returns bounding polygons for the all identified middles 
    in the image
    '''
    temp = gen_mask(img, lower_mask=lower_mask, upper_mask=upper_mask)
    bound_poly = thresh_callback(threshold, temp)

    return bound_poly, temp

def gen_mask(img, lower_mask=global_parameters.LOWER_MASK, upper_mask=global_parameters.UPPER_MASK, bitwise_and=False, process=True):
    '''
    Masks input img based off HSV colour ranges provided 
    '''
    iH, iW, _ = img.shape

    #Masks colour ranges provided
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_mask, upper_mask)

    cv2.bitwise_not(mask)

    if process:
        # Expands border to ensure when dilating shape is maintained 
        mask = cv2.copyMakeBorder(mask, 0, 0, 15, 15, cv2.BORDER_CONSTANT, value=0)

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
        return cv2.bitwise_and(img, img, mask=refined)
    return refined[:,16:-16]

def thresh_callback(val, img):
    '''
    Returns single convex hull of all contours of img 

    '''
    threshold = val #Threshold value for contours 
    canny_output = cv2.Canny(img, threshold, threshold * 2)
    
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if (len(contours) == 0):
        return 0

    hulls = [cv2.convexHull(contours[i]) for i in range(0, len(contours)) if cv2.contourArea(cv2.convexHull(contours[i])) > global_parameters.MINIMUM_AREA]

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