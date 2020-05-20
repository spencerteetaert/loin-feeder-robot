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

font = cv2.FONT_HERSHEY_SIMPLEX
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

    # ret = cv2.copyMakeBorder(ret, 300, 300, 0, 0, cv2.BORDER_CONSTANT, value=0)

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
        mask = cv2.copyMakeBorder(mask, 0, 0, 0, 300, cv2.BORDER_CONSTANT, value=0)

        kernel = np.ones([round(iW*0.013),round(iH*0.013)])
        refined = cv2.dilate(mask, kernel)

        kernel = np.ones([round(iW*0.02),round(iH*0.02)])
        refined = cv2.erode(refined, kernel)

        kernel = np.ones([round(iW*0.08),round(iH*0.08)])
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
    return refined

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

def draw_results(img, boundPolys, source, meat=0, extra_data=""):
    drawing = img.copy()

    try:
        for i in range(0, len(boundPolys)):
            #Draws convex hull
            cv2.drawContours(drawing, boundPolys, i, (31, 255, 49), 2)
            y0, dy = 30, 21
            for i, line in enumerate(extra_data.split('\n')):
                y = y0 + i*dy
                cv2.putText(drawing, line, (10, y), font, 0.7, (255, 255, 0))

            if meat != 0:
                #Draws identified lines of interest
                line_pts = meat.get_lines()

                #Red - Loin
                cv2.line(drawing, (line_pts[0][0][0],line_pts[0][0][1]), (line_pts[0][1][0],line_pts[0][1][1]), (0, 0, 255), thickness=2)
                #Yellow - Shoulder
                # cv2.line(drawing, (line_pts[1][0][0],line_pts[1][0][1]), (line_pts[1][1][0],line_pts[1][1][1]), (0, 255, 255), thickness=2)
                #Blue - Ham
                # cv2.line(drawing, (line_pts[2][0][0],line_pts[2][0][1]), (line_pts[2][1][0],line_pts[2][1][1]), (255, 0, 0), thickness=2)
                #Magenta - Belly 
                cv2.line(drawing, (line_pts[3][0][0],line_pts[3][0][1]), (line_pts[3][1][0],line_pts[3][1][1]), (255, 0, 255), thickness=2)
                #White - Cut 
                cv2.line(drawing, (line_pts[4][0][0],line_pts[4][0][1]), (line_pts[4][1][0],line_pts[4][1][1]), (100, 205, 205), thickness=2)
    except TypeError as err:
        print("Error: {0}".format(err))
        # raise

    cv2.imshow(source, drawing)

    return drawing