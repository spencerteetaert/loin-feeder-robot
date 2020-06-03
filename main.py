import cv2
from pylogix import PLC
import time
import numpy as np

from source import global_parameters
from source.path_planning.frame_handler import FrameHandler
from source.data_send_receive.instruction_handler import InstructionHandler

frame_handler = FrameHandler()
instruction_handler = InstructionHandler()
video_capture = cv2.VideoCapture(r"C:\Users\User\Documents\Hylife 2020\Loin Feeder\Data\good.mp4")
times = []

instruction_handler.start()

with PLC() as plc:
    plc.IPAddress = global_parameters.PLC_IP
    
    while True:
        ''' 
            Read camera image if available 
            Process image and store a sequential instruction set 
            Send the next instruction as required 
            Read feedbaack data from PLC
            Parse for errors
        '''

        ### Read and Process Image ### 
        t = time.time()
        (val, frame) = video_capture.read() 
        # print("1")

        if val != 0: # If image is available
            if frame_handler.process_frame(frame, t, draw=True):
                time_stamps, profiles = frame_handler.get_results()

                temp = time.time()
                for i in range(0, len(profiles)):
                    instruction_handler.add(time_stamps[i], profiles[i])
                instruction_handler.add(0, 0)
                print("TEST", time.time() - temp)

            # cv2.imshow("Temp", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):    
                break

        time.sleep(6)

        # print(time.time() - t)
        ### Read and process PLC data ### 

        # val1 = plc.Read("<tag1>")
        # val2 = plc.Read("<tag2>")
        # val3 = plc.Read("<tag3>")

        # Do something with read vals
        # val.TagName, val.Value, val.Status
        
    print("Average time", np.average(times))
    instruction_handler.stop()
        # break