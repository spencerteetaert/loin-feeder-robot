import numpy as np 
import cv2
import bbox_hsv as bbox 


DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\IMG_0111.MOV"

def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)

    while(cap.isOpened()):
        ret, frame = cap.read()

        frame = bbox.preprocess(frame)
        box = bbox.get_bbox(frame)
        bbox.draw_results(frame, box, "test")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # cv2.waitKey(20)

    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()