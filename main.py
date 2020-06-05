import time
import sys

import cv2
from pylogix import PLC
import numpy as np

from source import model
sys.modules['model'] = model
from source.global_parameters import global_parameters
from source.global_parameters import set_parameters
set_parameters("resources\configs\main-05062020-132549")

from source.path_planning.frame_handler import FrameHandler
from source.data_send_receive.instruction_handler import InstructionHandler
from source.vision_identification import bounding_box

frame_handler = FrameHandler()
instruction_handler = InstructionHandler()
video_capture = cv2.VideoCapture(r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4")
times = []

instruction_handler.start()

with PLC() as plc:
    plc.IPAddress = global_parameters['PLC_IP']
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

        if not count_flag:
            val = 0
        else:
            count_flag = False

        if val != 0: # If image is available
            if frame_handler.process_frame(frame, read_time, draw=True):
                time_stamps, profiles = frame_handler.get_results()

                flag = False
                for i in range(0, len(profiles)):
                    # Adds full path to instruction handler 
                    instruction_handler.add(time_stamps[i], profiles[i])
                    flag = True
                if flag:
                    instruction_handler.add(0, 0) # Ending flag. This is how the handler knows the command is over
        ################################


        #### Just for visualization ####
        # else:
        frame = bounding_box.scale(frame)
        frame = cv2.copyMakeBorder(frame, 0, 300, 300, 300, cv2.BORDER_CONSTANT, value=0)

        global_parameters['PICKUP_POINT'].draw(frame)
        cv2.imshow("Temp", frame)

        k = cv2.waitKey(max(global_parameters['FRAME_RATE'] - round((time.time() - read_time )*1000 + 1), 1)) & 0xFF
        if k == ord('q'):    
            break
        elif k == ord('c'):
            count_flag = True
        #################################
        
    instruction_handler.stop()