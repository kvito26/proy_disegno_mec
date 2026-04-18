# PROYECTO DISEÑO MECÁNICO - VEHÍCULO EXPLORADOR MINERO
El presente repositorio contiene el código realizado para integración con *hardware* del automovil explorador, así también comandos y archivos adicionales el cual dan un panorama y/o idea general del funcionamiento de éste proyecto.

En primera, se hace uso de los siguientes componentes electrónicos:
	- Rarspberry Pi V.3
	- DTOF LDROBOT LiDAR LD19

Este repositorio tiene como base (*fork*) el repositorio del fabricante del LiDAR, especificamente el repositorio del [SDK](https://github.com/ldrobotSensorTeam/ldlidar_stl_sdk) para Linux.

## Compilación del Programa para el Funcionamiento del Sensor Lidar.
## Toma de datos sin visualización en tiempo real
A la toma de datos estático, se refiere a que no vamos a ver ninguna interfaz en donde se muestre la visualizacion de datos en tiempo real, simplemente todos los datos que el sensor haya tomado serán guardados en un archivo tipo `.log` dentro del directorio `./log`.
