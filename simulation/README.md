![new yertle logo](https://user-images.githubusercontent.com/12387040/177182736-baa268a0-e6b8-4a5e-a758-1f791cb3d4f0.png)

# Simulation
<a href=""><img src="https://img.shields.io/badge/-pyBullet-green?style=for-the-badge" /></a> 
<a href=""><img src="https://img.shields.io/badge/-.urdf-orange?style=for-the-badge" /></a> 

<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://user-images.githubusercontent.com/12387040/177196016-99242a4f-4778-4c39-b6a1-576d3acc98ad.png">

<!--
# Table of Contents 
<p  style=" display: block;margin-left: auto;margin-right: auto;text-align:center;">
<a href="#wifi">WiFi</a><br>
<a href="#Robot Firmware">Firmware</a><br>
<a href="#Control Software">Control Software</a><br>
<a href="#ros">ROS</a><br>

</p>
-->

- - -
<br><br>
The robot model is the URDF file [yertle.urdf](yertle.urdf). It is
simulation-ready: the inertia tensors are physically valid, the twelve leg
joints are revolute with firmware-derived limits, and the actuators carry
effort and velocity caps, so the same model works in PyBullet and in
PhysX-based simulators.

For NVIDIA Isaac Sim / Isaac Lab, convert it to USD with Isaac Lab's importer
(the generated `usd/` directory is regenerable and not committed):

```
python IsaacLab/scripts/tools/convert_urdf.py simulation/yertle.urdf simulation/usd/yertle.usd --merge-joints --headless
```
<br>

There is a pyBullet simulation in the python control software, and the RL
pipelines ([learning/](../learning/README.md),
[isaac_lab/](../isaac_lab/README.md)) build their training environments from
this same model.
<br><br>
<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://media4.giphy.com/media/n3Z5qsrYJxJJMqyYtR/giphy.gif?cid=790b76111312ba6e427509258eeacdafe06fd2e38f7f575e&rid=giphy.gif&ct=g">
<br><br>
It creates a digital twin of the robot. You can control it with the UI. To move the robot around using the Keyboard direction keys. 
<br><br>