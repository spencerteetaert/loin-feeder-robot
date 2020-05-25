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

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)

def main(data_path=DATA_PATH):
    active = False
    cap = cv2.VideoCapture(data_path)
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output14.mp4', 0x7634706d, 30, (850,830))

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    delay = 0
    processing_times = []
    path_times = []
    display_times = []
    times_that_matter = []
    meats = [0]
    flip_flop = False 
    counter = 0
    queue = []

    while(cap.isOpened()):
        ################################################
        ### Video Processing and Meat Identification ###
        ################################################

        tstart = time.time()
        start = time.time()
        _, frame = cap.read()
        
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        try:
            frame = bbox.preprocess(frame)
        except:
            print("End of video")
            break

        iH, iW, _ = frame.shape
        box, mask = bbox.get_bbox(frame)

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
                            
                            delay = 0
                    except:
                        pass
        delay += 1
        processing_times += [time.time() - start]

        ########################################
        ### Path planning and Robot Movement ###
        ########################################

        start = time.time()
        ep1 = Point(625, 735, angle=90)
        ep2 = Point(250, 735, angle=90)

        if len(meats) > 3:
            if len(meats) % 2 == 0 and delay == 1:
                # Queue [P1 index, P2 index]
                queue += [[len(meats) - 1, len(meats) - 2]]
                
        if model.phase == 0 and len(queue) > 0:
            dist = (GlobalParameters.PICKUP_POINT - meats[queue[0][0]].get_center_as_point()).y

            if dist > 0:
                sp1 = meats[queue[0][0]].get_center_as_point().copy() + Point(0, dist)
                sp2 = meats[queue[0][1]].get_center_as_point().copy() + Point(0, dist)
                model.moveMeat(sp1, sp2, ep1, ep2, dist // GlobalParameters.CONVEYOR_SPEED)
                queue = queue[1:]

                # temp_start = time.time()
                # while model.update():
                #     pass
                # print(time.time() - temp_start)
            else:
                print("ERROR: Conveyor Speed too fast for current settings")
                queue = queue[1:]

        if model.phase != 0:
            model.update()
        path_times += [time.time() - start]
        times_that_matter += [time.time() - tstart]

        ###############
        ### Display ###
        ###############        
        
        start = time.time()
        if (len(meats) != 1):
            for i in range(1, len(meats)):
                meats[i].draw(frame, color=(255, 255, 0))
        model.draw(frame)
        cv2.imshow(win, frame)         
        display_times += [time.time() - start]

        ################
        ### Controls ###
        ################

        for i in range(1, len(meats)):
            meats[i].step()
        counter += 1

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)
        elif k == ord('r'):
            model.phase = 0

        # out.write(frame)

    print("Processing frame time:", np.average(processing_times))
    print("Path planning frame time:", np.average(path_times))
    print("Display frame time:", np.average(display_times))
    print("Total frame time:", np.average(processing_times) + np.average(path_times) + np.average(display_times))
    print("\nTotal real runtime:", np.sum(times_that_matter))

    cap.release()
    # out.release()
    cv2.destroyAllWindows()

main()