#include <Wire.h>
#include <FaBo9Axis_MPU9250.h>
#include "yertle lib.h"
#include <Arduino.h>
#include <FaBoPWM_PCA9685.h>
#include "WiFi.h"
#include "AsyncUDP.h"
#include <SimpleKalmanFilter.h>
#include <Preferences.h>
#include <MPU9250.h>

Preferences preferences;

MPU9250 mpu;

FaBoPWM ServoDriver;

AsyncUDP udpClient;
AsyncUDP udpServer;


PoseAngle currentPoseAngle, defaultPoseAngle;
PoseCartesian poseCartesian;

ImuConfig imuConfig;
ImuData imuData;

Flags flag;
String InputDataString;





float rawRotX = 0.0, rawRotY = 0.0, rawRotZ = 0.0;
float rawAccX = 0.0, rawAccY = 0.0, rawAccZ = 0.0;
float rawMagX = 0.0, rawMagY = 0.0, rawMagZ = 0.0;
float accAngleX = 0.0, accAngleY = 0.0, accAngleZ = 0.0;
float gyroAngleX = 0.0, gyroAngleY = 0.0, gyroAngleZ = 0.0;
float magAngleX = 0.0, magAngleY = 0.0, magAngleYZ = 0.0;






/// WIfi  Variables , change if necessary!
const char* ssid = "dog-net";
const char* password = "dognet123";

unsigned int localUdpPort = 1234;  //  port to listen on

IPAddress local_IP(10, 0, 0, 88);
// Set your Gateway IP address
IPAddress gateway(10, 0, 0, 1);
IPAddress subnet(255, 255, 0, 0);
IPAddress primaryDNS(8, 8, 8, 8);    //optional
IPAddress secondaryDNS(8, 8, 4, 4);  //optional





ServoClass::ServoClass() {
  // NOTHING
}

void ServoClass::start() {  // Start the servo driver
  if (ServoDriver.begin()) {
    ServoDriver.init(200);
    //Serial.println("  Configured FaBo ServoDriver I2C Brick");  // <--  bug with laptop library (int casting to byte?)
  } else {
    //Serial.println("  FaBo 9Axis I2C Brick failed.");
  }
  ServoDriver.set_hz(200);  // <--  bug with laptop library (int casting to byte?)
  //flag.killServosFlag = true;
  
  flag.newPoseCartesianFlag = true;
}

/// set robot to pose

void ServoClass::moveToPose() {
  setAngle(servoId.lf_theta1, currentPoseAngle.lf_theta1, defaultDirection.lf_theta1, defaultLimits.lowerTheta1, defaultLimits.upperTheta1, servoOffsets.lf_theta1);
  setAngle(servoId.lf_theta2, currentPoseAngle.lf_theta2, defaultDirection.lf_theta2, defaultLimits.lowerTheta2, defaultLimits.upperTheta2, servoOffsets.lf_theta2);
  setAngle(servoId.lf_theta3, currentPoseAngle.lf_theta3, defaultDirection.lf_theta3, defaultLimits.lowerTheta3, defaultLimits.upperTheta3, servoOffsets.lf_theta3);
  setAngle(servoId.rf_theta1, currentPoseAngle.rf_theta1, defaultDirection.rf_theta1, defaultLimits.lowerTheta1, defaultLimits.upperTheta1, servoOffsets.rf_theta1);
  setAngle(servoId.rf_theta2, currentPoseAngle.rf_theta2, defaultDirection.rf_theta2, defaultLimits.lowerTheta2, defaultLimits.upperTheta2, servoOffsets.rf_theta2);
  setAngle(servoId.rf_theta3, currentPoseAngle.rf_theta3, defaultDirection.rf_theta3, defaultLimits.lowerTheta3, defaultLimits.upperTheta3, servoOffsets.rf_theta3);
  setAngle(servoId.lb_theta1, currentPoseAngle.lb_theta1, defaultDirection.lb_theta1, defaultLimits.lowerTheta1, defaultLimits.upperTheta1, servoOffsets.lb_theta1);
  setAngle(servoId.lb_theta2, currentPoseAngle.lb_theta2, defaultDirection.lb_theta2, defaultLimits.lowerTheta2, defaultLimits.upperTheta2, servoOffsets.lb_theta2);
  setAngle(servoId.lb_theta3, currentPoseAngle.lb_theta3, defaultDirection.lb_theta3, defaultLimits.lowerTheta3, defaultLimits.upperTheta3, servoOffsets.lb_theta3);
  setAngle(servoId.rb_theta1, currentPoseAngle.rb_theta1, defaultDirection.rb_theta1, defaultLimits.lowerTheta1, defaultLimits.upperTheta1, servoOffsets.rb_theta1);
  setAngle(servoId.rb_theta2, currentPoseAngle.rb_theta2, defaultDirection.rb_theta2, defaultLimits.lowerTheta2, defaultLimits.upperTheta2, servoOffsets.rb_theta2);
  setAngle(servoId.rb_theta3, currentPoseAngle.rb_theta3, defaultDirection.rb_theta3, defaultLimits.lowerTheta3, defaultLimits.upperTheta3, servoOffsets.rb_theta3);
}

