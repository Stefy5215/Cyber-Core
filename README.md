# Cyber-Core
Este proyecto representa el trabajo en conjunto de tres jovenes que comparten la pasión por la robótica. Con Python y Arduino, desarrollamos el robot para la competencia de la WRO FUTUROS INGENIEROS. Aquí guardamos no solo nuestro código, sino también la experiencia y los retos que vivimos como equipo.

COMPONENTES BÁSICOS 
* Raspberry
* Arduino UNO
* Placa Shield  de Elegoo
* Servomotor 
* Motor DC
* Estructura de carrito

CÓDIGO EN ARDUINO UNO

#include <Servo.h>
#include "DeviceDriverSet.h"

Servo steeringServo;
DeviceDriverSet_Motor motor;

const int SERVO_PIN = 10;
const int BUTTON_PIN = 2;
const int SERVO_CENTER = 120;
const int SERVO_MIN = 70;
const int SERVO_MAX = 170;

String inputString = "";
bool stringComplete = false;
bool motorActivo = false;
bool botonPrevio = HIGH;

void setup() {
  Serial.begin(115200);
  steeringServo.attach(SERVO_PIN);
  steeringServo.write(SERVO_CENTER);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  motor.begin();
}

void loop() {
  bool botonPresionado = (digitalRead(BUTTON_PIN) == LOW);
  if (botonPrevio == HIGH && botonPresionado) {
    motorActivo = !motorActivo;
    if (!motorActivo) {
      pararMotor();
    }
    delay(300);
  }
  botonPrevio = botonPresionado;

  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    int steer = 0, vel = 0, line = 0;
    if (sscanf(cmd.c_str(), "STEER:%d,VEL:%d,LINE:%d", &steer, &vel, &line) == 3) {
      // Controla el servo segÃºn steer
      steer = constrain(steer, -100, 100);
      int angle = map(steer, -100, 100, SERVO_MIN, SERVO_MAX);
      angle = constrain(angle, SERVO_MIN, SERVO_MAX);
      steeringServo.write(angle);

      // Controla los motores segÃºn vel
      if (motorActivo) {
        int velFinal = (line == 1) ? 150 : vel;
        moverMotores(velFinal);
      } else {
        pararMotor();
      }
    }
  }
}

void moverMotores(int velocidadBase) {
  motor.control(
    DeviceDriverSet_Motor::BACKWARD, velocidadBase,
    DeviceDriverSet_Motor::BACKWARD, velocidadBase,
    true
  );
}

void pararMotor() {
  motor.control(
    DeviceDriverSet_Motor::BACKWARD, 0,
    DeviceDriverSet_Motor::BACKWARD, 0,
    false
  );
}

BITÁCORA 
08 de Enero del 2025
comenzamos desarmando un carrito control remoto para poder utilizar el chasis de la parte trasera.

10 de Marzo del 2025
imprimimos en la impresora 3D las piezas, la de arriba y la de abajo que sostiene la batería y las placas.




