import time

import numpy as np 
import cv2

from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample.PathPlanning.Path import PathFinder
from sample import GlobalParameters

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"
model = Robot(Point(280, 600), GlobalParameters.VIDEO_SCALE)
path_finder = PathFinder()
path1 = path_finder(Point(440,100, angle=40), Point(655, 735, angle=90), 40)
path2 = path_finder(Point(440,500, angle=0), Point(250, 735, angle=90), 40)

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)

def main(data_path=DATA_PATH):
    global path1, path2
    switch = True
    cap = cv2.VideoCapture(data_path)
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output11.mp4', 0x7634706d, 30, (850,830))

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

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

        if switch:
            model.followPath(path1, path2, 150)
            switch = False
        model.update()

        for i in range(0, len(path1)):
            path1[i].draw(frame)
        for i in range(0, len(path2)):
            path2[i].draw(frame, color=(0, 255, 0))
        for i in range(0, len(GlobalParameters.SAFE_ENVIRONMENT)):
            cv2.line(frame, (GlobalParameters.SAFE_ENVIRONMENT[i][0][0], GlobalParameters.SAFE_ENVIRONMENT[i][0][1]), (GlobalParameters.SAFE_ENVIRONMENT[i][1][0], GlobalParameters.SAFE_ENVIRONMENT[i][1][1]), (50, 50, 50))
    
        try:   
            model.draw(frame)
            for i in range(1, len(meats)):
                meats[i].draw(frame)
            cv2.imshow(win, frame)
        except:
            model.draw(frame)
            cv2.imshow(win, frame)              

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