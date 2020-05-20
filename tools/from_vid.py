import time

import numpy as np 
import cv2

from context import sample
from sample.VisionIdentification import bbox
from sample.VisionIdentification.meat import Meat 

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"

def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output6.mp4', 0x7634706d, 30, (500,1059))

    delay = 0
    times = []
    meats = [0]
    flip_flop = False 
    switch = 1

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
            if switch==1:
                res = bbox.draw_results(frame, [meats[-1].get_bbox()], "Test", meat=meats[-1], extra_data=data)
            elif switch==2:
                filtered = bbox.gen_mask(frame, bitwise_and=True, process=False)
                bbox.draw_results(filtered, [meats[-1].get_bbox()], "Test", meat=meats[-1], extra_data=data)
            elif switch==3:
                filtered = bbox.gen_mask(frame, bitwise_and=False, process=True)
                bbox.draw_results(filtered, [meats[-1].get_bbox()], "Test", meat=meats[-1], extra_data=data)
            # res = bbox.draw_results(mask, box, "Test", meat=meats[-1])
        except:
            res = frame
            cv2.imshow("Test", frame)              

        for i in range(1, len(meats)):
            meats[i].step()

        # filtered = bbox.gen_mask(frame, bitwise_and=True, process=True)
        # mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        # t1 = filtered[:,0:int(iW//3)]
        # t2 = filtered[:,int(iW//3):int(iW*2//3+1)]
        # t3 = filtered[:,int(iW*2//3+1):iW-1]
        # # t2 = mask[1:-1,int(iW//3):int(iW*2//3+1)]
        # # t3 = mask[1:-1,int(iW*2//3+1):iW-1]

        # temp1 = cv2.hconcat([t1, t2])
        # temp = cv2.hconcat([temp1, t3])

        # # color = (31, 255, 49)
        # # if (box != 0):
        # #     for i in range(0, len(box)):
        # #         cv2.drawContours(temp, box, i, color, 2)

        # out.write(res)
        # cv2.imshow("Split", temp)
        
        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)
        elif k == ord('1'):
            switch = 1
        elif k == ord('2'):
            switch = 2
        elif k == ord('3'):
            switch = 3

        # if delay == 0:
        #     cv2.waitKey(0)
        delay += 1
        times += [time.time() - start]
        # cv2.waitKey(20)

    print("Average frame processing time:", np.average(times))

    cap.release()
    # out.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()