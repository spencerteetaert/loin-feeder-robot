import time
import multiprocessing as mp
from multiprocessing import Lock
from queue import Queue

import numpy as np 
import cv2
from pylogix import PLC

from context import source
from source.vision_identification.video_reader import FileVideoStream
from source.path_planning.frame_handler import FrameHandler
from source.vision_identification import bounding_box
from source.model.robot import Robot
from source.global_parameters import global_parameters

'''
    A full implementation of all of the non-PLC specific functionality 
    of the library.
'''
DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4"

def on_mouse(event, pX, pY, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        print("Clicked", pX, pY)    

def run(Q, shared_data):
    with PLC() as plc:
        win = "Window"
        cv2.namedWindow(win)

        plc.IPAddress = global_parameters['PLC_IP']
        current_time = Q.get()
        counter = 0

        while True:
            if current_time is None:
                break
            if current_time < time.time() and current_time > 0:
                if counter == 0:
                    s = time.time()
                    # print("Sending instructions to PLC...")
                counter += 1
                if not Q.empty():
                    instruction = Q.get()
                    to_send = np.around(instruction, 2)

                    ### PLC write instruction ###
                    # print(instruction)
                    # print(current_time, time.time())
                    shared_data.set_model_state(to_send, vel_toggle=True)
                    # plc.Write("<tag0>", value=instruction[0])
                    # plc.Write("<tag1>", value=instruction[1])
                    # plc.Write("<tag2>", value=instruction[2])
                    # plc.Write("<tag3>", value=instruction[3])
                    # plc.Write("<tag4>", value=instruction[4])
                    # plc.Write("<tag5>", value=instruction[5])
                    # plc.Write("<tag6>", value=instruction[6])
                    # plc.Write("<tag7>", value=instruction[7])
                    #############################

                    current_time = Q.get()
                else:
                    print("ERROR: Instruction size mismatch.")

            elif current_time == 0 and counter != 0:
                # Send a stop order to stop all motion
                # plc.Write("<tag0>", value=instruction[0])
                # plc.Write("<tag1>", value=instruction[1])
                # plc.Write("<tag2>", value=instruction[2])
                # plc.Write("<tag3>", value=instruction[3])
                # plc.Write("<tag4>", value=instruction[4])
                # plc.Write("<tag5>", value=instruction[5])
                # plc.Write("<tag6>", value=instruction[6])
                # plc.Write("<tag7>", value=instruction[7])
                counter = 0
                print("Instruction completed. \nExecution time:", round(time.time() - s, 2),"s\n")
                current_time = Q.get()

            frame = np.zeros([800, 800, 3])
            shared_data.draw(frame)
            cv2.imshow(win, frame)
            cv2.waitKey(1)

def main():  
    shared_data = Robot(global_parameters['ROBOT_BASE_POINT'], global_parameters['VIDEO_SCALE'])

    Q = mp.Queue(maxsize=1048)
    process = mp.Process(target=run, args=(Q,shared_data,))
    process.start()

    frame_handler = FrameHandler()

    streamer = FileVideoStream(DATA_PATH)
    streamer.start()
    time.sleep(1) 
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.mp4', 0x7634706d, 30, (1680,830))
    # out = cv2.VideoWriter(r'C:\Users\User\Documents\Hylife 2020\Loin Feeder\output.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (1680,830))

    win = "Window"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)

    delay = -120
    counter = 90 
    timer1 = 0 
    times = []

    try:
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

            # Artificially simulate camera trigger 
            temp1 = streamer.read()
            temp2 = bounding_box.scale(temp1)
            frame = cv2.copyMakeBorder(temp2, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

            iH, iW, iD = frame.shape
            box, _, _ = bounding_box.get_bbox(frame)

            for i in range(0, len(box)):
                cv2.drawContours(frame, [box[i][0]], 0, (0, 255, 255), 2)
            
            if (box != 0):
                for i in range(0, len(box)):
                    if delay > 50:
                        cX = int(box[i][1]["m10"] / box[i][1]["m00"])
                        cY = int(box[i][1]["m01"] / box[i][1]["m00"])

                        if iH / 3 - 5 < cY and iH / 3 + 5 > cY:
                            delay = 0
                            timer1 = 10
                            read_time = time.time()
                            if frame_handler.process_frame(temp1, read_time):
                                time_stamps, profiles = frame_handler.get_results(vel_toggle=True)

                                flag = False
                                for i in range(0, len(profiles)):
                                    # Adds full path to instruction handler 
                                    Q.put(time_stamps[i])
                                    # print(time_stamps[i])
                                    Q.put(profiles[i])
                                    flag = True
                                if flag:
                                    Q.put(0) # Ending flag. This is how the handler knows the command is over
                        
            delay += 1

            ###############
            ### Display ###
            ############### 
            
            # drawing_model.set_model_state(Q.to_send)

            # if DISPLAY_TOGGLE:
            if timer1 > 0:
                cv2.circle(frame, (int(iW / 2), int(iH / 3)), 5, (0, 255, 0), 5)

            shared_data.draw(frame)
            cv2.imshow(win, frame)

            ################
            ### Controls ###
            ################

            timer1 -= 1
            times += [time.time() - start]
            # out.write(frame)

            k = cv2.waitKey(1) & 0xFF
            # k = cv2.waitKey(max(global_parameters['FPS'] - round((time.time() - force_timer )*1000 + 1), 1)) & 0xFF
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

        print("Average frame time:", np.average(times))
        # out.release()
        streamer.stop()
        cv2.destroyAllWindows()

        Q.put(None)
    except:
        Q.put(None)

if __name__=="__main__":
    main()