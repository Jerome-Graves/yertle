![new yertle logo](https://user-images.githubusercontent.com/12387040/177182736-baa268a0-e6b8-4a5e-a758-1f791cb3d4f0.png)
<p style=" display: block;margin-left: auto;margin-right: auto;text-align:center;">
<a  href=""><img src="https://img.shields.io/badge/-.step-red?style=for-the-badge" /></a> <a href=""><img src="https://img.shields.io/badge/-.stl-yellow?style=for-the-badge" /></a> <a href=""><img src="https://img.shields.io/badge/-.iges-green?style=for-the-badge" /></a>  
</p>



<img  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;
" src="https://user-images.githubusercontent.com/12387040/177196016-99242a4f-4778-4c39-b6a1-576d3acc98ad.png">
# Table of Contents 
<p  style=" display: block;margin-left: auto;margin-right: auto;text-align:center;">
<a href="#3d-printed-parts">3D Printed Parts</a><br>
<a href="#bill-of-materials">B.O.M (Bill of Materials)</a><br>
<a href="#electronics">Electronics</a><br>
<a href="#assembly">Assembly</a><br>
</p>

- - -

<br>


# 3D Printed Parts 
Yertle can be 3D printed with PLA or ABS. You will need a printer with a build plate 150x150cm. It took me roughly 2 weeks (5-10 hours a day) to print all the parts on my <b>Ender 3 Pro</b>. Most of the parts are compatible with the original SpotMicro parts.

<br>

### Shell:


| Item          | Quantity      | Link                             | Notes      |
| ------------- | ------------- | -------------                    | ---------- |
| Top Shell           | 1        | [link](STL/Shell/Top%20Shell.stl)     | print in secondary colour  |
| Bottom Shell           | 1     | [link](STL/Shell/Bottom%20Shell.stl)     |print in secondary colour |
| Front Shell          | 1       | [link](STL/Shell/Front%20Shell.stl)      |print in secondary colour  |
| Back Shell          | 1        | [link](STL/Shell/Back%20Shell.stl)     | print in secondary colour |



<br>

### Body Frame:
| Item          | Quantity      | Link                             | Notes      |
| ------------- | ------------- | -------------                    | ---------- |
| Inner Shoulder Frame           | 2        | [link](STL/Frame/Inner%20Shoulder%20Frame.stl)     |  no supports|
| Outer Shoulder Frame           | 2        | [link](STL/Frame/Outer%20Shoulder%20Frame.stl)     |  no supports|
| Upper Shoulder Frame           | 2        | [link](STL/Frame/Upper%20Shoulder%20Frame.stl)     |  no supports|
| Lower Shoulder Frame           | 2        | [link](STL/Frame/Lower%20Shoulder%20Frame.stl)     |  no supports|
| Left Servo Mount          | 2        | [link](STL/Frame/Left%20Servo%20Mount.stl)     |  no supports|
| Right Servo Mount        | 2        | [link](STL/Frame/Left%20Servo%20Mount.stl)     |  no supports|
| Servo Mount Top Bracket  | 4        | [link](STL/Frame/Servo%20Mount%20Top%20Bracket.stl)     |  no supports|
| Side Body beam           | 2        | [link](STL/Frame/Side%20Body%20Beam.stl)     |  no supports|
| Electronics Mounting Plate          | 1        | [link](STL/Frame/Electronics%20Mounting%20Plate.stl)     |  no supports|


<br>

### Legs:
| Item          | Quantity      | Link                             | Notes      |
| ------------- | ------------- | -------------                    | ---------- |
| Inner Tibia           | 4       | [link](STL/Legs/Inner%20Tibia.stl)     | |
| Outer Tibia           | 4       | [link](STL/Legs/Outer%20Tibia.stl)     | |
| Femur                 | 4       | [link](STL/Legs/Femur.stl)     | |
| Femur Servo Connector | 4       | [link](STL/Legs/Femur%20Servo%20Connector.stl)     | high infill|
| Left Shoulder         | 2       | [link](STL/Legs/Left%20Shoulder.stl)     |  print in secondary colour |
| Right Shoulder        | 2       | [link](STL/Legs/Right%20Shoulder.stl)     |  print in secondary colour |
| Short Link           | 4        | [link](STL/Legs/Short%20Link.stl)     |   |
| Long Link            | 4        | [link](STL/Legs/Long%20Link.stl)     |  |

- - -

<br>
<br>







# Bill of Materials:
| Item          | Quantity      | Cost          | Link          | Notes      |
| ------------- | ------------- | ------------- | ------------- | ---------- |
| PLA           | 1Kg           | £19           |    --    | This can be ABS of PEG. |
| SPT Servo SPT5435LV-180W 35KG   | 12            | £162.36           |    [link](https://uk.banggood.com/SPT-Servo-SPT5435LV-180W-35KG-Large-Torque-Waterproof-Metal-Gear-Digital-Servo-For-RC-Robot-RC-Car-p-1577514.html?cur_warehouse=CN)       | They need to be >= 15Kg/cm.|
| M3 Screws, Nuts and washers     | x100           | £10           |    [link](https://amzn.eu/d/dV1QDNL)       | |
| MPU9250           | 1          | £5           |    [link](https://www.aliexpress.com/item/1005004573086760.html?_randl_currency=GBP&_randl_shipto=GB&src=google&aff_fcid=41e9a88704994d1e86bda6bb583acc20-1664268874913-07892-UneMJZVf&aff_fsk=UneMJZVf&aff_platform=aaf&sk=UneMJZVf&aff_trace_key=41e9a88704994d1e86bda6bb583acc20-1664268874913-07892-UneMJZVf&terminal_id=cc80addd062b4558acb523f516ecdfe3&afSmartRedirect=y)       | optional, you can use a different IMU if needed |
| ESP32s         | 1           | £5           |    [link](https://www.google.com/search?q=esp32&rlz=1C1ONGR_en-GBGB992GB992&sxsrf=ALiCzsZepGPdGmADGOMSWxNcJFkwf7XaaA:1664268995462&source=lnms&tbm=shop&sa=X&ved=2ahUKEwjx0qOSzbT6AhUGQEEAHVDBAJ0Q_AUoAXoECAEQAw&biw=1918&bih=1039&dpr=1#spd=12019570854939482759)       | |
| (Raspberry Pi 4B)          | 1           | £50           |    [link](https://www.aliexpress.com/item/1005003952938315.html?_randl_currency=GBP&_randl_shipto=GB&src=google&aff_fcid=93340942133e48be85abe7f52b6806cc-1664269060030-06205-UneMJZVf&aff_fsk=UneMJZVf&aff_platform=aaf&sk=UneMJZVf&aff_trace_key=93340942133e48be85abe7f52b6806cc-1664269060030-06205-UneMJZVf&terminal_id=cc80addd062b4558acb523f516ecdfe3&afSmartRedirect=y)       | This is optional, The robot can uses remote device.  |
| PCA9685 Servo Driver         | 1          | £4           |    [link](https://www.aliexpress.com/item/32469378576.html)       |  |
| 7.4V 2S 5000mAh 50C LiPo Battery | 1          | £30           |    [link](https://amzn.eu/d/aaM0lUO)       | this can be smaller if you want less weight/cost |
| SBEC 6V 20A | 1          | £20           |    [link](https://hobbyking.com/en_us/yep-20a-hv-2-12s-sbec-w-selectable-voltage-output.html)       | |
| Miniature Ball Bearings 5x16x5mm   | 4       | £3           |    [link](https://www.ebay.co.uk/itm/394185642290)       | |
|  Deep Groove Ball Bearings 25x37x7mm   | 4       | £9           |    [link](https://www.ebay.co.uk/itm/124120979478?epid=28035077387&hash=item1ce62fd816:g:cFUAAOSwLIpecLPR&amdata=enc%3AAQAHAAAAoJQoreVPvkWQ1gBh%2BOiPX1BWv05VSyL1pl9tQdsAMxZgJpJy4VTnTr8%2FFW2Lc1HVPLfch2ZJOFeOUIk4bIO2sfl6UDS7BsWbrD1v%2FezQYY4piy8ZhrTNoDw9nbt2n5SiaKVdgnSBgNqcgfzRdbGnj1Rv5Upv%2BuIMloVQOwavfwL49OHsQkgJsVfjAYSDVTHPxfONGwidwoZPiBFLtdgP7Y0%3D%7Ctkp%3ABk9SR86nvuPvYA)       |  |
|  RS PRO Miniature Ball Bearing 3x13X5mm  | 8       | £9           |    [link](https://www.ebay.co.uk/itm/304258710252?hash=item46d73b7aec:g:1WgAAOSwN~diUTBF&amdata=enc%3AAQAHAAAA4MGsR1psd92dUbvi4uHqMovMcbwXkh60NkWrsxgDQwXE2ettVy3sRi06LdoH5GBpoeM5Cc8ZuFnVI%2FbDqjkIWDoJffTqNEaTuTT02iQpRbWgJfKlg40Au4fUKTzynHB1E06rH5l1GCRUwc7xX4DnbQJkWerMiaJ6p5PFRTmi6fyV7SR6fOJ7FqH0z15FvirmQwTeqKmuHMKNRwz9hVBz8YJcXFiOINyJY0kNHxLLChojPMEPEurdXzcUGjc%2BmnIiACosQf11Xao4XNSpDN41hqhKW8MqvSz75tE6T5SOFBDj%7Ctkp%3ABFBMvLDC4-9g)       |  |
| 25T Metal Servo Circular Horn    | 4       | £5           |    [link](https://amzn.eu/d/hwdEX03)       |  |
| 25T Metal Servo Arm Horn  | 4       | £5           |    [link](https://www.amazon.co.uk/N-Aluminum-Clamping-Steering-Crawler/dp/B08V4NP2JT/ref=sr_1_11?keywords=servo+arm&qid=1664269419&qu=eyJxc2MiOiI0LjQ4IiwicXNhIjoiNC4xNyIsInFzcCI6IjIuODcifQ%3D%3D&sr=8-11)       |  |
| Sleeve Bearing 3mm Bore x 5mm OD x 5mm | 32       | £15           |    [link](https://amzn.eu/d/bPWGEY8)       |  |
<br>


<br>
<br>

# Electronics

Yertle is controlled by an ESP-32s microcontroller and a Raspberry Pi 4 Single board computer. The robot can operate with just the ESP but will require a computer or phone with WiFi capable of running python3. The flow diagram shows the general electronic connections and wiring. 
The current and voltage sensors are optional.

![Yertle Diagram flow](https://user-images.githubusercontent.com/12387040/177245145-c20d1fc6-862a-4f38-909a-6146b7b7e857.png)
  

<br>
<br>

# Assembly

<br>

## Part1:
Connect and wire electronics to the mounting plate. You can use cable ties to hold the SBEC and battery. I normally connect the esp on top of the pi by soldering a custom Pi hat board that also mounts the IMU.

![image](https://user-images.githubusercontent.com/12387040/177247846-cfc5c834-6e8b-4745-9d76-c606543bca5a.png)

<br>

## Part2:
Construct the frame with inner servos and electronics.

![image](https://user-images.githubusercontent.com/12387040/177248519-6b8e5d40-a18e-4a59-8405-390a05a6b0cd.png)
<br>

## Part3:
Construct the legs.

![image](https://user-images.githubusercontent.com/12387040/177250145-c5ee9356-0b25-4144-842c-df5e74f91844.png)

<br>

## Part4:
Connect electronics and zero the servos (before connecting legs).

![image](https://user-images.githubusercontent.com/12387040/177250740-7c5629e7-9cad-4e7b-aead-6a167f0438b3.png)

<br>

## Part5:
Connect legs and Shell.

<img  align="center"  style=" display: block;margin-left: auto;margin-right: auto;width:400px;border: 5px solid grey;border-radius:20%;" src="https://user-images.githubusercontent.com/12387040/177191503-e122d730-9d83-4a72-aaf7-d9e7b08e673a.gif">
