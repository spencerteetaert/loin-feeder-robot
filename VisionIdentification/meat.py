import numpy as np

class Meat():
    def __init__(self, conveyor_speed=0, side="Left", bbox=[]):
        self.conveyor_speed = conveyor_speed
        self.side = side
        self.bbox = bbox

        self.loin_line = self.gen_significant_lines("loin")
        self.shoulder_line = self.gen_significant_lines("shoulder")
        self.ham_line = self.gen_significant_lines("ham")
        self.flank_line = self.gen_significant_lines("flank")
        self.cut_line = self.gen_significant_lines("cut")

    def __repr__(self):
        t1 = self.side + " piece\n"
        t2 = "Velocity: " + str(self.conveyor_speed) + "px/frame\n"
        t3 = repr(self.bbox) + "\n"
        return t1 + t2 + t3

    def step(self):
        '''
        Tranlsates every stored point by the conveyor speed
        '''
        step_vec = np.array([self.conveyor_speed, 0])
        self.bbox = self.bbox + step_vec
        self.loin_line = self.loin_line + step_vec
        self.shoulder_line = self.shoulder_line + step_vec
        self.ham_line = self.ham_line + step_vec
        self.flank_line = self.flank_line + step_vec
        self.cut_line = self.cut_line + step_vec

    def gen_significant_lines(self, line):
        return 0