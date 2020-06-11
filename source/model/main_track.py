import math

import cv2

from .point import Point
from ..global_parameters import global_parameters

class MainTrack:
    def __init__(self, pt:Point, scale, length=0.1):
        ''' Input parameter units: m '''
        self.scale = scale
        self.base_pt = pt
        self.length = length
        self.last_pos = self.length
        self.delta_pos = 0
        self.min_length = global_parameters['MAIN_TRACK_MIN_LENGTH']
        self.max_length = global_parameters['MAIN_TRACK_MAX_LENGTH']
        self.other_pt = self.get_other_pt()

    def __repr__(self):
        return "Main Track\n\tExtension " + str(round(self.length, 3)) + "m\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n"

    def get_other_pt(self):
        return Point(self.base_pt.x, self.base_pt.y - self.length)

    def get_min_pt_vector(self):
        return Point(self.base_pt.x, self.base_pt.y - self.min_length)
    def get_max_pt_vector(self):
        return Point(self.base_pt.x, self.base_pt.y - self.max_length)

    def draw(self, canvas):
        cv2.line(canvas, (self.get_max_pt_vector() * self.scale).to_drawing_tuple(), (self.base_pt * self.scale).to_drawing_tuple(), (255, 255, 255), 8) 
        cv2.line(canvas, (self.get_max_pt_vector() * self.scale).to_drawing_tuple(), (self.get_min_pt_vector() * self.scale).to_drawing_tuple(), (0, 0, 0), 3) 
        cv2.circle(canvas, (self.other_pt * self.scale).to_drawing_tuple(), self.scale//10, (255, 255, 255))
    
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

        self.delta_pos = self.length - self.last_pos
        self.last_pos = self.length

    def move_base(self, pt:Point):
        self.base_pt = pt
        self.other_pt = self.get_other_pt()

    def set_model_state(self, state, vel_toggle=False):
        '''
            state = length 
        '''
        if vel_toggle:
            self.__init__(self.base_pt, self.scale, length=self.length + state / global_parameters['FRAME_RATE'])
        else:
            self.__init__(self.base_pt, self.scale, length=state)
            
