# Cyber-Core

Este proyecto representa el trabajo en conjunto de tres jóvenes que comparten la pasión por la robótica. Con Python y Arduino, 
desarrollamos el robot para la competencia de la WRO Futuros Ingenieros. Aquí guardamos no solo nuestro código, sino también la 
experiencia, los aprendizajes y los retos que vivimos como equipo. Cada línea de programación, cada cable conectado y cada pieza ajustada 
representa horas de esfuerzo y dedicación, pero también momentos de alegría, descubrimiento y crecimiento personal.

Integrantes:

* Eleazar Abisaí Pacheco Oliva 
* Stefany Andrea Tobar de Paz 
* Sergio Andrés Carrera Canel

Misión

Nuestra misión es demostrar que la tecnología no es solo algo complicado que usan las grandes empresas, sino una herramienta que 
nosotros, como estudiantes, también podemos crear y aprovechar para resolver problemas reales. Queremos que nuestro proyecto muestre que 
con creatividad, dedicación y trabajo en equipo es posible transformar ideas en algo útil y funcional.

No buscamos únicamente construir un robot, sino aprender en el proceso, inspirar a otros jóvenes a interesarse por la ciencia y la 
ingeniería, y demostrar que la innovación está al alcance de todos si se combina disciplina con pasión.

Visión

Nuestra visión es llegar a un punto donde proyectos como el nuestro no se queden únicamente en una maqueta escolar, sino que puedan 
evolucionar hasta convertirse en soluciones que impacten positivamente en la vida diaria de las personas. Nos imaginamos un futuro donde 
los jóvenes tengamos más espacios para experimentar y compartir nuestras ideas, sin miedo a equivocarnos, porque de los errores también 
nacen avances importantes.

Queremos que lo que hoy empieza como un reto académico, en el futuro inspire a más generaciones a atreverse a pensar distinto y a usar la 
tecnología como una aliada para construir un mundo más eficiente, justo y sostenible.

Componentes del Proyecto

En el desarrollo de nuestro proyecto de robótica, fue fundamental contar con un conjunto de herramientas y dispositivos que permitieran 
llevar a cabo el diseño, la construcción y el funcionamiento del robot autónomo. Cada elemento utilizado cumple un papel específico 
dentro del sistema, aportando desde la parte estructural hasta la lógica de control y la interacción con el entorno.

Componentes básicos:
-
* Raspberry Pi 5 → cerebro principal del robot.
* Arduino UNO (Elegoo Shield) → controla motores y sensores.
* Motor DC de 12V → mueve las llantas traseras y proporciona tracción.
* Servomotor → controla la dirección del eje delantero.
* Cámara (webcam) → para detección de obstáculos y procesamiento de imágenes.
* Batería ELEGOO 7.4V → alimenta todo el sistema.
* 3 sensores ultrasónicos → detección de obstáculos a los lados y frente.
* Chasis o estructura del carrito → soporta todos los componentes y permite movilidad.
* Piezas impresas en 3D → para adaptar y fijar la electrónica y la batería al chasis.

Más allá de los componentes, lo realmente importante fue cómo los integramos. Cada conexión fue pensada para mantener la eficiencia y la 
seguridad eléctrica, cada línea de código escrita para optimizar el rendimiento. Fue un proceso de prueba y error, pero también de 
descubrimiento y mejora continua.

Bitácora del Proyecto:
-
08 de Enero del 2025

Comenzamos desarmando un carrito de control remoto para aprovechar el chasis de la parte trasera. También definimos los componentes que 
necesitaríamos para el proyecto. Además, iniciamos la programación base para el control del vehículo, estableciendo la estructura del 
código en Python para la Raspberry Pi.

22 de Enero del 2025

Avanzamos en la programación, implementando las primeras funciones para el movimiento del motor y la gestión de energía. También 
definimos el modelo de control remoto que se integraría. Fue un reto lograr que la comunicación entre la Raspberry y el Arduino fuera 
fluida, pero logramos los primeros movimientos básicos.

10 de Marzo del 2025

Imprimimos en 3D las piezas principales: la base superior y la base inferior que sostendrían la batería y las placas electrónicas. Estas 
pruebas nos ayudaron a confirmar que el diseño encajaba en el chasis. Fue la primera vez que vimos nuestro proyecto tomar forma física 
más allá de los esquemas en papel.

15 de Abril del 2025

