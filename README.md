![new yertle logo](https://user-images.githubusercontent.com/12387040/177182736-baa268a0-e6b8-4a5e-a758-1f791cb3d4f0.png)

# A 3D Printed Quadrupedal Robot for Locomotion Research (WIP)

<p align="center" >
<img src="https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white" /> 
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" /> 
<!--
<img src="https://img.shields.io/badge/ros-%230A0FF9.svg?style=for-the-badge&logo=ros&logoColor=white" /> 
<img src="https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white" /></p>
-->
<br>
<img  align="center"  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;" src="https://user-images.githubusercontent.com/12387040/177191503-e122d730-9d83-4a72-aaf7-d9e7b08e673a.gif">

<br>
The robot consists of:

* 4 limbs with 3 degrees of freedom powered by hobby servos, with a leg extension of approximately 20cm.
* A 5000mah battery - 30 minutes of run time (optional). 
* A 9-axis accelerometer/gyro sensor. (optional)
* A current and voltage sensor. (optional)
* A microcontroller (ESP32s) to communicate with Hardware and sensors.
* A single-board computer (RPi4) to compute image, location, ROS and advanced controller algorithms. (optional)
* 1.8 kg

<br>
This robot was inspired by the <a href="https://grabcad.com/library/diy-quadruped-robot-1">Kangal</a>, <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> and <a href="https://github.com/adham-elarabawy/open-quadruped">Open Quadruped</a>. The concept was to have the best parts of all designs and make it compatible with <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> parts.
The current cost of the robot is around £250.
</br>




- - -

<br>

## Robot in action:

<img   align="center"  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://user-images.githubusercontent.com/12387040/159661633-2cda4357-3ed2-483c-bc63-b13c3e34d269.gif">



<img   align="center"  style=" display: block;margin-left: auto;margin-right: auto;width:800px;border: 5px solid grey;border-radius:20%;
" src="https://media3.giphy.com/media/KFjNRAheWcB1mYteqC/giphy.gif?cid=790b76110cd3a428966bd2091bdf12e668c3ea9aa077822a&rid=giphy.gif&ct=g">

<img   style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://media2.giphy.com/media/ohLg4XAOlwop26fHhG/giphy.gif?cid=790b7611812c3d0172f0034f1dc05768a8a9239421e02847&rid=giphy.gif&ct=g">


- - -

<br>

## Design:
Click [here](Design/README.md) for 3D printer parts, assembly instructions and bill of materials.
<br><br>
Yertle is a  fusion of the leg design of <a href="https://grabcad.com/library/diy-quadruped-robot-1">Kangal</a> and the body of <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a>. As such, you can use the control software and electronics from any Kangal or derivative with this robot (with a little modification). Any Modifications for the spot micro shell will also work with this robot. And You can exchange the legs for Kangal's if you want. 
<br>
<br>
I have built a few quadruped robots and there are plenty of interesting leg mechanics to choose from. Overall The Kangal legs do have limitations. Such as their limited range in motion. But they do have the benefit of being extremely light and easy to change. This means I'm not pulling up anything heavy when I'm lifting my leg allowing the servos to be slightly faster when not under load. And I'm less worried about breaking them or putting the robot in a more extreme environment.
<br>


![image](https://user-images.githubusercontent.com/12387040/177250145-c5ee9356-0b25-4144-842c-df5e74f91844.png)
<br>


- - - 
<br>

## Electronics:
Click [here](Design/README.md/#electronics) for an electronics and wiring explanation.
<br><br>
I'm currently working on a better description of my wiring. I have soldered a custom Hat from my RPi that had all the necessary components. The robot was originally designed to use just the RPi but I found it to be unreliable as it is more complex to reset the device and more prone to corruption. As The ESP32 has WiFi I can debug the device remotely without a complex startup/shut down routine.
<br><br>
If you are familiar with wiring  <a href="https://grabcad.com/library/diy-quadruped-robot-1">Kangal</a> and the body of <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a>. You can use the same wiring.

- - -
<br>



## Software:
Click [here](Software/README.md) for the software.
<br><br>
The software runs in a master/slave system over the serial port or UPD over WiFi. The robot firmware acts as the slave. It controls all sensors, servos, computes the inverse kinematics of the robot and calculates safety limits. The main control system is written in Python3. It acts as a master It takes all data from the robot sensors and ROS(todo), generates the walk and sends this to the Slave.
<br><br>
The firmware was written in C++ using Arduino IDE so you can modify it to work on a different microcontroller if you want. 
There Python Control software uses a GUI and can run on anything that has WiFi a screen and can run Python3, including android devices(not tested).
<br><br>
The software can also runs ROS nodes for ROS2 integration(todo).

- - -
<br>

## Simulation:
Click [here](Simulation/README.md) for simulation tools.<br><br>
There is a simulation built into the python software. It enables you to test movement with the controller without a robot. 
<br><br>
<img   style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://media4.giphy.com/media/n3Z5qsrYJxJJMqyYtR/giphy.gif?cid=790b76111312ba6e427509258eeacdafe06fd2e38f7f575e&rid=giphy.gif&ct=g">

<br><br>

Here is another simulation example from Carter James using Unity.
<br><br> 
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/7LgCC4D3Wlk/0.jpg)](https://www.youtube.com/watch?v=7LgCC4D3Wlk)
- - -
<br>



<br>

## To Do

*  ROS integration
