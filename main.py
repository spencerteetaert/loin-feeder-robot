import time
import sys
import argparse
import multiprocessing as mp

import cv2
from pylogix import PLC
import numpy as np

from source import model
sys.modules['model'] = model
from source.global_parameters import global_parameters
from source.global_parameters import set_parameters
from source.model.robot import Robot
# set_parameters("resources\configs\main-10062020-124541")

from source.path_planning.frame_handler import FrameHandler
from source.vision_identification import bounding_box

frame_handler = FrameHandler()
video_capture = cv2.VideoCapture(r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4")

# ap = argparse.ArgumentParser()
# ap.add_argument("-v", "--video", required=False,
# 	help="path to the video file")
# args = vars(ap.parse_args())

# video_capture = cv2.VideoCapture(args['video'])

times = []  

with PLC() as plc:
    plc.IPAddress = global_parameters['PLC_IP']
    def run(Q):
        model = Robot(global_parameters['ROBOT_BASE_POINT'], global_parameters['VIDEO_SCALE'])   
        win = "Window"
        cv2.namedWindow(win)

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
                    model.set_model_state(to_send, vel_toggle=True)
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
            model.draw(frame)
            cv2.imshow(win, frame)
            cv2.waitKey(1)

    if __name__=="__main__":
        Q = mp.Queue(maxsize=1048)
        process = mp.Process(target=run, args=(Q,))
        process.start()

        count_flag = False

        while True:
            ### Read and process PLC data ### 
            '''
            Before any frame is processed, the model
            is updated to reflect the current physical
            state of the robot.
            
            State:
                Main Track
                    0: Length
                Main Arm
                    1: Length
                    2: Angle
                Secondary Arm
                    3: Length1
                    4: Length2
                    5: Angle 
                Carriage1
                    6: Angle
                    7: Raised/Lowered
                    8: Gripper extension
                Carriage2
                    9: Angle
                    10: Raised/Lowered
                    11: Gripper extension
            '''

            # v1 = plc.Read("<tag1>").Value
            # v2 = plc.Read("<tag2>").Value
            # v3 = plc.Read("<tag3>").Value
            # v4 = plc.Read("<tag4>").Value
            # v5 = plc.Read("<tag5>").Value
            # v6 = plc.Read("<tag6>").Value
            # v7 = plc.Read("<tag7>").Value
            # v8 = plc.Read("<tag8>").Value
            # v9 = plc.Read("<tag9>").Value
            # v10 = plc.Read("<tag10>").Value
            # v11 = plc.Read("<tag11>").Value

            # ERROR: Currently the model will start from an improper place when it sees the next meat
            # Need to find a way to account for this and adjust the start of path in real time. 
            # frame_handler.model.set_model_state([v1, v2, v3, v4, v5, v6, v7, v8, v9, v10, v11])

            # val.TagName, val.Value, val.Status

            #################################


            #### Read and Process Image ####
            read_time = time.time()

            #To be replaced by camera trigger software 
            (val, frame) = video_capture.read() 

            if val: # If image is available
                if count_flag:
                    if frame_handler.process_frame(frame, read_time):
                        time_stamps, profiles = frame_handler.get_results()

                        flag = False
                        for i in range(0, len(profiles)):
                            # Adds full path to instruction handler 
                            Q.put(time_stamps[i])
                            Q.put(profiles[i])
                            flag = True
                        if flag:
                            Q.put(0) # Ending flag. This is how the handler knows the command is over
                    print("Frame time:", time.time() - read_time)
                    count_flag = False
            ################################


                #### Just for visualization ####
                # else:
                frame = bounding_box.scale(frame)
                frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

                (global_parameters['PICKUP_POINT1'] * global_parameters['VIDEO_SCALE']).draw(frame)
                cv2.imshow("Temp", frame)

                k = cv2.waitKey(max(global_parameters['FRAME_RATE'] - round((time.time() - read_time )*1000 + 1), 1)) & 0xFF
                # k = cv2.waitKey(1) & 0xFF
                if k == ord('q'):    
                    cv2.destroyAllWindows()
                    break
                elif k == ord('c'):
                    count_flag = True
            else:
                print("ERROR: Image import failed.")
                break
            #################################
        Q.put(None)