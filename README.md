![yertle image](https://user-images.githubusercontent.com/12387040/154842903-77c47f65-0455-4f21-bacb-2093f784f7f1.png)

# Quadrupedal Robot (WIP)

<p>
<img src="https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white" /> <img src="https://img.shields.io/badge/ros-%230A0FF9.svg?style=for-the-badge&logo=ros&logoColor=white" /> <img src="https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white" /></p>


## A Quadrupedal robot capable of traversing uneven terrain by modifying foot trajectories using spatial information from a depth camera.

This robot was inspired by both the the <a href="http://https://github.com/reubenstr/Zuko">Zuko</a>, <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> and <a href="https://github.com/adham-elarabawy/open-quadruped">Open Quadruped</a>.

</br>

# !! Note this is a WIP 


![image](https://user-images.githubusercontent.com/12387040/154842373-42b3cce0-2450-4362-b23c-a2e9c3eca3d5.png)

## Hardware

* 3D printed boday (PLA, TPU)
* Raspbery Pi 4B
* Intel Reasense D435i
* Pca9685 16 Channel 12bit Pwm Servo Motor Driver
* YPG 20A HV SBEC
* 7.4V 2S 5000mAh 50C LiPo Battery
* (100X) M3 Screws and Nuts
* Bearings (todo)
* (12X) SPT Servo SPT5435LV-180W 35KG
* (4) M3 shafts >100mm( todo)
* (16X) M3 rod ends (todo)

## Software
* Ubunto Server 20.04
* ROS 2 , foxy fitzroy

## To Do
*  STEP file of mechanical design ([#1][i1])
*  SLT files for 3D Printing ([#2][i2])
*  Pi4 image including: OpenCV, ROS, Unbuntu, Realsense Drivers ([#3][i3])
*  Build robot hardware ([#4][i4])
*  Gazebo Simulation ([#5][i5])
*  Write Inverse Kinematics solver in C++ ([#6][i6])
* ....


[i1]: https://github.com/Jerome-Graves/yertle/issues/1
[i2]: https://github.com/Jerome-Graves/yertle/issues/2
[i3]: https://github.com/Jerome-Graves/yertle/issues/3
[i4]: https://github.com/Jerome-Graves/yertle/issues/4
[i5]: https://github.com/Jerome-Graves/yertle/issues/5
[i6]: https://github.com/Jerome-Graves/yertle/issues/6