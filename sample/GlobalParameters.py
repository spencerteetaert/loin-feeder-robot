import sys

import numpy as np

###########################
### Physical Parameters ###
###########################

# In meters
MAIN_TRACK_MIN_LENGTH = 0
MAIN_TRACK_MAX_LENGTH = 1.236

MAIN_ARM_MIN_LENGTH = 0.695
MAIN_ARM_MAX_LENGTH = 1.089
MAIN_ARM_MIN_ANGLE = 200
MAIN_ARM_MAX_ANGLE = 340

SECONDARY_ARM_MIN_LENGTH = 0.354
SECONDARY_ARM_MAX_LENGTH = 0.973

CARRIAGE_LENGTH = 0.875
CARRIAGE_WIDTH = 0.406

#########################
### Vision Parameters ###
#########################

VIDEO_SCALE = 212

MINIMUM_AREA = 8000 # Pixel area for an acceptable contour 

# LOWER_MASK = np.array([0, 51, 51]) # Default lower mask
# UPPER_MASK = np.array([15, 204, 255]) # Default upper mask
LOWER_MASK = np.array([0, 71, 99]) # Default lower mask
UPPER_MASK = np.array([9, 191, 212]) # Default upper mask

LOIN_WIDTH = 45 # How far from loin side to make cut in pixels
LINE_THRESHOLD = 100 # Distance between points to be considered a valid line 
SHORT_END_FACTOR = 0.35
CHANGING_START_INDEX = False # Toggles whether to iterated start indeces 