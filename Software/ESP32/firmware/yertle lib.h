#ifndef YERTLE_LIB_H
#define YERTLE_LIB_H

#include <Arduino.h>
#include <FaBoPWM_PCA9685.h>
#include <string>

extern struct PoseAngle {
  float lf_theta1 = 0.0;
  float lf_theta2 = 0.0;
  float lf_theta3 = 0.0;
  float rf_theta1 = 0.0; 
  float rf_theta2 = 0.0;
  float rf_theta3 = 0.0;
  float lb_theta1 = 0.0;
  float lb_theta2 = 0.0;
  float lb_theta3 = 0.0;
  float rb_theta1 = 0.0;
  float rb_theta2 = 0.0;
  float rb_theta3 = 0.0;
} defalutPoseAngle, currentPoseAngle;

extern struct ImuData {
  float magX = 0.0;
  float magY = 0.0;
  float magZ = 0.0;
  float rotX = 0.0;
  float rotY = 0.0;
  float rotZ = 0.0;
  float accX = 0.0;
  float accY = 0.0;
  float accZ = 0.0;
} imuData;

extern struct ImuConfig {
  float magXbias = 0.0;
  float magYbias = 0.0;
  float magZbias = 0.0;
  float rotXbias = 0.0;
  float rotYbias = 0.0;
  float rotZbias = 0.0;
  float accXbias = 0.0;
  float accYbias = 0.0;
  float accZbias = 0.0;
  float magXscale= 0.0;
  float magYscale= 0.0;
  float magZscale= 0.0;
} imuConfig;


extern struct PoseCartesian {  // Data type for cartesian pose xyz.
  float lf_x = -1.0;
  float lf_y = 20.0;
  float lf_z = 0;
  float rf_x = -1.0;
  float rf_y = 20.0;
  float rf_z = 0;
  float lb_x = -1.0;
  float lb_y = 20.0;
  float lb_z = 0;
  float rb_x = -1.0;
  float rb_y = 20.0;
  float rb_z = 0;
} defalutPoseCartesian, poseCartesian;

extern struct Flags{
  bool newPoseAngleFlag = false ;
  bool newPoseCartesianFlag = false;
  bool killServosFlag = false;
  bool getIMUDataFlag = false;
  bool sendPWMDataFlag = false;
  bool gotSerialDataFlag = false;
  bool gotUdpDataFlag = false;
  bool configMagnetFlag = false;
  bool sendConfigDataFlag = false;
  bool updateIMUConfigFlag = false;
} flags;

//extern String InputDataString;

class ServoClass {
public:
  ServoClass();
  void start();
  void tick();
  void moveToPose();
  void solveIk();
private:
  void Ik(float deltaX, float deltaY, float deltaZ, float& theta1, float& theta2, float& theta3);
  int sgn(float x);
  void sendPWMData();
  void killServos();
  void setAngle(int id, float angle, bool direction, float lowerLimit, float upperLimit, float offset);
  int angleToPWM(bool direction, float angle);
  float filterLimits(float inputValue, float lowerLimit, float upperLimit);
  const struct ServoId {
    int lf_theta1 = 15;
    int lf_theta2 = 11;
    int lf_theta3 = 7;

    int rf_theta1 = 14;
    int rf_theta2 = 10;
    int rf_theta3 = 6;

    int lb_theta1 = 13;
    int lb_theta2 = 9;
    int lb_theta3 = 5;

    int rb_theta1 = 12;
    int rb_theta2 = 8;
    int rb_theta3 = 4;
  } servoId;
  //Upper and lower limits of the servo
  const struct limits {
    float lowerTheta1 = -45.0;
    float upperTheta1 = 45.0;

    float lowerTheta2 = -90.0;
    float upperTheta2 = 20.0;

    float lowerTheta3 = 13.0;
    float upperTheta3 = 90.0;

  } defaultLimits;
  // forward direction for the servo (L/R have reversed directions).
  const struct direction {
    bool lf_theta1 = 1;
    bool lf_theta2 = 1;
    bool lf_theta3 = 0;

    bool rf_theta1 = 1;
    bool rf_theta2 = 0;
    bool rf_theta3 = 1;

    bool lb_theta1 = 0;
    bool lb_theta2 = 1;
    bool lb_theta3 = 0;

    bool rb_theta1 = 0;
    bool rb_theta2 = 0;
    bool rb_theta3 = 1;

  } defaultDirection;

  struct ServoOffsets {
    float lf_theta1 = -62;
    float lf_theta2 = 9;
    float lf_theta3 = 0;

    float rf_theta1 = 17;
    float rf_theta2 = -144;
    float rf_theta3 = 0;

    float lb_theta1 = -45;
    float lb_theta2 = -88;
    float lb_theta3 = 66;

    float rb_theta1 = -116;
    float rb_theta2 = -66;
    float rb_theta3 = 0;
  } servoOffsets;
};

class CommClass {
public:
  CommClass();
  struct ControlByteMap {  // these are codes for functions (custom UART protocol)
    static constexpr uint8_t GET_VOLTAGE = 0x00;
    static constexpr uint8_t GET_CURRENT = 0x01;
    static constexpr uint8_t GET_SERVO_POSITION = 0x02;
    static constexpr uint8_t SET_SERVO_ANGLE = 'a';
    static constexpr uint8_t SET_SERVO_OFF = 'k';
  } controlChar;
  void listen();
  void start();
private:
  void DecodeInputString(String InputString);
  String parseString(String data, char separator, int index);
  
};

class SensorClass {
public:
  SensorClass();
  void start();
  void tick();
  void calibrate();
  void calibrateMag();
private:
  float xOffAvg; 
  float yOffAvg; 
  float zOffAvg; 
  float xOff; 
  float yOff; 
  float zOff;
  float currentTime =0.0;
  float previousTime;
  float sampleTime;
};

#endif