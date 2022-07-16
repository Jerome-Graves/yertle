![new yertle logo](https://user-images.githubusercontent.com/12387040/177182736-baa268a0-e6b8-4a5e-a758-1f791cb3d4f0.png)
<p>
<img src="https://img.shields.io/badge/c++-%2300599C.svg?style=for-the-badge&logo=c%2B%2B&logoColor=white" /> 
<img src="https://img.shields.io/badge/ros2-%230A0FF9.svg?style=for-the-badge&logo=ros&logoColor=white" /> 
<img src="https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white" /> 
<img src="https://img.shields.io/badge/ubuntu 20.04-%23550055.svg?style=for-the-badge&logo=ubuntu&logoColor=white" /></p>

<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://user-images.githubusercontent.com/12387040/177196016-99242a4f-4778-4c39-b6a1-576d3acc98ad.png">
# Table of Contents 
<p  style=" display: block;margin-left: auto;margin-right: auto;text-align:center;">
<a href="#wifi">WiFi</a><br>
<a href="#Robot Firmware">Firmware</a><br>
<a href="#Control Software">Control Software</a><br>
<a href="#ros">ROS</a><br>

</p>


- - -
<br><br>
There are 2 options for controlling the robot. You can run The python GUI script from a remote device and connect to the robot via WiFi (recommended) or use a remote desktop application to run the script from the RPi.
<br><br>

# WiFi


<br><br>
The robot will want to connect to WiFi when it starts.
The default login detail are: <br>
* USSID : <b>dog-net</b>

* PASSWORD: <b>dog123</b>

You can change these in the <b>.ino</b> file.
<br><br>

</p>

- - -

<br>

# Firmware
This was written in <b>C++</b> using the <b>Arduino IDE</b>. It uses <b>FreeRtos</b> to separate tasks to different cores of the ESP32.
One task deals with WiFi and serial communication, while the other deals with I2C communication and inverse kinematics calculations. [Link](ESP32/firmware/firmware.ino)

- - -

<br>

# Control Software
This was written in <b>Python3</b> and uses the <b>tkinter</b> library to generate a GUI to control the robot. It connects to the robot through either <b>Wifi</b> or <b>serial</b> communication. The robot sends sensor information and the control software generates the feet's position and sends it back to the robot in real-time.

![image](https://user-images.githubusercontent.com/12387040/178509729-ef203f87-d7fb-4c72-958f-4f88137b29f7.png)

## Configuring IMU

The IMU needs to be initially calibrated. These settings are saved in an <b>.ini</b> and reused when the robot is restarted.
- - -
<br>

## Zeroing servos
You can use this GUI to Zero servos before fully constructing robot.
* Use the servo control tab bo visual center servos 
* Press the Get PWM button to get the current PWM values and use these in <b>.ino</b> file to set <b>servo offsets</b>.
    

<br>


# ROS
(python)
(todo)
- - -

<br>