import time

import numpy as np 
import cv2

from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample import GlobalParameters

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"
model = Robot(Point(280, 600), GlobalParameters.VIDEO_SCALE)


def main(data_path=DATA_PATH):
    cap = cv2.VideoCapture(data_path)
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output11.mp4', 0x7634706d, 30, (850,830))

    pt1 = Point(500, 300, angle=0)
    pt2 = Point(500, 600, angle=0)

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

                        if iH / 3 - 5 < cY and iH / 3 + 5 > cY:
                            if flip_flop:
                                meats += [meat.Meat(box[i], side="Right", center=[cX, cY])]
                            else:
                                meats += [meat.Meat(box[i], side="Left", center=[cX, cY])]
                            flip_flop = not flip_flop
                            print("Meat detected")
                            print(meats[-1])
                        
                            
                            delay = 0
                    except:
                        pass

        if len(meats) % 2 == 0 and len(meats) > 3:
            t1 = (meats[-1].get_center_as_point() - pt1).mag()
            t2 = (meats[-2].get_center_as_point() - pt2).mag()

            f1 = 8
            f2 = 8
            if t1 < 10:
                f1 = 2
            if t2 < 10:
                f2 = 2

            pt1.moveTo(meats[-1].get_center_as_point(), t1/f1)
            pt2.moveTo(meats[-2].get_center_as_point(), t2/f2)
        elif len(meats) > 4:
            t1 = (meats[-2].get_center_as_point() - pt1).mag()
            t2 = (meats[-3].get_center_as_point() - pt2).mag()

            pt1.moveTo(meats[-2].get_center_as_point(), t1/2)
            pt2.moveTo(meats[-3].get_center_as_point(), t2/2)
        
        pt1.update()
        pt2.update()
        # print(pt1.update_vec)
        pt1.draw(frame)
        pt2.draw(frame)
        model.moveTo(pt1, pt2)

        try:   
            model.draw(frame)
            for i in range(1, len(meats)):
                meats[i].draw(frame)
            cv2.imshow("Test", frame)
        except:
            model.draw(frame)
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

        # out.write(frame)

    print("Average frame processing time:", np.average(times))

    cap.release()
    # out.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()