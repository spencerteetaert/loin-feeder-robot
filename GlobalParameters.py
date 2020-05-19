import sys
import numpy as np

###########################
### Physical Parameters ###
###########################

MAIN_TRACK_MIN_LENGTH = 10
MAIN_TRACK_MAX_LENGTH = 300
MAIN_ARM_MIN_LENGTH = 150
MAIN_ARM_MAX_LENGTH = 300

SECONDARY_ARM_MIN_LENGTH = 50
SECONDARY_ARM_MAX_LENGTH = 150

#########################
### Vision Parameters ###
#########################

MINIMUM_AREA = 40000 # Pixel area for an acceptable contour 

# LOWER_MASK = np.array([0, 51, 51]) # Default lower mask
# UPPER_MASK = np.array([15, 204, 255]) # Default upper mask
LOWER_MASK = np.array([0, 71, 99]) # Default lower mask
UPPER_MASK = np.array([9, 191, 212]) # Default upper mask

LOIN_WIDTH = 90 # How far from loin side to make cut in pixels
LINE_THRESHOLD = 200 # Distance between points to be considered a valid line 
SHORT_END_FACTOR = 0.35
CHANGING_START_INDEX = False # Toggles whether to iterated start indeces 