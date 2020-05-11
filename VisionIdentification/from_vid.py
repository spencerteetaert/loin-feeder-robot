import numpy as np 
import cv2
import bbox_hsv as bbox 
import time


DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\IMG_0111.MOV"

def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)
    out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output3.mp4', 0x7634706d, 30, (1279,720))

    times = []

    while(cap.isOpened()):
        start = time.time()

        _, frame = cap.read()

        try:
            frame = bbox.preprocess(frame)
        except:
            print("End of video")
            break

        iH, iW, _ = frame.shape

        box, mask, _ = bbox.get_bbox(frame)
        filtered = bbox.gen_mask(frame, bitwise_and=True)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        t1 = frame[:,0:int(iW//3)]
        t2 = filtered[:,int(iW//3):int(iW*2//3+1)]
        t3 = mask[1:-1,int(iW*2//3+1):iW-1]

        temp1 = cv2.hconcat([t1, t2])
        temp = cv2.hconcat([temp1, t3])

        color = (31, 255, 49)
        if (box != 0):
            for i in range(0, len(box)):
                cv2.drawContours(temp, box, i, color, 2)

        out.write(temp)
        cv2.imshow("Split", temp)
        
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)

        times += [time.time() - start]
        # cv2.waitKey(20)

    print("Average frame processing time:", np.average(times))

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()