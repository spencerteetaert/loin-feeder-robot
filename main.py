import time

import cv2
from pylogix import PLC
import numpy as np

from source import global_parameters
from source.path_planning.frame_handler import FrameHandler
from source.data_send_receive.instruction_handler import InstructionHandler
from source.vision_identification import bounding_box

frame_handler = FrameHandler()
instruction_handler = InstructionHandler()
video_capture = cv2.VideoCapture(r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4")
times = []

instruction_handler.start()

with PLC() as plc:
    plc.IPAddress = global_parameters.PLC_IP
    count_flag = False

    while True:
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

        global_parameters.PICKUP_POINT.draw(frame)
        cv2.imshow("Temp", frame)

        k = cv2.waitKey(max(global_parameters.FRAME_RATE - round((time.time() - read_time )*1000 + 1), 1)) & 0xFF
        if k == ord('q'):    
            break
        elif k == ord('c'):
            count_flag = True
        #################################


        ### Read and process PLC data ### 

        # val1 = plc.Read("<tag1>")
        # val2 = plc.Read("<tag2>")
        # val3 = plc.Read("<tag3>")

        # Do something with read vals
        # val.TagName, val.Value, val.Status

        #################################
        
    instruction_handler.stop()