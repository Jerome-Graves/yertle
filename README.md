![new yertle logo](https://user-images.githubusercontent.com/12387040/177182736-baa268a0-e6b8-4a5e-a758-1f791cb3d4f0.png)

# A 3D printed Quadrupedal Robot for Locomotion Research (WIP)

<p>
<img src="https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white" /> 
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" /> 
<img src="https://img.shields.io/badge/ros-%230A0FF9.svg?style=for-the-badge&logo=ros&logoColor=white" /> 
<img src="https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white" /></p>


The objective of the project was to produce a high quality, 3D printed, quadrupedal robot capable of traversing even, uneven and slopped terrain and with comparable dexterity (for its size) as a the Boston Dynamics Spot Mini robot but with a low cost and easy to source parts list and ROS compatibility. 
<br>



This robot was inspired by the <a href="https://grabcad.com/library/diy-quadruped-robot-1">Kangal </a>, <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> and <a href="https://github.com/adham-elarabawy/open-quadruped">Open Quadruped</a>. The concept was to have the best parts of all designs and make it compatible with <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> parts.
The current cost of the robot is around £250
</br>
![giphy ](https://user-images.githubusercontent.com/12387040/177191503-e122d730-9d83-4a72-aaf7-d9e7b08e673a.gif)
- - -
## Hardware

* 3D printed body (PLA, TPU)
* Raspberry Pi 4B
* Intel Realsense D435i
* Pca9685 16 Channel 12bit Pwm Servo Motor Driver
* YPG 20A HV SBEC
* 7.4V 2S 5000mAh 50C LiPo Battery
* (100X) M3 Screws and Nuts
* Bearings (todo)
* (12X) SPT Servo SPT5435LV-180W 35KG
* (4) M3 shafts >100mm( todo)
* (16X) M3 rod ends (todo)

![ezgif-2-765fbd3c28](https://user-images.githubusercontent.com/12387040/159661633-2cda4357-3ed2-483c-bc63-b13c3e34d269.gif)

- - -
## Software
* Ubuntu Server 20.04
* ROS 2 , foxy fitzroy
 - - -
## To Do

*  ROS integration
*  Simulation ([#5][i5])


[i1]: https://github.com/Jerome-Graves/yertle/issues/1
[i2]: https://github.com/Jerome-Graves/yertle/issues/2
[i3]: https://github.com/Jerome-Graves/yertle/issues/3
[i4]: https://github.com/Jerome-Graves/yertle/issues/4
[i5]: https://github.com/Jerome-Graves/yertle/issues/5
[i6]: https://github.com/Jerome-Graves/yertle/issues/6
