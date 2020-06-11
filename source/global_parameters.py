import numpy as np
import pickle
from datetime import datetime

'''
    Running this file directly will save the current settings. 
'''

if __name__=="__main__":
    from model.point import Point
else:
    from .model.point import Point

now = datetime.now()
dt_string = now.strftime("-%d%m%Y-%H%M%S")
EXPORT_FILE_PATH = "resources\configs\main" + dt_string

params_1 = { # Parameters 
    ################################
    ### Communication Parameters ###
    ################################

    "PLC_IP" : "10.86.4.24",
    "CAMERA_IP" : "10.86.4.24",

    #########################
    ### Vision Parameters ###
    #########################

    "VIDEO_SCALE" : 212,                                       # Pixels / m 
    "RUNTIME_FACTOR" : 1.2,
    "FPS" : 30, 

    "MINIMUM_MIDDLE_SIZE" : 0.18,                              # Minimum middle size in m^2

    # "LOWER_MASK" : np.array([0, 71, 99]),      # Default lower mask
    # "UPPER_MASK" : np.array([9, 191, 212]),    # Default upper mask
    "LOWER_MASK" : np.array([0, 100, 98]),      # Default lower mask
    "UPPER_MASK" : np.array([21, 194, 236]),    # Default upper mask

    "BOUNDING_BOX_THESHOLD" : 10,
    "LOIN_WIDTH" : 0.021,                      # How far from loin side to make cut in pixels
    "LINE_THRESHOLD" : 100,                    # Distance between points to be considered a valid line 
    "SHORT_END_FACTOR" : 0.35,                 # Factor for short ends of hog
    "CHANGING_START_INDEX" : False,            # Toggles whether to iterated start indeces 


    ################################
    ### Path Planning Parameters ###
    ################################

    "RUNTIME_LIMIT" : 300, # Maximum number of path points before program breaks 

    "ROTATIONAL_ACCELERATION_MAX" : 360, # °/s^2
    "LINEAR_ACCELERATION_MAX" : 10, # m/s^2
    "ROTATIONAL_VELOCITY_MAX" : 360, # °/s
    "LINEAR_VELOCITY_MAX" : 1.5, # m/s
    "GRIPPER_SPEED" : 0.5, #m/s
    "DOWNWARD_SPEED" : 1, #m/s

    # Points 
    "READY_POS1" : Point(2.071, 2.377, angle=0),
    "READY_POS2" : Point(2.071, 3.085, angle=0),
    "PICKUP_POINT1" : Point(2.075, 2.170),
    "PICKUP_POINT2" : Point(2.075, 3.113),
    "END_POINT1" : Point(2.948, 3.467, angle=90),
    "END_POINT2" : Point(1.179, 3.467, angle=90),

    "SAFE_ENVIRONMENT" : [[[440, 190], [440, 730]], [[100, 735], [800, 735]], [[440, 600], [300, 735]], [[440, 600], [580, 735]]],

    # Phase Parameters 
    "TOTAL_EXECUTION_TIME" : 5.2,
    "PHASE_1_PERCENTAGE" : 0.096,
    "PHASE_2_PERCENTAGE" : 0.048,
    "PHASE_3_1_PERCENTAGE" : 0.116,
    "PHASE_3_2_PERCENTAGE" : 0.269,
    "PHASE_4_PERCENTAGE" : 0.135,
    "PHASE_5_PERCENTAGE" : 0.048,
    "PHASE_6_PERCENTAGE" : 0.288,

    "PHASE_3_PATH1" : [Point(2.075, 2.052, angle=60), Point(2.075, 2.736, angle=110), Point(2.500, 3.208, angle=90)],
    "PHASE_3_PATH2" : [Point(2.075, 3.443, angle=60), Point(1.509, 3.396, angle=110)],

    ###########################
    ### Physical Parameters ###
    ###########################

    "ROBOT_BASE_POINT" : Point(1.321, 2.830),

    # In meters
    "MAIN_TRACK_MIN_LENGTH" : 0,
    "MAIN_TRACK_MAX_LENGTH" : 1.236,

    "MAIN_ARM_WIDTH" : 0.2,

    "MAIN_ARM_MIN_LENGTH" : 0.695,
    "MAIN_ARM_MAX_LENGTH" : 1.089,
    "MAIN_ARM_MIN_ANGLE" : 200,
    "MAIN_ARM_MAX_ANGLE" : 340,

    "SECONDARY_ARM_MIN_LENGTH" : 0.354,
    "SECONDARY_ARM_MAX_LENGTH" : 0.973,

    "CARRIAGE_LENGTH" : 0.875,
    "CARRIAGE_WIDTH" : 0.406,
    "GRIPPER_MAX_EXTENSION" : 0.5,
    "GRIPPER_MIN_EXTENSION" : 0.3,
    "DOWNWARD_MAX_EXTENSION" : 0.2, 
    "DOWNWARD_MIN_EXTENSION" : 0.02
}

params_2 = {
    "FRAME_RATE" : params_1['FPS'] * params_1['RUNTIME_FACTOR'],
    "MINIMUM_AREA" : params_1['MINIMUM_MIDDLE_SIZE'] * params_1['VIDEO_SCALE']**2,     # Pixel area for an acceptable contour 

    "PHASE_6_PATH1" : [Point(2.123, 2.052, angle=0), params_1['READY_POS1']],
    "PHASE_6_PATH2" : [Point(1.627, 3.278, angle=0), params_1['READY_POS2']]
}

params_3 = {
    "CONVEYOR_SPEED" : 9.434e-3 * params_2['FRAME_RATE'], #m/s

    "PHASE_1_SPEED" : params_1['PHASE_1_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE'],
    "PHASE_2_DELAY" : params_1['PHASE_2_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE'],
    "PHASE_3_SPEED" : params_1['PHASE_3_2_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE'],
    "PHASE_3_INITIAL_SPEED" : params_1['PHASE_3_1_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE'],
    "PHASE_4_SPEED" : params_1['PHASE_4_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE'],
    "PHASE_5_DELAY" : params_1['PHASE_5_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE'],
    "PHASE_6_SPEED" : params_1['PHASE_6_PERCENTAGE'] * params_1['TOTAL_EXECUTION_TIME'] * params_2['FRAME_RATE']
}

global_parameters = {**{**params_1, **params_2}, **params_3}


def set_parameters(file_path):
    global global_parameters
    try:
        f = open(file_path, 'rb')
        data = pickle.load(f)
        global_parameters = data
        f.close()
    except:
        print("ERROR: Invalid configuration file.")

def save_parameters(file_path):
    f = open(file_path, 'wb')
    pickle.dump(global_parameters, f)
    f.close()

    print("Current configuration saved to:",file_path)

if __name__=="__main__":
    save_parameters(EXPORT_FILE_PATH)