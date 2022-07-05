![new yertle logo](https://user-images.githubusercontent.com/12387040/177182736-baa268a0-e6b8-4a5e-a758-1f791cb3d4f0.png)

# A 3D Printed Quadrupedal Robot for Locomotion Research (WIP)

<p  style=" display: block;margin-left: auto;margin-right: auto;width:400px;">
<img src="https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white" /> 
<img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" /> 
<img src="https://img.shields.io/badge/ros-%230A0FF9.svg?style=for-the-badge&logo=ros&logoColor=white" /> 
<img src="https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white" /></p>

<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://user-images.githubusercontent.com/12387040/177191503-e122d730-9d83-4a72-aaf7-d9e7b08e673a.gif">

The objective of the project was to produce a high quality, 3D printed, quadrupedal robot capable of traversing even, uneven and slopped terrain and with comparable dexterity (for its size) as a the Boston Dynamics Spot Mini robot but with a low cost parts list and ROS compatibility. 

<br>
The robot consists of:

* 4 limbs with 3 degrees of freedom powered by hobby servos, with a leg extension of approximately 25cm. 
* A 5000mah battery (45 minutes of run time). 
* A 9-axis accelerometer/gyro sensor. 
* A current and voltage sensor.
* A microcontroller (ESP32s) to communicate with Hardware and sensors.
* A single-board computer (RPi4) to compute image, location, ROS and advanced controller algorithms.

<br>
This robot was inspired by the <a href="https://grabcad.com/library/diy-quadruped-robot-1">Kangal</a>, <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> and <a href="https://github.com/adham-elarabawy/open-quadruped">Open Quadruped</a>. The concept was to have the best parts of all designs and make it compatible with <a href="https://spotmicroai.readthedocs.io/en/latest/">SpotMicro</a> parts.
The current cost of the robot is around £250.
</br>




- - -

<br>

## Robot in action:

<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://user-images.githubusercontent.com/12387040/159661633-2cda4357-3ed2-483c-bc63-b13c3e34d269.gif">



<img  style=" display: block;margin-left: auto;margin-right: auto;width:800px;border: 5px solid grey;border-radius:20%;
" src="https://media3.giphy.com/media/KFjNRAheWcB1mYteqC/giphy.gif?cid=790b76110cd3a428966bd2091bdf12e668c3ea9aa077822a&rid=giphy.gif&ct=g">

<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://media0.giphy.com/media/11GzEkS1TQJCkdmxBD/giphy.gif?cid=790b7611434c394204cfbd1d88a35720a67b6308b0162ed2&rid=giphy.gif&ct=g">

- - -

<br>

## Design:
Click [here](Design/README.md) for 3D printer parts, assembly instructions and bill of materials.
- - - 
<br>

## Software:
Click [here](Software/README.md) for a software explanation.
- - -
<br>

## Simulation:
Click [here](Simulation/README.md) for a simulation explanation (todo).
- - -
<br>



<br>

## To Do

*  ROS integration
*  Simulation ([#5][i5])


[i1]: https://github.com/Jerome-Graves/yertle/issues/1
[i2]: https://github.com/Jerome-Graves/yertle/issues/2
[i3]: https://github.com/Jerome-Graves/yertle/issues/3
[i4]: https://github.com/Jerome-Graves/yertle/issues/4
[i5]: https://github.com/Jerome-Graves/yertle/issues/5
[i6]: https://github.com/Jerome-Graves/yertle/issues/6
