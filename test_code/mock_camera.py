import time
import socket
import select
import errno # Error codes
import sys

import numpy as np 
import cv2

from context import source
from source.vision_identification import bounding_box
from source.vision_identification.video_reader import FileVideoStream
from source.vision_identification import meat
from source.model.robot import Robot
from source.model.point import Point
from source.path_planning.path_runner import PathRunner
from source.path_planning import graphing_tools
from source import global_parameters

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((socket.gethostname(), 2000))

client_socket.setblocking(False) # makes receive non blocking 

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"
DISPLAY_TOGGLE = True

streamer = FileVideoStream(DATA_PATH)
streamer.start()
time.sleep(1) 

def main(data_path=DATA_PATH):
    global streamer
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.mp4', 0x7634706d, 30, (1680,830))

    if DISPLAY_TOGGLE:
        win = "Window"
        cv2.namedWindow(win)

    delay = 0
    flip_flop = False 
    flip_flop2 = False

    meats = [0]
    queue1 = []
    queue2 = []
    times = []

    while(streamer.running):
        start = time.time()
        ################################################
        ### Video Processing and Meat Identification ###
        ################################################
        
        force_timer = time.time()

        # Keeps streamer queue size within a lag free range (>0 and <128)
        qsize = streamer.Q.qsize()
        if qsize < 40:
            streamer.sleep_time = 0
        elif qsize > 88:
            streamer.sleep_time = 0.005

        temp = streamer.read()
        frame = bounding_box.scale(temp)
        frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        iH, iW, iD = frame.shape
        box, _, _ = bounding_box.get_bbox(frame)
        
        # Artificially simulate camera trigger 
        if (box != 0):
            for i in range(0, len(box)):
                if delay > 50:
                    cX = int(box[i][1]["m10"] / box[i][1]["m00"])
                    cY = int(box[i][1]["m01"] / box[i][1]["m00"])

                    if iH / 3 - 5 < cY and iH / 3 + 5 > cY:
                        if flip_flop:
                            meats += [meat.Meat(box[i], side="Right", center=[cX, cY])]
                        else:
                            meats += [meat.Meat(box[i], side="Left", center=[cX, cY])]
                        flip_flop = not flip_flop
                        delay = 0

        delay += 1

        ###############
        ### Display ###
        ###############        
        
        if DISPLAY_TOGGLE:
            cv2.imshow(win, frame)

        ################
        ### Controls ###
        ################

        for i in range(1, len(meats)):
            meats[i].step()

        if DISPLAY_TOGGLE:
            k = cv2.waitKey(1) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('p'):
                cv2.waitKey(0)
            
        times += [time.time() - start]
        # out.write(frame)

        #Artifically slow the program to the desired frame rate
        # cv2.waitKey(max(global_parameters.FRAME_RATE - round((time.time() - force_timer )*1000 + 1), 1))

    print("Average frame time:", np.average(times))
    # out.release()
    streamer.stop()
    cv2.destroyAllWindows()

main()