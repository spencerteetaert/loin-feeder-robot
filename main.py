import time

import numpy as np 
import cv2

from sample.VisionIdentification import bbox
from sample.VisionIdentification import image_sizing
from sample.VisionIdentification.VideoReader import FileVideoStream
from sample.VisionIdentification import meat
from sample.Model.Robot import Robot
from sample.Model.Point import Point
from sample.PathPlanning.Path import PathFinder
from sample import GlobalParameters

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"
model = Robot(Point(280, 600), GlobalParameters.VIDEO_SCALE)
path_finder = PathFinder()

streamer = FileVideoStream(DATA_PATH)
streamer.start()
time.sleep(1)

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)

def main(data_path=DATA_PATH):
    global streamer
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output15.mp4', 0x7634706d, 30, (850,830))

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    delay = 0
    flip_flop = False 

    meats = [0]
    queue = []

    while(streamer.more()):
        ################################################
        ### Video Processing and Meat Identification ###
        ################################################
        
        qsize = streamer.Q.qsize()
        if qsize < 40:
            streamer.sleep_time = 0
        elif qsize > 80:
            streamer.sleep_time = 0.005
        
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        frame = streamer.read()
        frame = image_sizing.scale(frame)
        frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        iH, _, _ = frame.shape
        box, _ = bbox.get_bbox(frame)

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

        ########################################
        ### Path planning and Robot Movement ###
        ########################################

        ep1 = Point(625, 735, angle=90)
        ep2 = Point(250, 735, angle=90)

        if len(meats) > 3:
            if len(meats) % 2 == 0 and delay == 1:
                # Queue [P1 index, P2 index]
                queue += [[len(meats) - 1, len(meats) - 2]]
                
        if model.phase == 0 and len(queue) > 0:
            dist = (GlobalParameters.PICKUP_POINT - meats[queue[0][0]].get_center_as_point()).y

            if dist > 0:
                print("Dist", dist // GlobalParameters.CONVEYOR_SPEED)
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

        ###############
        ### Display ###
        ###############        
        
        if (len(meats) != 1):
            for i in range(1, len(meats)):
                meats[i].draw(frame, color=(255, 255, 0))
        model.draw(frame)
        cv2.imshow(win, frame)

        ################
        ### Controls ###
        ################

        for i in range(1, len(meats)):
            meats[i].step()

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('p'):
            cv2.waitKey(0)
        elif k == ord('r'):
            model.phase = 0

        # out.write(frame)
        # cv2.waitKey(15)

    # out.release()
    streamer.stop()
    cv2.destroyAllWindows()

main()