// Convert float angle to pwm, needs the forward direction of the servo.
int ServoClass::angleToPWM(bool direction, float input) {
  if (direction == true) return map(input, -90, 90, 400, 2000);
  else if (direction == false)
    return map(input, -90, 90, 2000, 400);
};

// Keeps angle between upper and lower limits.
float ServoClass::filterLimits(float inputValue, float lowerLimit, float upperLimit) {
  if (inputValue < lowerLimit) return lowerLimit;
  else if (inputValue > upperLimit)
    return upperLimit;
  else
    return inputValue;
};

// Set servo angle.
void ServoClass::setAngle(int id, float angle, bool direction, float lowerLimit, float upperLimit, float offset) {

  ServoDriver.set_channel_value(id, int(offset) + angleToPWM(direction, +filterLimits(angle, lowerLimit, upperLimit)));
}

// Disable servos. <- not working
void ServoClass::killServos() {
  ServoDriver.set_channel_value(servoId.lf_theta1, 0);
  ServoDriver.set_channel_value(servoId.lf_theta2, 0);
  ServoDriver.set_channel_value(servoId.lf_theta3, 0);
  ServoDriver.set_channel_value(servoId.rf_theta1, 0);
  ServoDriver.set_channel_value(servoId.rf_theta2, 0);
  ServoDriver.set_channel_value(servoId.rf_theta3, 0);
  ServoDriver.set_channel_value(servoId.lb_theta1, 0);
  ServoDriver.set_channel_value(servoId.lb_theta2, 0);
  ServoDriver.set_channel_value(servoId.lb_theta3, 0);
  ServoDriver.set_channel_value(servoId.rb_theta1, 0);
  ServoDriver.set_channel_value(servoId.rb_theta2, 0);
  ServoDriver.set_channel_value(servoId.rb_theta3, 0);
}
// Send currnet postion PWM data through serial com port (used or zeroing servos).
void ServoClass::sendPWMData() {
  String val[12];
  val[0] = ServoDriver.get_channel_value(servoId.lf_theta1);
  val[1] = ServoDriver.get_channel_value(servoId.lf_theta2);
  val[2] = ServoDriver.get_channel_value(servoId.lf_theta3);
  val[3] = ServoDriver.get_channel_value(servoId.rf_theta1);
  val[4] = ServoDriver.get_channel_value(servoId.rf_theta2);
  val[5] = ServoDriver.get_channel_value(servoId.rf_theta3);
  val[6] = ServoDriver.get_channel_value(servoId.lb_theta1);
  val[7] = ServoDriver.get_channel_value(servoId.lb_theta2);
  val[8] = ServoDriver.get_channel_value(servoId.lb_theta3);
  val[9] = ServoDriver.get_channel_value(servoId.rb_theta1);
  val[10] = ServoDriver.get_channel_value(servoId.rb_theta2);
  val[11] = ServoDriver.get_channel_value(servoId.rb_theta3);
  Serial.print("PWM values: " + val[0] + " " + val[1] + " " + val[2] + " " + val[3] + " " + val[4] + " " + val[5] + " " + val[6] + " " + val[7] + " " + val[8] + " " + val[9] + " " + val[10] + " " + val[11]);
}

