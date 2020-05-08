import numpy as np 
import cv2
import bbox_hsv as bbox 
import time


DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\IMG_0111.MOV"

def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.mp4', 0x7634706d, 20.0, (1000,1000))

    times = []

    while(cap.isOpened()):
        start = time.time()

        _, frame = cap.read()

        try:
            frame = bbox.preprocess(frame)
        except:
            print("End of video")
            break

        box, _, _ = bbox.get_bbox(frame, draw=True, source="Video")
        
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)

        times += [time.time() - start]
        # cv2.waitKey(20)

    print("Average frame processing time:", np.average(times))

    cap.release()
    # out.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()