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

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\Output Data 07.05.2020 07-31-40\L"
THRESHOLD = 200

#Threshold values for typical meat colours (lean and fat)
LOWER_MASK = np.array([0, 51, 51])
UPPER_MASK = np.array([15, 204, 255])

def get_bbox(img, threshold=THRESHOLD, draw=False, lower_mask=LOWER_MASK, upper_mask=UPPER_MASK):
    '''
    Returns single bounding polygon for the given middle image
    A larger threshold value will result in larger bbox
    '''
    img = preprocess(img)
    #Masks meat 
    temp = gen_mask(img, lower_mask, upper_mask)

    #Add border to ensure full hull is created 
    temp = cv2.copyMakeBorder(temp, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    img = cv2.copyMakeBorder(img, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
    bound_poly = thresh_callback(threshold, temp)

    if draw:
        draw_results(img, bound_poly, "single")
        cv2.waitKey(0)

    return bound_poly

def preprocess(img):
    '''
    Crops image
    Scales image
    Filters out red channel (makes contour finding easier for meats for bbox later)
    Grayscales image to reduce computation time
    '''
    ret = imgsz.crop(img)
    ret = imgsz.scale(ret)

    return ret 

def gen_mask(img, lower_mask, upper_mask):
    '''
    Masks input img based off HSV colour ranges provided 
    '''
    ret = img.copy()

    #Masks colour ranges provided
    hsv = cv2.cvtColor(ret, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_mask, upper_mask)
    cv2.bitwise_not(mask)
    ret = cv2.bitwise_and(ret, ret, mask=mask)

    # First erode and dilate to remove small pieces and noise
    kernel = np.ones([15,15])
    refined = cv2.morphologyEx(ret, cv2.MORPH_OPEN, kernel)

    #Then dilate and erode to remove holes 
    kernel = np.ones([25,25])
    refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)

    return refined

def thresh_callback(val, img):
    '''
    Returns single convex hull of all contours of img 

    '''
    threshold = val #Threshold value for contours 
    canny_output = cv2.Canny(img, threshold, threshold * 2)
    
    contours, _ = cv2.findContours(canny_output, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = np.concatenate(contours)
    hull = cv2.convexHull(contours)

    return [hull]
    
def filter_outliers(c, m=1):
    '''
    Filters out all bounding boxes with center X or Y coordinates further than
    m standard deviations from average. 
    '''

    M = [cv2.moments(c[i]) for i in range(0, len(c))]
    print(M)
    centersX = [int(M[i]["m10"] / M[i]["m00"]) for i in range(0, len(M))]
    centersY = [int(M[i]["m01"] / M[i]["m00"]) for i in range(0, len(M))]

    avgX, stdX = np.average(centersX), np.std(centersX)
    avgY, stdY = np.average(centersY), np.std(centersY)

    filt = []

    for i in range(0, len(c)):
        if (abs(centersX[i] - avgX) < stdX * m):
            filt+=[True]
        elif (abs(centersY[i] - avgY) < stdY * m):
            filt+=[True]
        else:
            filt+=[False]

    ret = [c[i] for i in range(0, len(c)) if filt[i]==True]
    return ret

def draw_results(img, boundRect, name):
    drawing = img.copy()

    color = (255, 255, 255)
    cv2.drawContours(drawing, boundRect, 0, color)
    cv2.imshow(name, drawing)

def main(input_path=DATA_PATH):
    for i in range(228, 300):
        temp = input_path + str(i) + ".png"
        try: 
            og = cv2.imread(temp)
            og.shape
        except:
            continue
        get_bbox(og, draw=True)

if __name__=="__main__":
    main() 