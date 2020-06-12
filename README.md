# loin-feeder-robot

This project is to design the control systems for a robot that feeds the loin puller at Hylife Foods Ltd. The mechanical design for this system was done by a team of student from the University of Manitoba (Christopher Mckay, Zheng Fan, Dylan Van Deynze, David Lubi). 

This software aims at solving three challenges:
* Develop a vision system that allows the robot to determine the size, orientation, and proper cut line on travelling hogs. 
* Develop an algorithm that plans the actuator paths required to align the hogs in the proper orientation. 
* Program the appropriate PLCs to actuate the path determined on the physical build. 

## source
### data_send_receive 

This folder contains code that aids in sending/receiving data from a PLC/server as required. 
* instruction_handler.py is a script that ensures commands are sent at the required time to achieve the expected robot motion. 

### model

This folder contains the necessary classes required for creating a digital model of the actual robot. 
* robot.py contains the robot class. It has all the functions required to move the robot using inverse kinematics. 

#### Test code: model_test.py

<img src="/resources/images/model.PNG" width="500" height="500">

### path_planning

This folder contains functions for path planning. The current algorithm uses the raw position information from the inverse kinematics of the model to derive an acceleration profile. When twice integrated, this profile will closely resemble how the robot will move. We can compare the raw position data to the integrated position data to determine the accuracy of this method. 

Raw position data          |  Integrated position data
:-------------------------:|:-------------------------:
![](/resources/images/figure_o.png)  |  ![](/resources/images/figure_i.png)

* frame_handler.py contains functionality to handle frames as produced by a triggered camera. Given two images, and some time between them, the script identifies their location and produces the required motion profiles to achieve the desired path. 
* graphing_tools.py contains a class to thread the graphing process. 
* path_runner.py contains a class to thread the path finder.
* path.py (Not in use) contains a path finding algorithm based off existing "safe paths".

#### Test code: path_finder_test.py

### vision_identification

This folder contains the tools needed for identifying pieces of product as they travel through a frame.
* bounding_box.py contains functions that given an image, can identify all the pieces of meat in the image and returns appropriate bounding boxes. 
* meat.py contains the meat class. This object determines important features of the meat to use in path planning.
* video_reader.py contains a video reader class. This class allows reading of video to be threaded to increase runtime efficiency. 

![Meat object identification](/resources/images/meat_identified.PNG)

## tools 

Contains tools used for finding parameter values, testing functions, and timing optimization. 
* bbox_parameter_optimizer.py allows for fine tuning of HSV filter parameters using images of product.
* extend_data.py (Not in use) randomly distorts a collection of data. This was made with the thought of machine learning in mind. 
* from_vid.py accesses a video and implements a usage for the meat class. 
* get_colour_range.py allows users to specify a range of pixels over a range of images and returns the max/min values for HSV. 
* profiler.py runs a timing analysis on any file required. 

## implementation_code.py 

implementation_code.py is a full implementation of the library for visualization and debugging purposes. 

![Visualization of library implementation](/resources/images/main.PNG)

## main.py
main.py is an implementation of the library required to be used for the robotic system. 


_Note: Project development was stopped due to internal company factors._
