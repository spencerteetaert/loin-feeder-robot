import math

import cv2
import numpy as np

from .point import Point
from ..global_parameters import global_parameters
from .. import vector_tools

class Carriage:
    def __init__(self, pt:Point, scale, angle=0, downward_extension=0, gripper_extension=0.5, relative_angle=90):
        ''' Input parameter units: m '''
        self.scale = scale
        self.base_pt = pt
        self.width = global_parameters['CARRIAGE_WIDTH']
        self.length = global_parameters['CARRIAGE_LENGTH']
        self.angle = angle 
        self.relative_angle = relative_angle
        self.other_pt = self.get_other_pt()
        self.downward_extension = downward_extension
        self.gripper_extension = gripper_extension

        self.last_angle = self.relative_angle
        self.delta_angle = 0

        self.hyp_dist = math.sqrt(self.length**2 + self.width**2)/2
        self.update_points()
        
    def __repr__(self):
        return "Carriage\n\tAngle " + str(round(self.relative_angle, 1)) + "\n\tdA " + str(round(self.delta_angle, 3)) + "\n" 

    def refresh(self, secondary_arm_angle=None):
        # self.angle = (self.otherPt - self.basePt).vector_angle()
        if secondary_arm_angle != None:
            self.relative_angle = (self.angle - secondary_arm_angle + 360 + 180) % 360

    def get_other_pt(self):
        return Point(self.base_pt.x + self.length * math.cos(math.radians(self.angle))/2, self.base_pt.y - self.length * math.sin(math.radians(self.angle))/2)

    def draw(self, canvas, color=(255, 255, 255)):  
        self.update_points()    
        contour = (np.array(self.points[0:4]) * self.scale).reshape((-1, 1, 2)).astype(np.int32)
        cv2.drawContours(canvas, [contour], 0, color, 2)
        cv2.line(canvas, (int(round(self.points[4][0] * self.scale)), int(round(self.points[4][1] * self.scale))), (int(round(self.points[5][0] * self.scale)), int(round(self.points[5][1] * self.scale))), color, 4)

    def follow(self, pt:Point):
        if pt.angle != None:
            self.angle = pt.angle

        self.delta_angle = self.relative_angle - self.last_angle
        self.last_angle = self.relative_angle
        
    def move_base(self, pt:Point, secondary_arm_angle):
        self.refresh(secondary_arm_angle)
        self.base_pt = pt
        self.update_points()

    def update_points(self):
        self.points = []

        k = np.array([self.length*math.cos(math.radians(self.angle))/2, -1 * self.length*math.sin(math.radians(self.angle))/2])
        x = vector_tools.get_normal_unit([0, 0], k)
        x1 = x * self.width/2
        x2 = x * self.gripper_extension

        self.points += [(self.base_pt.to_array() + k + x1)] # top right
        self.points += [(self.base_pt.to_array() + k - x1)] # top left
        self.points += [(self.base_pt.to_array() - k - x1)] # bottom left
        self.points += [(self.base_pt.to_array() - k + x1)] # bottom right 
        self.points += [(self.base_pt.to_array() + k - x1 + x2)] # gripper top right
        self.points += [(self.base_pt.to_array() - k - x1 + x2)] # gripper bottom right 
        self.other_pt = self.get_other_pt()

    def get_collision_bounds(self):
        r1 = np.subtract(self.points[1], self.points[2])
        if self.gripper_extension < global_parameters['CARRIAGE_WIDTH']:
            r2 = np.subtract(self.points[1], self.points[0]) 
            r3 = np.subtract(self.points[3], self.points[2])
            r4 = np.subtract(self.points[3], self.points[0])

            return [[self.points[1], r3], [self.points[1], r4], [self.points[3], r1], [self.points[3], r2]]
        else:
            r2 = np.subtract(self.points[1], self.points[4]) 
            r3 = np.subtract(self.points[5], self.points[2])
            r4 = np.subtract(self.points[5], self.points[4])
        
            return [[self.points[1], r3], [self.points[1], r4], [self.points[5], r1], [self.points[5], r2]]

    def set_model_state(self, state, vel_toggle=False):
        '''
            0: Secondary arm other pt
            1: Secondary arm abs angle
            2: Angle
            3: Raised/Lowered
            4: Gripper extension
        '''
        if vel_toggle:
            angle = (state[2] / global_parameters['FRAME_RATE'] + self.relative_angle + state[1] + 180 + 720) % 360
            self.__init__(state[0], self.scale, angle, self.downward_extension + state[3] / global_parameters['FRAME_RATE'], \
                self.gripper_extension + state[4] / global_parameters['FRAME_RATE'], self.relative_angle + state[2] / global_parameters['FRAME_RATE'])
        else:
            angle = (state[2] + state[1] + 180 + 720) % 360
            self.__init__(state[0], self.scale, angle, state[3], state[4])

    def close(self, width):
        if self.gripper_extension > width:
            self.gripper_extension -= global_parameters['GRIPPER_SPEED'] / global_parameters['FRAME_RATE']
            self.gripper_extension = max(self.gripper_extension, global_parameters['GRIPPER_MIN_EXTENSION'])

    def open(self):
        if self.gripper_extension < global_parameters['GRIPPER_MAX_EXTENSION']:
            self.gripper_extension += global_parameters['GRIPPER_SPEED'] / global_parameters['FRAME_RATE']
            self.gripper_extension = min(self.gripper_extension, global_parameters['GRIPPER_MAX_EXTENSION'])

    def lower(self):
        if self.downward_extension < global_parameters['DOWNWARD_MAX_EXTENSION']:
            self.downward_extension += global_parameters['DOWNWARD_SPEED'] / global_parameters['FRAME_RATE']
            self.downward_extension = min(self.downward_extension, global_parameters['DOWNWARD_MAX_EXTENSION'])

    def lift(self):
        if self.downward_extension > global_parameters['DOWNWARD_MIN_EXTENSION']:
            self.downward_extension -= global_parameters['DOWNWARD_SPEED'] / global_parameters['FRAME_RATE']
            self.downward_extension = max(self.downward_extension, global_parameters['DOWNWARD_MIN_EXTENSION'])