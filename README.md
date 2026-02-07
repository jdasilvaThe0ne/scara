# SCARA Arm Simulation (ROS 2 & Gazebo) '
 ## overview 
 This project implements a SCARA (Selective Compliance Assembly Robot Arm) simulation using ROS 2 and Gazebo. The repository contains the robot description (URDF/XACRO), controller configuration, launch files, and a Gazebo world. The system supports visualization, motion control, and camera feedback using standard ROS 2 tools.
 ## Prerequisites

- ROS 2 jazzy
- Gazebo (harmonic)
- colcon build system
- rqt, rqt_image_view, rqt_grap

### this to you .bashrc file  at the end 
source /opt/ros/<ros_distro>/setup.bash

###  clone the ripository 
     git clone https://github.com/jdasilvaThe0ne/scara.git  my_scara
###  build the project 
     - cd my_scara
     - colcon build
     - source install/setup.bash
### modify files 
#### Update path in robot definintion file 
   1.   open src/last_scara_arm/urdf/scara.urdf.xacro
     go to 395 
     - replace  the filepath with yours
     Example 
    <filepath>/src/last_scara_arm/urdf/scara_controllers.yml
     becomes 
      /home/your_username/my_scara/src/last_scara_arm/urdf/scara_controllers.yml

#### Update path in launch file 
    2. open src/last_scara_arm/launch/spawn_scara.launch.py
     got the line 10 
     <filepath>/src/last_scara_arm/urdf/scara.urdf.xacro
      modify as above 
### running the summulattion 
    - do this for each terminal
        cd <prject directory>
        cd  my_scara
        source install/setup.bash;
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ros/jazzy/lib;
        export GZ_SIM_RESOURCE_PATH=$GZ_SIM_RESOURCE_PATH:/opt/ros/jazzy/share;
        export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/ros/jazzy/lib;
        export  GZ_SIM_SYSTEM_PLUGIN_PATH=$GZ_SIM_SYSTEM_PLUGIN_PATH:/opt/ros/jazzy/lib


    in separate terminals run 
#### Start gazebo world
    -T1 gz sim src/last_scara_arm/world/lab_world.sdf -r
####  spawn the robot into the world
    -t2  ros2 launch last_scara_arm  spawn_scara.launch.py
####  View the camera image 
    T3 ros2 run rqt_image_view rqt_image_view
#### Moake the arm  move 
    -T4 ros2 run last_scara_arm movingaparatus
#### check the ross graph
    -T5 ros run rqt_graph

      
