import numpy as np 
import cv2
import bbox_hsv as bbox 
import time


DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\IMG_0111.MOV"

def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.avi', fourcc, 20.0, (1000,1000))

    times = []

    while(cap.isOpened()):
        start = time.time()

        ret, frame = cap.read()

        frame = bbox.preprocess(frame)
        box, img = bbox.get_bbox(frame)
        temp = bbox.draw_results(frame, box, "test")

        # out.write(temp)

        # cv2.imshow("adgasdfg", box)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        times += [time.time() - start]
        # cv2.waitKey(20)

    print("Average frame time:", np.average(times))

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()