import numpy as np
import cv2

from .. import global_parameters

def crop(img):
    '''Crops image to be largest square possible'''
    iH, iW, _ = img.shape
    crop_size = min(iH, iW)
    ret = img[(iH - crop_size)//2:(iH - crop_size)//2 + crop_size,(iW - crop_size)//2:(iW - crop_size)//2+crop_size]
    return ret

def scale(img):
    iH, iW, _ = img.shape

    final_window_width = 250

    dest_width = final_window_width
    dest_height = round((final_window_width / iW) * iH)

    res = cv2.resize(img, dsize=(dest_width, dest_height), interpolation=cv2.INTER_CUBIC)
    return res

def get_bbox(img, threshold=global_parameters.BOUNDING_BOX_THESHOLD, lower_mask=global_parameters.LOWER_MASK, upper_mask=global_parameters.UPPER_MASK, source="Image"):
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

    # hulls = [cv2.convexHull(contours[i]) for i in range(0, len(contours)) if cv2.contourArea(cv2.convexHull(contours[i])) > global_parameters.MINIMUM_AREA]

    # if (len(hulls) == 0):
        # return 0

    minRects = [None]*len(contours)
    for i, c in enumerate(contours):
        temp = np.intp(cv2.boxPoints(cv2.minAreaRect(c)))
        minRects[i] = [temp, cv2.moments(temp)]
        # print(minRects[i], "\n\n")

    # Removes hulls that are contained within others. This allows for multiple pieces of meat to be detected
    filt = []
    for i in range(0, len(minRects)):
        flag = True
        for j in range(0, len(minRects)):
            # If rect is too small 
            if (minRects[i][1]['m00'] < global_parameters.MINIMUM_AREA):
                flag = False
            # If rect is inside any other rect
            # elif (cv2.pointPolygonTest(minRects[j][0], (minRects[i][0][0][0], minRects[i][0][0][1]), measureDist=False) == 1):
            #     flag = False
            # elif (cv2.pointPolygonTest(minRects[j][0], (minRects[i][0][1][0], minRects[i][0][1][1]), measureDist=False) == 1):
            #     flag = False
            # elif (cv2.pointPolygonTest(minRects[j][0], (minRects[i][0][2][0], minRects[i][0][2][1]), measureDist=False) == 1):
            #     flag = False
            # elif (cv2.pointPolygonTest(minRects[j][0], (minRects[i][0][3][0], minRects[i][0][3][1]), measureDist=False) == 1):
            #     flag = False
            # If any indices are negative 
            elif (minRects[i][0] <= 0).any():
                flag = False
            
        filt += [flag]

    ret = [minRects[i] for i in range(0, len(minRects)) if filt[i]==True]

    return ret