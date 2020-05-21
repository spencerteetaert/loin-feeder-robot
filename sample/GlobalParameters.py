import numpy as np

################################
### Path Planning Parameters ###
################################

RUNTIME_LIMIT = 300                                                         # Maximum number of path points before program breaks 
SAFE_ENVIRONMENT = [[[440, 190], [440, 730]], [[145, 735], [665, 735]], [[440, 600], [300, 735]], [[440, 600], [580, 735]]]#[[[440, 190], [440, 730]], [[145, 735], [665, 735]]]     # Lines that are safe to travel on

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

VIDEO_SCALE = 212                                       # Pixels / m 

MINIMUM_MIDDLE_SIZE = 0.18                              # Minimum middle size in m^2
MINIMUM_AREA = MINIMUM_MIDDLE_SIZE * VIDEO_SCALE**2     # Pixel area for an acceptable contour 

LOWER_MASK = np.array([0, 71, 99])      # Default lower mask
UPPER_MASK = np.array([9, 191, 212])    # Default upper mask

LOIN_WIDTH = 45                         # How far from loin side to make cut in pixels
LINE_THRESHOLD = 100                    # Distance between points to be considered a valid line 
SHORT_END_FACTOR = 0.35                 # Factor for short ends of hog
CHANGING_START_INDEX = False            # Toggles whether to iterated start indeces 