//Update fuctions for servos
void ServoClass::tick() {
  if (flag.newPoseAngleFlag) {  // <--- switched on in ROS task (extenally)
    moveToPose();
    flag.newPoseAngleFlag = false;
    //Serial.println("flag.newPoseAngleFlag");
  }

  if (flag.killServosFlag) {
    killServos();
    flag.killServosFlag = false;
    //Serial.println("flag.killServosFlag");
  }
  if (flag.newPoseCartesianFlag) {
    solveIk();
    moveToPose();
    flag.newPoseCartesianFlag = false;
    //Serial.println("flag.newPoseCartesianFlag");
  }
  if (flag.sendPWMDataFlag) {
    sendPWMData();
    flag.sendPWMDataFlag = false;
  }
}

//Compute IK for single limb.
void ServoClass::Ik(float deltaX, float deltaY, float deltaZ, float& theta1, float& theta2, float& theta3) {
  if (deltaX == 0) { deltaX = 0.001; }
  if (deltaY == 0) { deltaY = 0.001; }
  if (deltaZ == 0) { deltaZ = 0.001; }

  float dirXY, dirZY, distanceXYZ = sqrt(sq(deltaY) + sq(deltaX) + sq(deltaZ));

  if (sgn(deltaX) == 1) {
    dirXY = -1 * (atan(deltaY / deltaX) - PI + (PI / 2));
  } else if (sgn(deltaX) == -1) {
    dirXY = -1 * (atan(deltaY / deltaX) + (PI / 2));
  }

  if (sgn(deltaZ) == 1) {
    dirZY = -1 * (atan(deltaY / deltaZ) - PI + (PI / 2));
  } else if (sgn(deltaZ) == -1) {
    dirZY = -1 * (atan(deltaY / deltaZ) + (PI / 2));
  }

  dirXY = 360 * (dirXY / (2 * PI));  // xy plane direction from 0,0
  dirZY = 360 * (dirZY / (2 * PI));  // xz plane direction from 0,0

  float legLen1 = 13, legLen2 = 13, legspan = distanceXYZ;
  float c = legLen1, a = legLen2, b = legspan;
  float ang1 = acos((sq(b) + sq(c) - sq(a)) / (2 * b * c));
  theta1 = dirZY;
  theta2 = dirXY - 360 * (ang1 / (2 * PI));  //  convert to deg
  theta3 = -dirXY + 180 - (360 * (ang1 / (2 * PI)) + 90);
}
// Compute Ik for all limbs using currentPoseAngle.
void ServoClass::solveIk() {
  Ik(poseCartesian.lf_x, poseCartesian.lf_y, poseCartesian.lf_z, currentPoseAngle.lf_theta1, currentPoseAngle.lf_theta2, currentPoseAngle.lf_theta3);
  Ik(poseCartesian.rf_x, poseCartesian.rf_y, poseCartesian.rf_z, currentPoseAngle.rf_theta1, currentPoseAngle.rf_theta2, currentPoseAngle.rf_theta3);
  Ik(poseCartesian.lb_x, poseCartesian.lb_y, poseCartesian.lb_z, currentPoseAngle.lb_theta1, currentPoseAngle.lb_theta2, currentPoseAngle.lb_theta3);
  Ik(poseCartesian.rb_x, poseCartesian.rb_y, poseCartesian.rb_z, currentPoseAngle.rb_theta1, currentPoseAngle.rb_theta2, currentPoseAngle.rb_theta3);
}

//Check sign of flaot value.
int ServoClass::sgn(float x) {
  if (x < 0) { return -1; }
  if (x > 0) { return 1; }
  if (x == 0) { return 0; }
}


CommClass::CommClass() {}

//Initialisation of Com Class (wifi)
void CommClass::start() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  WiFi.setSleep(false);

  Serial.println("");

  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    Serial.println("STA Failed to configure");
  }
  // Wait for connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  udpClient.connect(IPAddress(10, 0, 0, 13), 1234);
  if (udpServer.listen(24321)) {
    udpServer.onPacket([](AsyncUDPPacket packet) {
      InputDataString = (char*)packet.data();
      flag.gotUdpDataFlag = true;
    });
  }
}

