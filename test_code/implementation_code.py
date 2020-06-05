import time

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
from source.global_parameters import global_parameters

'''
    A full implementation of all of the non-PLC specific functionality 
    of the library.
'''

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"
DISPLAY_TOGGLE = True
PROFILER_TOGGLE = True

# Model for creating acceleration profiles
if PROFILER_TOGGLE:
    profile_model = Robot(Point(280, 600), global_parameters['VIDEO_SCALE'])
    path_runner = PathRunner(profile_model)
# Model for display
if DISPLAY_TOGGLE:
    drawing_model = Robot(Point(280, 600), global_parameters['VIDEO_SCALE'])
    current_graph = np.zeros([830, 830, 3], dtype=np.uint8)
    grapher = graphing_tools.Grapher()

streamer = FileVideoStream(DATA_PATH)
streamer.start()
time.sleep(1) 

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)

def main(data_path=DATA_PATH):
    global streamer, grapher, profile_model, drawing_model, current_graph, DISPLAY_TOGGLE
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.mp4', 0x7634706d, 30, (1680,830))
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (1680,830))

    if DISPLAY_TOGGLE:
        win = "Window"
        cv2.namedWindow(win)
        cv2.setMouseCallback(win, on_mouse)

    delay = 0
    flip_flop = False 
    flip_flop2 = False

    meats = [0]
    queue1 = []
    queue2 = []
    times = []
    saved_state = []

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
        
        # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        temp = streamer.read()
        frame = bounding_box.scale(temp)
        frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        iH, iW, iD = frame.shape
        box, _, _ = bounding_box.get_bbox(frame)

        # for i in range(0, len(box)):
        #     cv2.drawContours(frame, [box[i][0]], 0, (255, 255, 255), 3)
        
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

        ########################################
        ### Path planning and Robot Movement ###
        ########################################

        ep1 = Point(625, 735, angle=90)
        ep2 = Point(250, 735, angle=90)

        if len(meats) > 3:
            if len(meats) % 2 == 0 and delay == 1:
                # Queue [P1 index, P2 index], so that meat can be accounted for even if robot is currently in motion 
                queue1 += [[len(meats) - 1, len(meats) - 2]]
                queue2 += [[len(meats) - 1, len(meats) - 2]]
                
        # # Profiler model creates motion profiles, it updates as fast as possible in a separate thread
        if PROFILER_TOGGLE:
            if profile_model.phase == 0 and len(queue1) > 0 and not path_runner.running:
                dist = (global_parameters['PICKUP_POINT'] - meats[queue1[0][0]].get_center_as_point()).y

                if dist > 0:
                    sp1 = meats[queue1[0][0]].get_center_as_point().copy() + Point(0, dist)
                    sp2 = meats[queue1[0][1]].get_center_as_point().copy() + Point(0, dist)
                    profile_model.move_meat(sp1, sp2, ep1, ep2, dist // global_parameters['CONVEYOR_SPEED'], \
                        meats[queue1[0][0]].width, meats[queue1[0][1]].width, phase_1_delay=False)
                    queue1 = queue1[1:]

                    # Given the start and end conditions, calculate the profile_model motor profiles
                    path_runner.start()
            
        # Drawing model is just for drawing purposes, it updates at the frame rate displayed
        if DISPLAY_TOGGLE:
            if drawing_model.phase == 0 and len(queue2) > 0:
                dist = (global_parameters['PICKUP_POINT'] - meats[queue2[0][0]].get_center_as_point()).y

                if dist > 0:
                    sp1 = meats[queue2[0][0]].get_center_as_point().copy() + Point(0, dist)
                    sp2 = meats[queue2[0][1]].get_center_as_point().copy() + Point(0, dist)
                    drawing_model.move_meat(sp1, sp2, ep1, ep2, dist // (global_parameters['CONVEYOR_SPEED'] * \
                        global_parameters['RUNTIME_FACTOR']), meats[queue2[0][0]].width, meats[queue2[0][1]].width)
                    queue2 = queue2[1:]
                    flip_flop2 = True
                    if PROFILER_TOGGLE:
                        grapher.start(path_runner, (830, 830), 'o')
                else:
                    print("ERROR: Conveyor Speed too fast for current settings")
                    queue2 = queue2[1:]
            drawing_model.update()

        # Changes display chart
        if DISPLAY_TOGGLE and PROFILER_TOGGLE:
            if flip_flop2 and not path_runner.running and not grapher.running:
                current_graph = grapher.read()
                flip_flop2 = False

        ###############
        ### Display ###
        ###############        
        
        if DISPLAY_TOGGLE:
            if (len(meats) != 1):
                for i in range(1, len(meats)):
                    meats[i].draw(frame, color=(255, 255, 0))
            drawing_model.draw(frame)

            if PROFILER_TOGGLE:
                frame = np.concatenate((frame, current_graph), axis=1)
            cv2.imshow(win, frame)

        ################
        ### Controls ###
        ################

        for i in range(1, len(meats)):
            meats[i].step()

        if DISPLAY_TOGGLE:
            # k = cv2.waitKey(1) & 0xFF
            k = cv2.waitKey(max(global_parameters['FRAME_RATE'] - round((time.time() - force_timer )*1000 + 1), 1)) & 0xFF
            if k == ord('q'):
                break
            elif k == ord('p'):
                cv2.waitKey(0)
            elif k == ord('o'):
                grapher.start(path_runner, (830, 830), 'o')
                while grapher.running:
                    pass
                current_graph = grapher.read()
            elif k == ord('i'):
                grapher.start(path_runner, (830, 830), 'i')
                while grapher.running:
                    pass
                current_graph = grapher.read()
            elif k == ord('s'):
                saved_state = drawing_model.get_model_state()
                cv2.waitKey(0)
                print("State saved.\n")
            elif k == ord('r'):
                drawing_model.set_model_state(saved_state)
                print("State uploaded.")
            
        times += [time.time() - start]
        # out.write(frame)

        #Artifically slow the program to the desired frame rate
        

    print("Average frame time:", np.average(times))
    # out.release()
    streamer.stop()
    if PROFILER_TOGGLE:
        path_runner.stop()
    if DISPLAY_TOGGLE:
        grapher.stop()
    cv2.destroyAllWindows()

main()