Verificamos la estabilidad del chasis y realizamos ajustes en el diseño de las piezas impresas para mejorar la distribución del peso. 
También avanzamos en la lógica de control y comenzamos con la planificación de la integración de la cámara, que sería esencial para la 
detección de obstáculos.

28 de Mayo del 2025

Pedimos el tren delantero y la placa Raspberry en la tienda electrónica. También investigamos sobre controladores de motores y sobre 
librerías de visión por computadora. Empezamos a trabajar con OpenCV para detección de colores.

20 de Junio del 2025

Nos llegó el tren delantero y comenzamos a implementarlo en el chasis. Fue necesario modificar las piezas impresas para lograr un buen 
acople, lo cual nos enseñó la importancia de la iteración en el diseño.

10 de Julio del 2025

Recibimos la Raspberry Pi e iniciamos la configuración del sistema operativo. Instalamos librerías necesarias para control de hardware y 
procesamiento de imágenes. Implementamos la cámara para la detección de obstáculos, probando filtros de color para diferenciar entre 
objetos rojos y verdes.

25 de Julio del 2025

Finalizamos la integración física de todos los componentes: chasis, tren delantero, placa, batería y cámara. Realizamos pruebas básicas 
de encendido para confirmar que todo estuviera correctamente alimentado. Fue un día emocionante porque por primera vez nuestro prototipo 
estuvo completo.

11 - 25 de Agosto del 2025

Comenzamos pruebas de funcionamiento del prototipo, evaluando tanto el control manual como la respuesta ante obstáculos. Descubrimos 
problemas de estabilidad en la lectura de sensores y tuvimos que ajustar los parámetros del código. Poco a poco, logramos que los 
movimientos fueran más precisos y menos bruscos.

26 de Agosto del 2025

Probamos el sistema de detección de obstáculos en diferentes escenarios de luz. Nos dimos cuenta de que la cámara respondía distinto en 
ambientes con poca iluminación, lo que nos llevó a implementar calibraciones dinámicas. También optimizamos el código para reducir la 
latencia entre la cámara y la ejecución de los motores.

27 de Agosto del 2025

Probamos específicamente la detección del cubo rojo. El reto más grande fue que el carrito confundía ciertos tonos rojos con el color 
naranja. Implementamos un filtrado por rango de color en HSV y ajustamos varias veces hasta que los resultados fueron estables.

28 de Agosto del 2025

Hicimos pruebas más avanzadas con la detección de obstáculos verdes. Nos dimos cuenta de que la cámara tenía problemas con los reflejos y 
los brillos, por lo que añadimos un ajuste en el balance de blancos y filtros de suavizado de imagen. Con estas mejoras, el robot empezó 
a reconocer con más confianza los objetos.

Retos, aprendizajes y crecimiento:
-
Uno de los mayores retos fue la integración entre hardware y software. No bastaba con que la programación estuviera bien estructurada, 
también era necesario que las conexiones eléctricas fueran correctas y que la distribución física de los componentes no afectara el 
rendimiento.

También aprendimos que la paciencia y el trabajo en equipo son esenciales. Hubo días en los que nada funcionaba: la cámara no detectaba, 
los motores no respondían, o el código lanzaba errores inexplicables. Pero en lugar de rendirnos, cada obstáculo se convirtió en una 
oportunidad para investigar más, probar nuevas soluciones y reforzar nuestra comunicación como equipo.

Este proyecto no solo nos dio habilidades técnicas, sino también valores como la perseverancia, la organización y la confianza en que con 
esfuerzo se pueden lograr grandes cosas.

Impacto y proyecciones futuras:
-

Aunque hoy nuestro robot es un prototipo, vemos en él un reflejo de lo que podría convertirse en un futuro: un sistema autónomo capaz de 
adaptarse a entornos más complejos, de colaborar en tareas de logística, seguridad o incluso apoyo en emergencias.

Nuestro sueño es que este tipo de proyectos puedan trascender más allá de las competencias escolares y convertirse en propuestas reales 
que resuelvan problemas cotidianos. Así como nosotros comenzamos con un carrito reciclado y un par de ideas, sabemos que otros jóvenes 
también pueden crear proyectos que transformen su entorno.

Queremos que Cyber-Core sea recordado no solo como un robot de competencia, sino como el inicio de un camino de innovación, aprendizaje y 
motivación para quienes vengan después.
