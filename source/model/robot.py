import time

import cv2
import numpy as np
from scipy import integrate

from .point import Point
from .main_track import MainTrack
from .main_arm import MainArm 
from .secondary_arm import SecondaryArm
from .carriage import Carriage
from ..global_parameters import global_parameters

class Robot:

    #######################
    ### Basic Functions ###
    #######################

    def __init__(self, robot_base_pt, scale):
        self.scale = scale

        # Initializes robot parts 
        self.basePt = robot_base_pt
        self.main_track = MainTrack(self.basePt, scale)
        self.main_arm = MainArm(self.main_track.otherPt, scale)
        self.secondary_arm = SecondaryArm(self.main_arm.otherPt, scale)
        self.carriage1 = Carriage(self.secondary_arm.otherPt1, scale)
        self.carriage2 = Carriage(self.secondary_arm.otherPt2, scale)

        # Points the robot follows when update() is called 
        self.follow_pt1 = self.get_current_point(1)
        self.follow_pt2 = self.get_current_point(2)

        self.phase = 0
        self.switched = False
        self.delay = 0
        self.counter = 0
        self.phase_1_counter = 0

        self.profile_data = []
        self.xs = []
        self.acc_data = []
        self.vel_data = []
        self.recording = False

    def __repr__(self):
        ret = ""
        ret += "PHASE:" + str(self.phase) + "\n\t" + "Delay:" + str(self.delay) + "\n"
        ret += self.main_track.__repr__()
        ret += self.main_arm.__repr__()
        ret += self.secondary_arm.__repr__()
        ret += self.carriage2.__repr__()
        ret += self.carriage1.__repr__()
        return ret

    #########################
    ### Profile Functions ###
    #########################

    def scrap_data(self):
        self.recording = False
        self.phase = 0
        self.profile_data = []
        self.xs = []
        self.acc_data = []
        self.vel_data = []

    def confirm_acceleration(self):
        return True

    def get_current_state(self):
        ret = []
        
        ret += [self.main_track.length / global_parameters['VIDEO_SCALE']] # Main track extension
        ret += [self.main_arm.length / global_parameters['VIDEO_SCALE']] # Main arm extension
        ret += [self.main_arm.angle] # Main arm rotation 
        ret += [self.secondary_arm.length1 / global_parameters['VIDEO_SCALE']] # Secondary arm extension 1
        ret += [self.secondary_arm.length2 / global_parameters['VIDEO_SCALE']] # Secondary arm extension 2
        ret += [self.secondary_arm.relative_angle] # Secondary arm rotation 
        ret += [self.carriage1.relative_angle] # Carriage 1 rotation
        ret += [self.carriage2.relative_angle] # Carriage 2 rotation

        return ret

    def clear_history(self):
        self.profile_data = []

    def get_data(self):
        if not self.confirm_acceleration():
            self.scrap_data()
        return self.xs, self.profile_data, self.vel_data

    def gen_profiles(self):
        # Discrete data as derived from the model
        _, raw_pos_data, _ = self.get_data()
        if len(raw_pos_data) == 0:
            return False
        raw_vel_data = np.gradient(np.asarray(raw_pos_data), axis=0)
        
        # Integrated data. Closer representation of how robot will move 
        self.acc_data = np.gradient(raw_vel_data, axis=0)

        # Convert from per frame to per second
        self.acc_data = np.multiply(self.acc_data, global_parameters['FRAME_RATE'])

        if abs(np.amax(self.acc_data[:,[0, 1, 3, 4]])) > global_parameters['LINEAR_ACCELERATION_MAX']:
            print("Linear acceleration fault. Val:", np.amax(self.acc_data[:,[0, 1, 3, 4]]))
            print(self.acc_data[:,[0, 1, 3, 4]])
            return False
        if abs(np.amax(self.acc_data[:,[2, 5, 6, 7]])) > global_parameters['ROTATIONAL_ACCELERATION_MAX']:
            print("Rotational acceleration fault. Val:", np.amax(self.acc_data[:,[2, 5, 6, 7]]))
            print(self.acc_data[:,[2, 5, 6, 7]])
            return False

        self.vel_data = np.asarray([integrate.simps(self.acc_data[0:i+1], axis=0).tolist() for i in range(0, len(self.acc_data))])

        if abs(np.amax(self.vel_data[:,[0, 1, 3, 4]])) > global_parameters['LINEAR_VELOCITY_MAX']:
            print("Linear velocity fault. Val:", np.amax(self.vel_data[:,[0, 1, 3, 4]]))
            print(self.vel_data[:,[0, 1, 3, 4]])
            return False
        if abs(np.amax(self.vel_data[:,[2, 5, 6, 7]])) > global_parameters['ROTATIONAL_VELOCITY_MAX']:
            print("Rotational velocity fault. Val:", np.amax(self.vel_data[:,[2, 5, 6, 7]]))
            print(self.vel_data[:,[2, 5, 6, 7]])
            return False

        # Convert from change per frame to change
        # self.vel_data = np.multiply(self.vel_data, global_parameters['FRAME_RATE)
        # self.pos_data = np.add(np.asarray([integrate.simps(self.vel_data[0:i+1], axis=0).tolist() for i in range(0, len(self.vel_data))]), self.constants)

        return True

    ########################
    ### Helper Functions ###
    ########################

    def get_current_point(self, num):
        if num == 1:
            return Point(self.secondary_arm.otherPt1.x, self.secondary_arm.otherPt1.y, angle=self.carriage1.angle)
        elif num == 2:
            return Point(self.secondary_arm.otherPt2.x, self.secondary_arm.otherPt2.y, angle=self.carriage2.angle)

    def draw(self, canvas):
        self.main_track.draw(canvas)
        self.carriage1.draw(canvas, color=(0, 255, 0))
        self.carriage2.draw(canvas, color=(0, 0, 255))
        self.secondary_arm.draw(canvas)
        self.main_arm.draw(canvas)

        self.follow_pt1.draw(canvas, color=(0, 255, 0))
        self.follow_pt2.draw(canvas, color=(0, 0, 255))
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        y0, dy = 30, 18
        for i, line in enumerate(self.__repr__().split('\n')):
            y = y0 + i*dy
            try:
                if (line[0] == '\t'):
                    cv2.putText(canvas, line[1:], (25, y), font, 0.6, (150, 150, 0))
                else:
                    cv2.putText(canvas, line, (15, y), font, 0.6, (255, 255, 0))
            except:
                cv2.putText(canvas, line, (15, y), font, 0.6, (255, 255, 0))

    ##########################
    ### Movement Functions ###
    ##########################

    '''
        Phase 0: Not moving >> Phase 1 on Function call 
        Phase 1: Moving to predicted meat location >> Phase 2
        Phase 2: Grabbing >> Phase 3
        Phase 3: "Step 0" -> Rotating meat according to pre-set path >> Phase 4
        Phase 4: "Step 2" -> Extending >> Phase 5
        Phase 5: Releasing >> Phase 6
        Phase 6: Moving to "Ready Position" >> Phase 0
    '''

    def moveMeat(self, s1, s2, e1, e2, delay, counter=0, phase_1_delay=True):
        if self.phase != 0:
            print("ERROR: Robot in use")
            return False 
        
        self.s1 = s1
        self.s2 = s2
        self.e1 = e1
        self.e2 = e2
        self.phase = 1
        self.switched = True
        self.delay = delay
        self.counter = counter
        self.PHASE_1_DELAY = phase_1_delay

    def collision_check(self):
        ''' Checks all significant points and boundaries to see if a collision has occurred in a given state 
        
        How it works:
        - regions will be defined as no entry zones for specific heights
        - all relevant points will be run on a polygon inclusion algo to check if they fall within the regions 
        - any single collision at any height will return True 
        
        Points/Vects on robot to be considered (9):
        - four vectors for each carriage 
        - one vector for secondary arm 

        Points/Vects for no travel zones:
        - Carriages with themselves 
        - two defining top left corner (above and past the main arm) 
        - any additional environmental constraints 

        '''

        # Gather all relevant vectors 
        main_arm = self.main_arm.get_collision_bounds()
        secondary_arm = self.secondary_arm.get_collision_bounds()
        carriage1 = self.carriage1.get_collision_bounds()
        carriage2 = self.carriage2.get_collision_bounds()

        for i in range(0, len(main_arm)):
            # Check collision between secondary arm and main arm 
            for j in range(0, len(secondary_arm)):
                if self.check_vector_intersect(main_arm[i][0], main_arm[i][1], secondary_arm[j][0], secondary_arm[j][1]):
                    return True, "Collision between main arm and secondary arm"
            # Check collision between carriage1 and main arm
            for j in range(0, len(carriage1)):
                if self.check_vector_intersect(main_arm[i][0], main_arm[i][1], carriage1[j][0], carriage1[j][1]):
                    return True, "Collision between main arm and carriage1"
            # Check collision between carriage2 and main arm
            for j in range(0, len(carriage2)):
                if self.check_vector_intersect(main_arm[i][0], main_arm[i][1], carriage2[j][0], carriage2[j][1]):
                    return True, "Collision between main arm and carriage2"
        # Check collisions between carriages
        for i in range(0, len(carriage1)):
            for j in range(0, len(carriage2)):
                if self.check_vector_intersect(carriage1[i][0], carriage1[i][1], carriage2[j][0], carriage2[j][1]):
                    return True, "Collision between carriage1 and carriage2"
            
        return False, ""

    def check_vector_intersect(self, p, r, q, s):
        temp1 = np.subtract(q, p)
        temp2 = np.cross(r, s)

        if temp2 == 0:
            return False

        u = np.cross(temp1, r) / temp2
        t = np.cross(temp1, s) / temp2

        if u <= 0 or u >= 1 or t <= 0 or t >= 1:
            return False

        return True

    def moveTo(self, pt1, pt2):
        # First moves all the components to the desired points
        self.carriage1.follow(pt1)
        self.carriage2.follow(pt2)
        self.secondary_arm.follow(pt1, pt2)
        self.main_arm.follow(self.secondary_arm.basePt, self.secondary_arm.angle)
        self.main_track.follow(self.main_arm.basePt)

        # Then restricts movements by translating constrained points back 
        self.main_track.moveBase(self.basePt)
        self.main_arm.moveBase(self.main_track.otherPt)
        self.secondary_arm.moveBase(self.main_arm.otherPt, self.main_arm.angle)
        self.carriage1.moveBase(self.secondary_arm.otherPt1, self.secondary_arm.angle)
        self.carriage2.moveBase(self.secondary_arm.otherPt2, self.secondary_arm.angle)

    def followPath(self, path1, path2, execution_time):
        self.follow1_index = 0
        self.follow2_index = 0

        self.path1 = path1
        self.path2 = path2

        self.dt1 = []
        for i in range(0, len(path1)-1):
            self.dt1 += [(path1[i + 1] - path1[i]).mag()]
        self.dt2 = []
        for i in range(0, len(path2)-1):
            self.dt2 += [(path2[i + 1] - path2[i]).mag()]

        dt1_sum = np.sum(self.dt1)
        dt2_sum = np.sum(self.dt2)

        longest = max(dt1_sum, dt2_sum)

        self.dt1 = np.divide(np.multiply(self.dt1, execution_time), longest)
        self.dt2 = np.divide(np.multiply(self.dt2, execution_time), longest)

    def update(self):
        self.counter += 1
        # Phase 0: Not moving, in ready position
        if self.phase == 0:
            return False

        self.follow_pt1.update()
        self.follow_pt2.update()

        # Phase 1: Moving to predicted meat location
        if self.phase == 1:
            self.delay -= 1 # Delay here tracks time until meat is at start points 
            self.phase_1_counter += 1
            if self.switched:
                if self.recording:
                    self.profile_data += [self.get_current_state()]
                    self.profile_data += [self.get_current_state()]
                # self.counter = 0
                self.switched = False
                self.follow_pt1.moveTo(self.s1, global_parameters['PHASE_1_SPEED'])
                self.follow_pt2.moveTo(self.s2, global_parameters['PHASE_1_SPEED'])
                self.phase_1_counter = 0
            if self.follow_pt1.steps_remaining <= 1 and self.follow_pt2.steps_remaining <= 1 and self.delay < 1 and self.PHASE_1_DELAY: # End of step condition 
                self.switched = True 
                self.phase = 2
            if self.follow_pt1.steps_remaining <= 1 and self.follow_pt2.steps_remaining <= 1 and not self.PHASE_1_DELAY: # End of step condition 
                self.switched = True 
                self.phase = 2

        # Phase 2: Grabbing (Follow meat)
        if self.phase == 2:
            self.delay -= 1
            if self.switched:
                self.switched = False
                self.delay = global_parameters['PHASE_2_DELAY']
                self.follow_pt1.moveTo(self.follow_pt1 + Point(0, self.delay * global_parameters['CONVEYOR_SPEED']), global_parameters['PHASE_2_DELAY'])
                self.follow_pt2.moveTo(self.follow_pt2 + Point(0, self.delay * global_parameters['CONVEYOR_SPEED']), global_parameters['PHASE_2_DELAY'])
            if self.delay <= 1: # End of step condition 
                self.switched = True 
                self.phase = 3
            

        # Phase 3: "Step 0" -> Rotating meat according to pre-set path
        if self.phase == 3:
            if self.switched:
                self.switched = False
                self.followPath(global_parameters['PHASE_3_PATH1'], global_parameters['PHASE_3_PATH2'], global_parameters['PHASE_3_SPEED'])
                self.follow_pt1.moveTo(global_parameters['PHASE_3_PATH1'][0], global_parameters['PHASE_3_INITIAL_SPEED'])
                self.follow_pt2.moveTo(global_parameters['PHASE_3_PATH2'][0], global_parameters['PHASE_3_INITIAL_SPEED'])
                self.follow1_index = 0
                self.follow2_index = 0

            # End condition 
            if self.follow_pt1.steps_remaining <= 1 and self.follow_pt2.steps_remaining <= 1 \
                and self.follow1_index >= len(global_parameters['PHASE_3_PATH1'])-1 \
                    and self.follow2_index >= len(global_parameters['PHASE_3_PATH2'])-1: 
                self.switched = True 
                self.phase = 4

                #Stops robot in its tracks
                self.follow_pt1.moveTo(self.follow_pt1, 1)
                self.follow_pt2.moveTo(self.follow_pt2, 1)

            if self.follow_pt1.steps_remaining <= 1 and self.follow1_index < len(global_parameters['PHASE_3_PATH1']) - 1:
                self.follow1_index += 1
                self.follow_pt1.moveTo(global_parameters['PHASE_3_PATH1'][self.follow1_index], self.dt1[self.follow1_index - 1])
            if self.follow_pt2.steps_remaining <= 1 and self.follow2_index < len(global_parameters['PHASE_3_PATH2']) - 1:
                self.follow2_index += 1
                self.follow_pt2.moveTo(global_parameters['PHASE_3_PATH2'][self.follow2_index], self.dt2[self.follow2_index - 1])

        # Phase 4: "Step 2" -> Extending
        if self.phase == 4:
            if self.switched:
                self.switched = False
                self.follow_pt1.moveTo(self.e1, global_parameters['PHASE_4_SPEED'])
                self.follow_pt2.moveTo(self.e2, global_parameters['PHASE_4_SPEED'])
            if self.follow_pt1.steps_remaining <= 1 and self.follow_pt2.steps_remaining <= 1: # End of step condition 
                self.switched = True 
                self.phase = 5

        # Phase 5: Releasing
        if self.phase == 5:
            self.delay -= 1
            if self.switched:
                self.switched = False
                self.delay = global_parameters['PHASE_5_DELAY']
            if self.delay <= 0: # End of step condition 
                self.switched = True 
                self.phase = 6

        # Phase 6: Moving to "Ready Position"
        if self.phase == 6:
            self.delay -= 1
            if self.switched:
                self.switched = False
                self.delay = round(np.sum(self.dt1))//3
                self.followPath(global_parameters['PHASE_6_PATH1'], global_parameters['PHASE_6_PATH2'], global_parameters['PHASE_6_SPEED']-self.delay)
                self.follow1_index = 0
                self.follow2_index = 0

            # End condition 
            if self.follow_pt1.steps_remaining <= 1 and self.follow_pt2.steps_remaining <= 1 \
                and self.follow1_index >= len(global_parameters['PHASE_6_PATH1']) - 1 \
                    and self.follow2_index >= len(global_parameters['PHASE_6_PATH2']) - 1: 
                self.switched = True 
                self.phase = 0

                #Stops robot in its tracks
                self.follow_pt1.moveTo(self.follow_pt1, 1)
                self.follow_pt2.moveTo(self.follow_pt2, 1)

            if self.follow_pt1.steps_remaining <= 1 and self.follow1_index < len(global_parameters['PHASE_6_PATH1']) - 1:
                self.follow1_index += 1
                self.follow_pt1.moveTo(global_parameters['PHASE_6_PATH1'][self.follow1_index], self.dt1[self.follow1_index - 1])
            if self.follow_pt2.steps_remaining <= 1 and self.follow2_index < len(global_parameters['PHASE_6_PATH2']) - 1 \
                and self.delay <= 0:
                self.follow2_index += 1
                self.follow_pt2.moveTo(global_parameters['PHASE_6_PATH2'][self.follow2_index], self.dt2[self.follow2_index - 1])

        self.moveTo(self.follow_pt1, self.follow_pt2)

        # frame = np.zeros([1200, 1200, 3])
        # self.draw(frame)
        # cv2.imshow("Temp", frame)
        # cv2.waitKey(0)

        flag, report = self.collision_check()
        if flag:
            # If a collision occured in this step, turn off recording so that it is not added to the recommended path.
            # Resets robot to phase 0. Stops current path.
            print("ERROR: Profile resulted in collision and was not sent.")
            print(report)
            self.scrap_data()
            # cv2.waitKey(0)
            return False

        if self.recording:
            self.profile_data += [self.get_current_state()]
            if self.phase == 0: # This only ever hits immediately after phase 6
                self.profile_data += [self.get_current_state()]
                self.profile_data += [self.get_current_state()]

        return True

    def run(self, read_time, dist):
        self.clear_history()
        self.recording = True

        counter = 0
        self.xs = []
        self.xs += [read_time - 2 / global_parameters['FRAME_RATE']]
        self.xs += [read_time - 1 / global_parameters['FRAME_RATE']]
        while self.update():
            self.xs += [read_time + counter / global_parameters['FRAME_RATE']]
            counter += 1
        self.xs += [read_time + counter / global_parameters['FRAME_RATE']]
        counter += 1
        self.xs += [read_time + counter / global_parameters['FRAME_RATE']]
        counter += 1

        # c accounts for the time after the robot has moved into position but before it grabs the meat
        c = (dist / global_parameters['CONVEYOR_SPEED'] - self.phase_1_counter) / global_parameters['FRAME_RATE']
        self.xs = [self.xs[i] + c for i in range(0, len(self.xs))]

        self.recording = False