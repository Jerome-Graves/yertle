/*
* Yertle Quadruped Robot - Firmware for EPS32
* 
* Written by Jerome Graves
* 2022
* Jeromegraves.com    
*/
#include "yertle lib.h"
#include <Wire.h>

TaskHandle_t Task1;
TaskHandle_t Task2;

ServoClass Servos;
CommClass Comms;
SensorClass Sensors;



const TickType_t hardwareDelay = 10 / portTICK_PERIOD_MS;
const TickType_t commDelay = 10 / portTICK_PERIOD_MS;

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);
  
  Wire.setClock(1000000);
  Wire.begin();
  delay(500);

  xTaskCreatePinnedToCore(hardwareTask, "Task1",5000,NULL,2, &Task1,1);
  delay(500);

  xTaskCreatePinnedToCore(commTask, "Task2",5000,NULL,1, &Task2, 0);
  delay(500);
}

//  This task that controls I2C , servos , sesors.

void hardwareTask(void* parameter) {
  Serial.print("\nHardwareTask is running on core ");
  Serial.println(xPortGetCoreID());

  Sensors.start();
  Servos.start();
  Servos.tick();
  
  for (;;) {
    Servos.tick();
    Sensors.tick();
    vTaskDelay(hardwareDelay);
  }
}


//  This task that contols wifi, serial.
void commTask(void* parameter) {
  Serial.print("\ncommTask is running on core ");
  Serial.println(xPortGetCoreID());
  Comms.start();
  for (;;) {
    Comms.listen();
    vTaskDelay(commDelay);
  }
}

void loop(){};