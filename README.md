# loin-feeder-robot

This project is to design the control systems for a robot that feeds the loin puller at Hylife Foods Ltd. The mechanical design for this system was done by a team of student from the University of Manitoba (Christopher Mckay, Zheng Fan, Dylan Van Deynze, David Lubi). 

This software aims at solving three challenges:
* Develop a vision system that allows the robot to determine the size, orientation, and proper cut line on travelling hogs. 
* Develop an algorithm that plans the actuator paths required to align the hogs in the proper orientation. 
* Program the appropriate PLCs to actuate the path determined on the physical build. 


## Current Progress

### Vision System
bbox_hsv.py can take an image with a piece of meat in it and identify the bounding box of the meat. 

meat.py is a class for a meat object. Given a bounding box, it can find all the significant edges and identify where the cut line should be. 

![Meat object identification](/images/meat_identified.PNG)

from_vid.py creates an application of the above files and implements it from a video stream. 

### Inverse Kinematics 
robot.py creates a model of the actual robot (to scale). It uses inverse kinematics to be able to follow two points at once with both of its carriages. 

IK.py is an implementation of robot.py 
![Robot model implementation](/images/model.PNG)
