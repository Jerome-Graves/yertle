/*
* Yertle Quadrupedl robot Firmware
* 
*
* Jeromegraves.com 
*/
#include "yertle lib.h"
#include <Wire.h>

TaskHandle_t Task1;
TaskHandle_t Task3;

ServoClass Servos;
CommClass Comms;
SensorClass Sensors;

const TickType_t sensorDelay =10 / portTICK_PERIOD_MS;
const TickType_t servoDelay = 10 / portTICK_PERIOD_MS;
const TickType_t commDelay = 10 / portTICK_PERIOD_MS;

void setup() {
  Serial.begin(115200);
  Serial.print("Starting task!!!....");
  Serial.setTimeout(10);
  
  Wire.setClock(1000000);
  Wire.begin();

  delay(500);
  
  xTaskCreatePinnedToCore(HardwareTask, "Task1",5000,NULL,2, &Task1,1);
  delay(500);

  xTaskCreatePinnedToCore(commTask, "Task3",5000,NULL,1, &Task3, 0);
  delay(500);


}

// Communicate with Hardware

void HardwareTask(void* parameter) {
  Serial.print("\nHardwareTask is running on core ");
  Serial.println(xPortGetCoreID());

  Sensors.start();
  //Sensors.calibrate();
  Servos.start();
  Servos.tick();
  
  for (;;) {
    Servos.tick();
    Sensors.tick();
    vTaskDelay(servoDelay);
  }
}



// get/send data from over serial (custom interface)
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