// Uppate loop of commclass
void CommClass::listen() {


  if (flag.gotUdpDataFlag) {
    DecodeInputString(InputDataString);
    flag.gotUdpDataFlag = false;
  }
  if (flag.sendConfigDataFlag){
  udpClient.print("c " +String(imuConfig.magXbias ) + " " + 
                        String(imuConfig.magYbias ) + " " +
                        String(imuConfig.magZbias ) + " " +
                        String(imuConfig.rotXbias ) + " " +
                        String(imuConfig.rotYbias ) + " " +
                        String(imuConfig.rotZbias ) + " " +
                        String(imuConfig.accXbias ) + " " +
                        String(imuConfig.accYbias ) + " " +
                        String(imuConfig.accZbias ) + " " +
                        String(imuConfig.magXscale) + " " +
                        String(imuConfig.magYscale) + " " +
                        String(imuConfig.magZscale) +" ewq");
  flag.sendConfigDataFlag = false;
  }
  if(Serial.available()) {
    InputDataString = Serial.readString();
    DecodeInputString(InputDataString);
  
  }
  
  udpClient.print("m " + String(imuData.magX) + " " + String(imuData.magY) + " " + String(imuData.magZ) + " ewq");
  udpClient.print("r " + String(imuData.rotX) + " " + String(imuData.rotY) + " " + String(imuData.rotZ) + " ewq");

}


// Convert input string to data (currentPoseAngle, poseCartesian)
void CommClass::DecodeInputString(String InputString) {
  if (InputString.charAt(0) == 'a') {
    currentPoseAngle.lf_theta1 = parseString(InputString, ' ', 1).toFloat();
    currentPoseAngle.lf_theta2 = parseString(InputString, ' ', 2).toFloat();
    currentPoseAngle.lf_theta3 = parseString(InputString, ' ', 3).toFloat();
    currentPoseAngle.rf_theta1 = parseString(InputString, ' ', 4).toFloat();
    currentPoseAngle.rf_theta2 = parseString(InputString, ' ', 5).toFloat();
    currentPoseAngle.rf_theta3 = parseString(InputString, ' ', 6).toFloat();
    currentPoseAngle.lb_theta1 = parseString(InputString, ' ', 7).toFloat();
    currentPoseAngle.lb_theta2 = parseString(InputString, ' ', 8).toFloat();
    currentPoseAngle.lb_theta3 = parseString(InputString, ' ', 9).toFloat();
    currentPoseAngle.rb_theta1 = parseString(InputString, ' ', 10).toFloat();
    currentPoseAngle.rb_theta2 = parseString(InputString, ' ', 11).toFloat();
    currentPoseAngle.rb_theta3 = parseString(InputString, ' ', 12).toFloat();
    flag.newPoseAngleFlag = true;
  }

  if (InputString.charAt(0) == 'd') {
    currentPoseAngle.lf_theta1 = defaultPoseAngle.lf_theta1;
    currentPoseAngle.lf_theta2 = defaultPoseAngle.lf_theta2;
    currentPoseAngle.lf_theta3 = defaultPoseAngle.lf_theta3;
    currentPoseAngle.rf_theta1 = defaultPoseAngle.rf_theta1;
    currentPoseAngle.rf_theta2 = defaultPoseAngle.rf_theta2;
    currentPoseAngle.rf_theta3 = defaultPoseAngle.rf_theta3;
    currentPoseAngle.lb_theta1 = defaultPoseAngle.lb_theta1;
    currentPoseAngle.lb_theta2 = defaultPoseAngle.lb_theta2;
    currentPoseAngle.lb_theta3 = defaultPoseAngle.lb_theta3;
    currentPoseAngle.rb_theta1 = defaultPoseAngle.rb_theta1;
    currentPoseAngle.rb_theta2 = defaultPoseAngle.rb_theta2;
    currentPoseAngle.rb_theta3 = defaultPoseAngle.rb_theta3;
    flag.newPoseAngleFlag = true;
  }
  if (InputString.charAt(0) == 'f') {
    poseCartesian.lf_x = parseString(InputString, ' ', 1).toFloat();
    poseCartesian.lf_y = 15 + parseString(InputString, ' ', 2).toFloat();
    poseCartesian.lf_z = parseString(InputString, ' ', 3).toFloat();
    poseCartesian.rf_x = parseString(InputString, ' ', 4).toFloat();
    poseCartesian.rf_y = 15 + parseString(InputString, ' ', 5).toFloat();
    poseCartesian.rf_z = parseString(InputString, ' ', 6).toFloat();
    poseCartesian.lb_x = parseString(InputString, ' ', 7).toFloat();
    poseCartesian.lb_y = 15 + parseString(InputString, ' ', 8).toFloat();
    poseCartesian.lb_z = parseString(InputString, ' ', 9).toFloat();
    poseCartesian.rb_x = parseString(InputString, ' ', 10).toFloat();
    poseCartesian.rb_y = 15 + parseString(InputString, ' ', 11).toFloat();
    poseCartesian.rb_z = parseString(InputString, ' ', 12).toFloat();
    flag.newPoseCartesianFlag = true;
  }
  if (InputString.charAt(0) == 'k') {
    flag.killServosFlag = true;
  }
  if (InputString.charAt(0) == 'i') {
    flag.getIMUDataFlag = true;
  }
  if (InputString.charAt(0) == 'p') {
    flag.sendPWMDataFlag = true;
  }
  if (InputString.charAt(0) == 'c') {
    flag.configMagnetFlag = true;
  }
  if (InputString.charAt(0) == 'C') {
    imuConfig.magXbias  = parseString(InputString, ' ', 1).toFloat();
    imuConfig.magYbias  = parseString(InputString, ' ', 2).toFloat();
    imuConfig.magZbias  = parseString(InputString, ' ', 3).toFloat();
    imuConfig.rotXbias  = parseString(InputString, ' ', 4).toFloat();
    imuConfig.rotYbias  = parseString(InputString, ' ', 5).toFloat();
    imuConfig.rotZbias  = parseString(InputString, ' ', 6).toFloat();
    imuConfig.accXbias  = parseString(InputString, ' ', 7).toFloat();
    imuConfig.accYbias  = parseString(InputString, ' ', 8).toFloat();
    imuConfig.accZbias  = parseString(InputString, ' ', 9).toFloat();
    imuConfig.magXscale = parseString(InputString, ' ', 10).toFloat();
    imuConfig.magYscale = parseString(InputString, ' ', 11).toFloat();
    imuConfig.magZscale = parseString(InputString, ' ', 12).toFloat();
    flag.updateIMUConfigFlag = true;
    udpClient.print("--modifed IMU config");
  }
}

