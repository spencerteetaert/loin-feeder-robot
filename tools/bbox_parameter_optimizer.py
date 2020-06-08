import numpy as np
import cv2

from context import source
from source.vision_identification import bounding_box

'''
    Iterates through images allowing user to adjust HSV filter values to 
    see the effect on the bounding box algorithm. At the end of the list, 
    the lowest min value and highest max value are returned. 

    Images files should be of the form "DATA_PATH<index value>.FILE_TYPE"

    Controls: 
    - press 'q' to quit
    - press 'n' to go to the next image
'''

#Location of test images
DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\FilterImg\img"
FILE_TYPE = ".png"
START_INDEX = 0
END_INDEX = 89

def n(x):
    pass

def main(input_path=DATA_PATH):
    h = [0, 180]
    s = [0, 255]
    v = [0, 255]
    hlow = 0
    hhigh = 21
    slow = 100
    shigh = 194
    vlow = 98
    vhigh = 236
    flag = False

    for i in range(START_INDEX, END_INDEX+1):
        temp = input_path + str(i) + FILE_TYPE
        og = bounding_box.scale(cv2.imread(temp))
        
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

            box, contours, img = bounding_box.get_bbox(og, lower_mask=LOWER_MASK, upper_mask=UPPER_MASK)
            temp = og.copy()

            if contours != 0:
                for i in range(0, len(box)):
                    cv2.drawContours(temp, [box[i][0]], 0, (255, 255, 255), 3)   
                for i in range(0, len(contours)):
                    cv2.drawContours(temp, contours, i, ((i * 17)%255, (i * 57)%255, (i * 3)%255), 2)
                
            cv2.imshow(src, temp)

        cv2.destroyAllWindows()

        if (hlow < h[1]):
            h[1] = hlow
        if (slow < s[1]):
            s[1] = slow
        if (vlow < v[1]):
            v[1] = vlow

        if (hhigh > h[0]):
            h[0] = hhigh
        if (shigh > s[0]):
            s[0] = shigh
        if (vhigh > v[0]):
            v[0] = vhigh

        if flag:
            break

    st = ""
    st += "H: (" + str(h[1]) + "," + str(h[0]) + ")\n"
    st += "S: (" + str(s[1]) + "," + str(s[0]) + ")\n"
    st += "V: (" + str(v[1]) + "," + str(v[0]) + ")"
    print(st)

if __name__=="__main__":
    main() 