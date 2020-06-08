import numpy as np
import cv2
from skimage import feature 

from ..global_parameters import global_parameters

def crop(img):
    '''Crops image to be largest square possible'''
    iH, iW, _ = img.shape
    crop_size = min(iH, iW)
    ret = img[(iH - crop_size)//2:(iH - crop_size)//2 + crop_size,(iW - crop_size)//2:(iW - crop_size)//2+crop_size]
    return ret

def scale(img, width=250):
    iH, iW, _ = img.shape

    final_window_width = width

    dest_width = final_window_width
    dest_height = round((final_window_width / iW) * iH)

    res = cv2.resize(img, dsize=(dest_width, dest_height), interpolation=cv2.INTER_CUBIC)
    return res

def get_bbox(img, lower_mask=global_parameters['LOWER_MASK'], upper_mask=global_parameters['UPPER_MASK']):
    '''
    Returns bounding polygons for the all identified middles 
    in the image
    '''
    temp = gen_mask(img, lower_mask=lower_mask, upper_mask=upper_mask)
    bound_poly, contours = thresh_callback(temp)

    return bound_poly, contours, temp

def gen_mask(img, lower_mask=global_parameters['LOWER_MASK'], upper_mask=global_parameters['UPPER_MASK'], bitwise_and=False, process=True):
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
        mask = cv2.copyMakeBorder(mask, 150, 150, 150, 150, cv2.BORDER_CONSTANT, value=0)

        # kernel = np.ones([round(iW*0.013),round(iH*0.013)])
        # refined = cv2.dilate(mask, kernel)

        # kernel = np.ones([round(iW*0.02),round(iH*0.02)])
        # refined = cv2.erode(refined, kernel)

        # kernel = np.ones([round(iW*0.035),round(iH*0.035)])
        # refined = cv2.dilate(refined, kernel)
        # refined = cv2.erode(refined, kernel)

        kernel = np.ones([11,11]) #0.02
        refined = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, kernel)

        # kernel = np.ones([round(iH*0.03),round(iH*0.03)])
        # refined = cv2.erode(refined, kernel)

        kernel = np.ones([27,27]) #0.05
        refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)

        kernel = np.ones([42,42]) #0.08
        refined = cv2.morphologyEx(refined, cv2.MORPH_OPEN, kernel)

        # kernel = np.ones([round(iH*0.09),round(iH*0.09)])
        # refined = cv2.erode(refined, kernel)


        # kernel = np.ones([round(iW*0.08),round(iH*0.08)])
        # refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)

        # kernel = np.ones([round(iW*0.1),round(iH*0.1)])
        # refined = cv2.morphologyEx(refined, cv2.MORPH_CLOSE, kernel)
    else:
        refined = mask

    if bitwise_and:
        return cv2.bitwise_and(img, img, mask=refined)
    return refined[151:-151,151:-151]

def thresh_callback(mask):
    ''' Returns single convex hull of all contours of mask '''   

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if (len(contours) == 0):
        return 0, 0

    minRects = [None]*len(contours)
    for i, c in enumerate(contours):
        temp = np.intp(cv2.boxPoints(cv2.minAreaRect(c)))
        minRects[i] = [temp, cv2.moments(temp)]

    filt = []
    for i in range(0, len(minRects)):
        flag = True
        if (minRects[i][1]['m00'] < global_parameters['MINIMUM_AREA']):
            flag = False
            
        filt += [flag]

    ret = [minRects[i] for i in range(0, len(minRects)) if filt[i]==True]


    return ret, contours