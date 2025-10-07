# Cyber-Core

Este repositorio contiene la documentación para la participación de Cyber-Core para la 
competencia de la categoria WRO Futuros Ingenieros 2025. Nuestro vehículo está 
diseñado por un equipo guatemalteco apasionado por la robótica.






#EQUIPO


(foto)



Somos un equipo pequeño, pero con un corazón enorme. Solo somos dos, pero juntos formamos una fuerza imparable impulsada desde la 
pasión por la robótica y el deseo de superarnos. Cada paso que damos, cada error que corregimos y cada avance que logramos es el 
resultado de trabajo duro, largas horas y una confianza inquebrantable entre nosotros. No tenemos un gran número, pero tenemos algo 
más poderoso:la determinación de nunca rendirnos y la certeza de que, con creatividad y trabajo en equipo, podemos lograr cosas 
increíbles.Porque no se trata de cuántos somos… se trata de cuánto creemos en lo que hacemos.


                          ELEAZAR ABISAI PACHECO OLIVA
 -EDAD: 17 AÑOS.
 -ENCARGADO DE: Programación y logistica de componentes.
 
 Soy estudiante del Colegio Villa Real Atlántico 1 y formo parte del grado de quinto 
 Bachillerato. Para mi, la robótica representa un camino de aprendizaje y superación, 
 donde cada proyecto me ha permitido desarrollar liderazgo, creatividad y confianza en 
 en sus capacidades, siempre trabajando en equipo para alcanzar nuevas metas.



                           STEFANY ANDREA TOBAR DE PAZ
 
 -EDAD: 15 AÑOS.
 -ENCARGADA DE: Diseño y electrónica.

  soy estudiante del Colegio Villa Real Atlántico 1 y formo parte del grado de tercero 
  básico sección B. para mi, la robótica es más que una materia: es un espacio donde 
  puedo expresar mi creatividad, aprender de los errores y crecer junto a mi equipo. A 
  través de ella he descubierto que cada reto es una oportunidad para mejorar y que 
  condedicacion es posible convertir las ideas en logros.



  


-MISIÓN

Nuestra misión es diseñar, construir y programar un vehículo autónomo que sea capaz de enfrentar con éxito los diversos retos de movilidad 
planteados en la competencia. Para lograrlo, integramos principios fundamentales de la ingeniería, la creatividad, el pensamiento crítico y la 
innovación tecnológica, con el objetivo de desarrollar soluciones que no solo sean funcionales, sino también 
seguras, eficientes y sostenibles.

Nos enfocamos en el aprendizaje constante, el trabajo colaborativo y la aplicación práctica de nuestros conocimientos, creando un entorno donde cada 
integrante del equipo pueda aportar sus habilidades y crecer profesional y personalmente. A través de este proyecto, buscamos no solo alcanzar un 
alto rendimiento técnico, sino también fomentar valores como la responsabilidad, la resiliencia y el compromiso con el desarrollo de tecnologías que 
impacten positivamente a la sociedad.

Queremos demostrar que la robótica y la automatización no son solo herramientas del futuro, sino oportunidades presentes para construir un mundo más 
inteligente, accesible y sostenible, desde la perspectiva de jóvenes con visión y pasión por la ingeniería.





-VISIÓN

Nuestra visión es convertirnos en un equipo líder y referente en el ámbito de la robótica e innovación tecnológica, reconocidos por nuestra 
capacidad para transformar ideas en soluciones concretas que contribuyan a mejorar la movilidad del futuro. Aspiramos a ser un ejemplo de cómo la 
combinación de creatividad, disciplina, conocimiento técnico y trabajo en equipo puede dar lugar a desarrollos que inspiren a otras generaciones de 
estudiantes, ingenieros y entusiastas de la tecnología.

Queremos ir más allá de una competencia: buscamos dejar huella como un grupo que se atreve a imaginar, diseñar y construir tecnologías disruptivas
con impacto real. Visualizamos un futuro en el que nuestra experiencia y nuestras creaciones sirvan de base para nuevos proyectos, investigaciones y 
emprendimientos que promuevan la evolución hacia sistemas de transporte más inteligentes, seguros y sostenibles.

Nos proyectamos como una comunidad de aprendizaje que crece con cada desafío, que comparte el conocimiento y que mantiene viva la pasión por 
innovar, creyendo firmemente que la tecnología, guiada por principios éticos y humanos, puede ser una herramienta transformadora al servicio del 
bienestar colectivo.







