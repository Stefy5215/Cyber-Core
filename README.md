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



Bitácora del Proyecto

08 de Enero del 2025
Comenzamos desarmando un carrito de control remoto para aprovechar el chasis de la parte trasera. También definimos los componentes que necesitaremos para el proyecto. Además, iniciamos la programación base para el control del vehículo, estableciendo la estructura del código en Python para la Raspberry Pi.

22 de Enero del 2025
Realizamos avances en la programación, implementando las primeras funciones para el movimiento del motor y la gestión de energía. También definimos el modelo de control remoto que se integrará.

10 de Marzo del 2025
Hoy imprimimos en la impresora 3D las piezas principales: la base superior y la base inferior que sostendrán la batería y las placas electrónicas. Probamos el ensamblaje de estas piezas para asegurarnos de que encajaran correctamente en el chasis.

15 de Abril del 2025
Verificamos la estabilidad del chasis y realizamos ajustes en el diseño de las piezas impresas para mejorar la distribución del peso. También continuamos avanzando en la lógica de control y comenzamos con la planificación de la integración de la cámara.

28 de Mayo del 2025
El día de hoy pedimos el tren delantero y la placa Raspberry en la tienda electrónica. También investigamos los controladores necesarios para los motores y el sistema de visión.

20 de Junio del 2025
Nos llegó el tren delantero y comenzamos a implementarlo en el chasis. Ajustamos las piezas impresas para que encajaran correctamente con el nuevo sistema.

10 de Julio del 2025
Hoy recibimos la placa Raspberry Pi e iniciamos la configuración del sistema operativo y la instalación de librerías necesarias. Además, implementamos una cámara para la detección de obstáculos, que será fundamental para la navegación autónoma.

25 de Julio del 2025
Finalizamos la integración física de todos los componentes: chasis, tren delantero, placa, batería y cámara. Hicimos pruebas básicas para verificar que la alimentación y las conexiones funcionaran sin problemas.

11 - 25 de Agosto del 2025
Comenzamos con las pruebas de funcionamiento del prototipo, evaluando el control manual y la respuesta del sistema ante obstáculos. Ajustamos parámetros en el código para mejorar la estabilidad y la precisión de los movimientos.

26 de Agosto del 2025
Realizamos pruebas con el sistema de detección de obstáculos en diferentes escenarios. También optimizamos el código para reducir la latencia entre la cámara y la ejecución de los movimientos.






