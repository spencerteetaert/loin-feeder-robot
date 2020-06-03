import numpy as np

from .model.point import Point

################################
### Communication Parameters ###
################################

PLC_IP = "10.86.4.24"
CAMERA_IP = "10.86.4.24"

#########################
### Vision Parameters ###
#########################

VIDEO_SCALE = 212                                       # Pixels / m 
RUNTIME_FACTOR = 1
FRAME_RATE = 30 * RUNTIME_FACTOR

MINIMUM_MIDDLE_SIZE = 0.18                              # Minimum middle size in m^2
MINIMUM_AREA = MINIMUM_MIDDLE_SIZE * VIDEO_SCALE**2     # Pixel area for an acceptable contour 

LOWER_MASK = np.array([0, 71, 99])      # Default lower mask
UPPER_MASK = np.array([9, 191, 212])    # Default upper mask

BOUNDING_BOX_THESHOLD = 10
LOIN_WIDTH = 0.021                      # How far from loin side to make cut in pixels
LINE_THRESHOLD = 100                    # Distance between points to be considered a valid line 
SHORT_END_FACTOR = 0.35                 # Factor for short ends of hog
CHANGING_START_INDEX = False            # Toggles whether to iterated start indeces 


################################
### Path Planning Parameters ###
################################

CONVEYOR_SPEED = 2 / RUNTIME_FACTOR #Px/frame
RUNTIME_LIMIT = 300 # Maximum number of path points before program breaks 
SAFE_ENVIRONMENT = [[[440, 190], [440, 730]], [[100, 735], [800, 735]], [[440, 600], [300, 735]], [[440, 600], [580, 735]]]#[[[440, 190], [440, 730]], [[145, 735], [665, 735]]]     # Lines that are safe to travel on

# Points 
READY_POS_1 = Point(439, 504, angle=0)
READY_POS_2 = Point(439, 654, angle=0)
PICKUP_POINT = Point(440, 504)
END_POINT_1 = Point(625, 735, angle=90)
END_POINT_2 = Point(250, 735, angle=90)

# Phase Parameters 
'''
    Phase 0: Not moving >> Phase 1 on Function call 
    Phase 1: Moving to predicted meat location >> Phase 2
    Phase 2: Grabbing >> Phase 3
    Phase 3: "Step 0" -> Rotating meat according to pre-set path >> Phase 4
    Phase 4: "Step 2" -> Extending >> Phase 5
    Phase 5: Releasing >> Phase 6
    Phase 6: Moving to "Ready Position" >> Phase 0
'''

TOTAL_EXECUTION_TIME = 6
PHASE_1_PERCENTAGE = 0.096
PHASE_2_PERCENTAGE = 0.048
PHASE_3_1_PERCENTAGE = 0.116
PHASE_3_2_PERCENTAGE = 0.269
PHASE_4_PERCENTAGE = 0.135
PHASE_5_PERCENTAGE = 0.048
PHASE_6_PERCENTAGE = 0.288

PHASE_1_SPEED = PHASE_1_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE

PHASE_2_DELAY = PHASE_2_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE

PHASE_3_PATH1 = [Point(440, 435, angle=60), Point(440, 580, angle=110), Point(530, 680, angle=90)]
PHASE_3_PATH2 = [Point(440, 730, angle=60), Point(320, 720, angle=110)]
PHASE_3_SPEED = PHASE_3_2_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE
PHASE_3_INITIAL_SPEED = PHASE_3_1_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE

PHASE_4_SPEED = PHASE_4_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE

PHASE_5_DELAY = PHASE_5_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE

# CONDITION: Last point must be Ready Pos 
PHASE_6_PATH1 = [Point(450, 435, angle=0), READY_POS_1]
PHASE_6_PATH2 = [Point(345, 695, angle=0), READY_POS_2]
PHASE_6_SPEED = PHASE_6_PERCENTAGE * TOTAL_EXECUTION_TIME * FRAME_RATE

###########################
### Physical Parameters ###
###########################

ROBOT_BASE_POINT = Point(280, 600)

# In meters
MAIN_TRACK_MIN_LENGTH = 0
MAIN_TRACK_MAX_LENGTH = 1.236

MAIN_ARM_WIDTH = 0.2

MAIN_ARM_MIN_LENGTH = 0.695
MAIN_ARM_MAX_LENGTH = 1.089
MAIN_ARM_MIN_ANGLE = 200
MAIN_ARM_MAX_ANGLE = 340

SECONDARY_ARM_MIN_LENGTH = 0.354
SECONDARY_ARM_MAX_LENGTH = 0.973

CARRIAGE_LENGTH = 0.875
CARRIAGE_WIDTH = 0.406