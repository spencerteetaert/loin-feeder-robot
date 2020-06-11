import math

import cv2
import numpy as np

from .point import Point
from ..global_parameters import global_parameters

class MainArm:
    def __init__(self, pt:Point, scale, length=0.75, angle=180):
        ''' Input parameter units: m '''
        self.scale = scale
        self.base_pt = pt
        self.length = length
        self.min_length = global_parameters['MAIN_ARM_MIN_LENGTH']
        self.max_length = global_parameters['MAIN_ARM_MAX_LENGTH']
        self.angle = angle 
        self.other_pt = self.get_other_pt()
        self.refresh()

        self.last_pos = 0
        self.delta_pos = self.length - self.last_pos
        self.last_angle = 0
        self.delta_angle = self.angle - self.last_angle

    def __repr__(self):
        return "Main Arm\n\tExtension " + str(round(self.length, 3)) + "m\n\tAngle " + str(round(self.angle, 1)) + "\n\tdL " + str(round(self.delta_pos, 3)) + "m/frame\n\tdA " + str(round(self.delta_angle, 3)) + "\n" 

    def refresh(self):
        self.angle = ((self.other_pt - self.base_pt).vector_angle() + 180) % 360

    def get_other_pt(self):
        return Point(self.base_pt.x - self.length * math.cos(math.radians(self.angle)), self.base_pt.y + self.length * math.sin(math.radians(self.angle)))

    def get_min_pt_vector(self):
        return Point(self.base_pt.x - self.min_length * math.cos(math.radians(self.angle)), self.base_pt.y + self.min_length * math.sin(math.radians(self.angle)))
    def get_max_pt_vector(self):
        return Point(self.base_pt.x - self.max_length * math.cos(math.radians(self.angle)), self.base_pt.y + self.max_length * math.sin(math.radians(self.angle)))

    def draw(self, canvas):
        cv2.line(canvas, (self.get_max_pt_vector() * self.scale).to_drawing_tuple(), (self.base_pt * self.scale).to_drawing_tuple(), (255, 255, 255), 8) 
        cv2.line(canvas, (self.get_max_pt_vector() * self.scale).to_drawing_tuple(), (self.get_min_pt_vector() * self.scale).to_drawing_tuple(), (0, 0, 0), 3) 
        cv2.circle(canvas, (self.other_pt * self.scale).to_drawing_tuple(), self.scale//15, (255, 255, 255))
    
    def follow(self, pt:Point, secondary_arm_angle):
        dr = pt - self.base_pt
        if dr.mag() <= self.min_length:
            self.length = self.min_length
        elif dr.mag() <= self.max_length:
            self.length = dr.mag()
        else:
            self.length = self.max_length

        self.other_pt = pt
        self.base_pt = self.other_pt - dr.norm() * self.length

        # Rotational bounds 
        self.refresh()
        rel_angle = (secondary_arm_angle - self.angle + 360) % 360 
        if rel_angle < global_parameters['MAIN_ARM_MIN_ANGLE']:
            self.base_pt.rotate(global_parameters['MAIN_ARM_MIN_ANGLE'] - rel_angle, self.other_pt)
        elif rel_angle > global_parameters['MAIN_ARM_MAX_ANGLE']:
            self.base_pt.rotate(global_parameters['MAIN_ARM_MAX_ANGLE'] - rel_angle, self.other_pt)

        self.delta_pos = self.length - self.last_pos
        self.last_pos = self.length
        self.delta_angle = self.angle - self.last_angle
        self.last_angle = self.angle

    def move_base(self, pt:Point):
        self.refresh()
        self.base_pt = pt
        self.other_pt = self.get_other_pt()

    def get_collision_bounds(self):
        p = np.add(self.base_pt.to_array(), [global_parameters['MAIN_ARM_WIDTH'], global_parameters['MAIN_ARM_WIDTH']])
        r1 = np.array([0, -1000])
        r2 = np.array([-1000, 0])

        return [[p, r1], [p, r2]]

    def set_model_state(self, state, vel_toggle=False):
        '''
            0: Main track other pt
            1: Length
            2: Angle
        '''
        if vel_toggle:
            self.__init__(state[0], self.scale, self.length + state[1] / global_parameters['FRAME_RATE'], self.angle + state[2] / global_parameters['FRAME_RATE'])
        else:
            self.__init__(state[0], self.scale, state[1], state[2])