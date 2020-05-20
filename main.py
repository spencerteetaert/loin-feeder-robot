import numpy as np 
import cv2
import time

import lib.VisionIdentification.bbox_hsv as bbox
from lib.VisionIdentification.meat import Meat

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"

def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output6.mp4', 0x7634706d, 30, (500,1059))

    delay = 0
    times = []
    meats = [0]
    flip_flop = False 

    while(cap.isOpened()):
        start = time.time()

        _, frame = cap.read()
        
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        try:
            frame = bbox.preprocess(frame)
        except:
            print("End of video")
            break

        iH, iW, _ = frame.shape

        box, mask, _ = bbox.get_bbox(frame)

        if (box != 0):
            for i in range(0, len(box)):
                if delay > 50:
                    try:
                        M = cv2.moments(box[i])
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])

                        if iH / 1.8 - 5 < cY and iH / 1.8 + 5 > cY:
                            if flip_flop:
                                meats += [Meat(box[i], side="Right", center=[cX, cY])]
                            else:
                                meats += [Meat(box[i], side="Left", center=[cX, cY])]
                            flip_flop = not flip_flop
                            print("Meat detected")
                            print(meats[-1])
                            
                            data = "Side:" + meats[-1].get_side() + "\n" + str(delay) + "\nArea:" + str(meats[-1].get_area())
                            
                            delay = 0
                    except:
                        pass

        try:   
            res = bbox.draw_results(frame, [meats[-1].get_bbox()], "Test", meat=meats[-1], extra_data=data)
        except:
            res = frame
            cv2.imshow("Test", frame)              

        for i in range(1, len(meats)):
            meats[i].step()

        
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)

        delay += 1
        times += [time.time() - start]

    print("Average frame processing time:", np.average(times))

    cap.release()
    # out.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()
    pass