-RETO

El reto de la competencia WRO Futuros Ingenieros busca que los estudiantes desarrollen habilidades de diseño, innovacion y trabajo en equipo através
de la construccion y programacion de vehículos autónomos. Este desafío no solo pone a prueba la creatividad y la precision, sino también lacapacidad 
de resolver problemas reales aplicando la ingenieria y la tecnología. Más que una competencia,representa una oportunidad para crecer, compartir 
conocimientos y acercarnos al mundo de la ingeniería del futuro.

- Detectar y evitar obstáculos
- Seguir el camino de las pistas de manera autónoma
- Reconocer señales o marcas de la pista
- Adaptarse a cambios en el recorrido
- Mantener estabilidad y precisión en todo momento
- Completar el recorrido en el menor tiempo posible






-RESUMEN DEL CARRITO

Nuestro carrito ha sido desarrollado para operar de manera completamente autónoma, sin intervención humana directa durante su desplazamiento. Su
funcionamiento se basa en el uso de una cámara y redes neuronales, lo que le permite tomar decisiones inteligentes en tiempo real, dependiendo del 
entorno que percibe a través de la visión artificial.

-Fase 1 – Navegación por Colores (Líneas Azul y Naranja)
Durante la primera fase del recorrido, el carrito utiliza el procesamiento de imágenes captadas por la cámara frontal para identificar líneas de 
colores que indican el camino a seguir. El algoritmo, entrenado mediante una red neuronal, analiza el orden en el que aparecen las líneas naranja y 
azul sobre la pista:

- Si se detecta primero la línea naranja, el carrito interpreta que debe girar hacia la derecha.

- Si se detecta primero la línea azul, ejecuta un giro hacia la izquierda.

Este comportamiento es posible gracias al entrenamiento previo del modelo de inteligencia artificial, que fue alimentado con múltiples ejemplos de 
trayectorias, colores y decisiones asociadas, permitiendo así una navegación adaptativa y precisa.

- Fase 2 – Detección y Evasión de Obstáculos (Cubos Rojos y Verdes)
En la segunda fase, el carrito se enfrenta a obstáculos representados por cubos de color rojo y verde. Mediante visión por computadora, el sistema
identifica el color del cubo y decide la maniobra adecuada:

- Si detecta un cubo rojo, gira hacia la derecha para evitarlo.

- Si detecta un cubo verde, realiza la evasión por la izquierda.

Esta lógica permite que el carrito navegue de forma segura, reconociendo su entorno y tomando decisiones en tiempo real. El uso de redes neuronales 
 y segmentación por color mejora la precisión en la clasificación de objetos.

-Fase 3 – Estacionamiento Autónomo (Zona con Tablas Rosadas)
En la tercera y última fase, el carrito debe completar su recorrido realizando una maniobra de estacionamiento autónomo dentro de una zona 
específica delimitada por tablas de color rosado.            


| Front | Back |
|-------|------|
<img src="https://github.com/chaBotsMX/chaBots-NERV-WRO-Future-Engineers-2025/blob/docs-nacional/v-photos/national/v-front.jpeg?raw=true" width="250"> | <img src="https://github.com/chaBotsMX/chaBots-NERV-WRO-Future-Engineers-2025/blob/docs-nacional/v-photos/national/v-back.jpeg?raw=true" width="250">

| Left | Right |
|------|-------|
<img src="https://github.com/chaBotsMX/chaBots-NERV-WRO-Future-Engineers-2025/blob/docs-nacional/v-photos/national/v-left.jpeg?raw=true" width="250"> | <img src="https://github.com/chaBotsMX/chaBots-NERV-WRO-Future-Engineers-2025/blob/docs-nacional/v-photos/national/v-right.jpeg?raw=true" width="250">

| Top | Bottom |
|------|--------|
<img src="https://github.com/chaBotsMX/chaBots-NERV-WRO-Future-Engineers-2025/blob/docs-nacional/v-photos/national/v-top.jpeg?raw=true" width="250"> | <img src="https://github.com/chaBotsMX/chaBots-NERV-WRO-Future-Engineers-2025/blob/docs-nacional/v-photos/national/v-bottom.jpeg?raw=true" width="250">








                                           
