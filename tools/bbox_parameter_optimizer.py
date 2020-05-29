import numpy as np
import cv2

from context import source
from source.vision_identification import bounding_box

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\test"

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

    for i in range(0, 10):
        # temp = input_path + str(i) + ".png"
        temp = input_path + str(i) + ".png"
        # try: 
        og = bounding_box.scale(cv2.imread(temp), width=500)
        og.shape
        # except:
        #     continue
        
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

            box, contours, _ = bounding_box.get_bbox(og, source=src, lower_mask=LOWER_MASK, upper_mask=UPPER_MASK)
            temp = og.copy()

            if box != 0:
                for i in range(0, len(box)):
                    cv2.drawContours(temp, [box[i][0]], 0, (255, 255, 255), 3)   
            for i in range(0, len(contours)):
                cv2.drawContours(temp, contours, i, (255, 255, 0), 2)
                
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