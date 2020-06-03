from pylogix import PLC
from threading import Thread
from threading import Lock
from queue import Queue
import time

from .. import global_parameters

class InstructionHandler:
    def __init__(self, queueSize=1048):
        self.stopped = False
        self.running = False
        self.instruction_Q = Queue(maxsize=queueSize)
        self.time_Q = Queue(maxsize=queueSize)

    def __repr__(self):
        pass

    def start(self):
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
            temp = time.time()
            counter = 0

            while True:
                if self.stopped:
                    return 

                if current_time < time.time():
                    print(counter)
                    counter += 1
                    # print(self.instruction_Q.empty())
                    if not self.instruction_Q.empty():
                        instruction = self.instruction_Q.get()

                        ### PLC write instruction ###
                        # plc.Write("<tag0>", value=instruction[0])
                        # plc.Write("<tag1>", value=instruction[1])
                        # plc.Write("<tag2>", value=instruction[2])
                        # plc.Write("<tag3>", value=instruction[3])
                        # plc.Write("<tag4>", value=instruction[4])

                        current_time = self.time_Q.get()

                if current_time == 0:
                    print("EXECUTION TIME:", time.time() - temp)
                    self.time_Q.get()
                    self.instruction_Q.get()
                    temp = time.time()
                    counter = 0

    def add(self, time, instruction):
        self.time_Q.put(time)
        self.instruction_Q.put(instruction)