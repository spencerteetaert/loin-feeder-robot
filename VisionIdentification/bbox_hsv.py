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
THRESHOLD = 255

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
        drawing = draw_results(img, bound_poly, "single")
        # cv2.waitKey(0)

    return bound_poly, temp, drawing

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
    # ret = cv2.bitwise_and(ret, ret, mask=mask)

    # First erode and dilate to remove small pieces and noise
    kernel = np.ones([15,15])
    refined = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    #Then dilate and erode to remove holes 
    kernel = np.ones([20,20])
    refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)

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
    hulls = [cv2.convexHull(contours[i]) for i in range(0, len(contours))]

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

def draw_results(img, boundPolys, name):
    drawing = img.copy()

    # print(boundPolys)

    color = (31, 255, 49)
    if (boundPolys != 0):
        for i in range(0, len(boundPolys)):
            cv2.drawContours(drawing, boundPolys, i, color, 2)
    # cv2.imshow(name, drawing)
    return drawing

def n(x):
    pass

def main(input_path=DATA_PATH):
    h = [0, 180]
    s = [0, 255]
    v = [0, 255]
    hlow = 0
    hhigh = 15
    slow = 51
    shigh = 204
    vlow = 51
    vhigh = 255
    flag = False

    for i in range(228, 245):
        temp = input_path + str(i) + ".png"
        try: 
            og = cv2.imread(temp)
            og.shape
        except:
            continue
        
        src = 'Source'
        cv2.namedWindow(src)

        cv2.createTrackbar('H Low', src, hlow, 180, n)
        cv2.createTrackbar('H High', src, hhigh, 180, n)
        cv2.createTrackbar('S Low', src, slow, 255, n)
        cv2.createTrackbar('S High', src, shigh, 255, n)
        cv2.createTrackbar('V Low', src, vlow, 255, n)
        cv2.createTrackbar('V High', src, vhigh, 255, n)

        while (1):
            k = cv2.waitKey(1) & 0xFF
            if (k == ord('n')):
                break
            elif (k == ord('q')):
                flag = True
                break
            hlow = cv2.getTrackbarPos('H Low', src)
            hhigh = cv2.getTrackbarPos('H High', src)
            slow = cv2.getTrackbarPos('S Low', src)
            shigh = cv2.getTrackbarPos('S High', src)
            vlow = cv2.getTrackbarPos('V Low', src)
            vhigh = cv2.getTrackbarPos('V High', src)

            LOWER_MASK = np.array([hlow, slow, vlow])
            UPPER_MASK = np.array([hhigh, shigh, vhigh])

            _, _, drawing = get_bbox(og, draw=True, lower_mask=LOWER_MASK, upper_mask=UPPER_MASK)
            cv2.imshow(src, drawing)

        cv2.destroyAllWindows()

        if (hlow < h[1]):
            h[1] = hlow
        if (slow < s[1]):
            s[1] = hlow
        if (vlow < v[1]):
            v[1] = hlow

        if (hhigh > h[0]):
            h[0] = hhigh
        if (shigh > s[0]):
            s[0] = shigh
        if (vhigh > v[0]):
            v[0] = vhigh

        if flag:
            break


    print("H:", h[1], h[0], "\nS:", s[1], s[0], "\nV:", v[1], v[0])

if __name__=="__main__":
    main() 

