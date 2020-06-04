from threading import Thread
from threading import Lock
from queue import Queue
import time

from pylogix import PLC
import numpy as np
np.set_printoptions(suppress=True, precision=2)

from .. import global_parameters

"""
    This class is meant to ensure that the timing of instructions
    sent to the PLC are as they should be. It sends instructions
    to the PLC at a given absolute time to ensure that the machine
    output is not affected by a slow computer. 
"""

class InstructionHandler:
    def __init__(self, queueSize=1048):
        self.stopped = False
        self.running = False
        self.instruction_Q = Queue(maxsize=queueSize)
        self.time_Q = Queue(maxsize=queueSize)

    def __repr__(self):
        pass

    def start(self):
        self.stopped = False
        self.t = Thread(target=self.run, args=([]))
        self.t.daemon = True
        self.t.start()
        return self

    def stop(self):
        self.stopped = True

    def run(self):
        self.running = True
        with PLC() as plc:
            plc.IPAddress = global_parameters.PLC_IP
            current_time = self.time_Q.get()
            counter = 0

            while True:
                if self.stopped:
                    return 

                if current_time < time.time() and current_time > 0:
                    if counter == 0:
                        s = time.time()
                        print("Sending instructions to PLC...")
                    counter += 1
                    if not self.instruction_Q.empty():
                        instruction = self.instruction_Q.get()
                        to_send = np.around(instruction, 2)

                        print(instruction)

                        ### PLC write instruction ###
                        # plc.Write("<tag0>", value=instruction[0])
                        # plc.Write("<tag1>", value=instruction[1])
                        # plc.Write("<tag2>", value=instruction[2])
                        # plc.Write("<tag3>", value=instruction[3])
                        # plc.Write("<tag4>", value=instruction[4])
                        # plc.Write("<tag5>", value=instruction[5])
                        # plc.Write("<tag6>", value=instruction[6])
                        # plc.Write("<tag7>", value=instruction[7])

                        current_time = self.time_Q.get()
                    else:
                        print("ERROR: Instruction size mismatch.")

                elif current_time == 0 and counter != 0:
                    counter = 0
                    print("Instruction completed. \nExecution time:", round(time.time() - s, 2),"s\n")
                    current_time = self.time_Q.get() # get is a locking function so it stays here until the next instruction comes in
                    self.instruction_Q.get() # Clears out the 0 instruction 
                    
    def add(self, time, instruction):
        ''' Adds a time stamp and instruction profile to the queue. 
        Time stamp is as time.time() reads (in s) and instruction is a
        list of velocity values to be sent to the actuators at the given 
        time '''
        self.time_Q.put(time)
        self.instruction_Q.put(instruction)