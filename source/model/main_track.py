import math

import cv2

from .point import Point
from ..global_parameters import global_parameters

class MainTrack:
    def __init__(self, pt:Point, scale, length=0.1):
        self.scale = scale
        self.base_pt = pt
        self.length = length * scale
        self.last_pos = self.length/self.scale
        self.delta_pos = 0
        self.min_length = global_parameters['MAIN_TRACK_MIN_LENGTH'] * scale
        self.max_length = global_parameters['MAIN_TRACK_MAX_LENGTH'] * scale
        self.other_pt = self.get_other_pt()

    def __repr__(self):
        return "Main Track\n\tExtension " + str(round(self.length/self.scale, 3)) + "m\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n"

    def get_other_pt(self):
        return Point(self.base_pt.x, self.base_pt.y - self.length)

    def get_min_pt_vector(self):
        return Point(round(self.base_pt.x), round(self.base_pt.y - self.min_length))
    def get_max_pt_vector(self):
        return Point(round(self.base_pt.x), round(self.base_pt.y - self.max_length))

    def draw(self, canvas):
        cv2.line(canvas, self.get_max_pt_vector().to_tuple(), self.base_pt.to_tuple(), (255, 255, 255), 8) 
        cv2.line(canvas, self.get_max_pt_vector().to_tuple(), self.get_min_pt_vector().to_tuple(), (0, 0, 0), 3) 
        cv2.circle(canvas, self.other_pt.to_tuple(), self.scale//10, (255, 255, 255))
    
    def follow(self, pt:Point):
        dr = self.base_pt.y - pt.y 
        if dr <= self.min_length:
            self.length = self.min_length
        elif dr <= self.max_length:
            self.length = dr
        else:
            self.length = self.max_length

        self.other_pt = Point(self.base_pt.x, pt.y)
        self.base_pt = Point(self.other_pt.x, self.other_pt.y + self.length)

        self.delta_pos = self.length/self.scale - self.last_pos
        self.last_pos = self.length/self.scale

    def move_base(self, pt:Point):
        self.base_pt = pt
        self.other_pt = self.get_other_pt()

    def set_model_state(self, state):
        '''
            state = length 
        '''
        self.__init__(self.base_pt, self.scale, length=state)