// Convert input string to  string array.
String CommClass::parseString(String data, char separator, int index) {
  int found = 0;
  int strIndex[] = { 0, -1 };
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++) {
    if (data.charAt(i) == separator || i == maxIndex) {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }

  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

SensorClass::SensorClass() {}

void SensorClass::start() {
  mpu.setMagneticDeclination(30);
  mpu.setup(0x68);
  delay(2000);
}


void SensorClass::calibrate() {
  Serial.println("hold still  in 3,2,1 !!");
  delay(2000);
  mpu.calibrateAccelGyro();
  Serial.println("done !!");

}

void SensorClass::calibrateMag() {
  Serial.println("move around in fig of 8 in 3,2,1 !!");
  delay(3000);
  mpu.calibrateMag();
  Serial.println("done !!");
}

void SensorClass::tick() {

  if (mpu.update()) {
        imuData.rotX = mpu.getYaw();
        imuData.rotY = mpu.getPitch();
        imuData.rotZ = mpu.getRoll();
    }

  
  if (flag.configMagnetFlag) {
    calibrate();
    calibrateMag();
    imuConfig.accXbias  = mpu.getAccBiasX() ;
    imuConfig.accYbias  = mpu.getAccBiasY() ;
    imuConfig.accZbias  = mpu.getAccBiasZ() ;
    imuConfig.rotXbias  = mpu.getGyroBiasX();
    imuConfig.rotYbias  = mpu.getGyroBiasY();
    imuConfig.rotZbias  = mpu.getGyroBiasZ();
    imuConfig.magXbias  = mpu.getMagBiasX() ;
    imuConfig.magYbias  = mpu.getMagBiasY() ;
    imuConfig.magZbias  = mpu.getMagBiasZ() ;
    imuConfig.magXscale = mpu.getMagScaleX();
    imuConfig.magYscale = mpu.getMagScaleY();
    imuConfig.magZscale = mpu.getMagScaleZ();
    flag.sendConfigDataFlag = true;
    flag.configMagnetFlag =false;
  }

  if (flag.updateIMUConfigFlag){
    mpu.setAccBias(imuConfig.accXbias,imuConfig.accYbias,imuConfig.accZbias);
    mpu.setGyroBias(imuConfig.rotXbias,imuConfig.rotYbias,imuConfig.rotZbias);
    mpu.setMagBias(imuConfig.magXbias,imuConfig.magYbias,imuConfig.magZbias);
    mpu.setMagScale(imuConfig.magXscale,imuConfig.magYscale,imuConfig.magZscale);
    flag.updateIMUConfigFlag = false;
  }

}