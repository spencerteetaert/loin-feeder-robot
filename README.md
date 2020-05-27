# loin-feeder-robot

This project is to design the control systems for a robot that feeds the loin puller at Hylife Foods Ltd. The mechanical design for this system was done by a team of student from the University of Manitoba (Christopher Mckay, Zheng Fan, Dylan Van Deynze, David Lubi). 

This software aims at solving three challenges:
* Develop a vision system that allows the robot to determine the size, orientation, and proper cut line on travelling hogs. 
* Develop an algorithm that plans the actuator paths required to align the hogs in the proper orientation. 
* Program the appropriate PLCs to actuate the path determined on the physical build. 

## source
### model

This folder contains the necessary classes required for creating a digital model of the actual robot. 
* robot.py contains the robot class. It has all the functions required to move the robot using inverse kinematics. 

#### Test code: model_test.py

![Robot model implementation](/images/model.PNG)

### path_planning

This folder contains functions for path planning. The current algorithm uses the raw position information from the inverse kinematics of the model to derive an acceleration profile. When twice integrated, this profile will closely resemble how the robot will move. We can compare the raw position data to the integrated position data to determine the accuracy of this method. 

![Raw position data](/images/figure_o.PNG)![Integrated position data](/images/figure_i.PNG)

* graphing_tools.py contains a class to thread the graphing process. 
* path_runner.py contains a class to thread the path finder.
* path.py (Not in use) contains a path finding algorithm based off existing "safe paths".

#### Test code: path_finder_test.py

### vision_identification

This folder contains the tools needed for identifying pieces of product as they travel through a frame.
* bounding_box.py contains functions that given an image, can identify all the pieces of meat in the image and returns appropriate bounding boxes. 
* meat.py contains the meat class. This object determines important features of the meat to use in path planning.
* video_reader.py contains a video reader class. This class allows reading of video to be threaded to increase runtime efficiency. 

![Meat object identification](/images/meat_identified.PNG)

## tools 

Contains tools used for finding parameter values, testing functions, and timing optimization. 
* bbox_parameter_optimizer.py allows for fine tuning of HSV filter parameters using images of product.
* extend_data.py (Not in use) randomly distorts a collection of data. This was made with the thought of machine learning in mind. 
* from_vid.py accesses a video and implements a usage for the meat class. 
* get_colour_range.py allows users to specify a range of pixels over a range of images and returns the max/min values for HSV. 
* profiler.py runs a timing analysis on any file required. 