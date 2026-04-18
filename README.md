# PROYECTO DISEÑO MECÁNICO - VEHÍCULO EXPLORADOR MINERO
El presente repositorio contiene el código realizado para integración con *hardware* del automovil explorador, así también comandos y archivos adicionales el cual dan un panorama y/o idea general del funcionamiento de éste proyecto.

En primera, se hace uso de los siguientes componentes electrónicos:

	- Rarspberry Pi V.3
	- DTOF LDROBOT LiDAR LD19

Este repositorio tiene como base (*fork*) el repositorio del fabricante del LiDAR, especificamente el repositorio del [SDK](https://github.com/ldrobotSensorTeam/ldlidar_stl_sdk) para Linux.

> [!NOTE]
> Para este repositorio, se harán las explicaciones desde la instalación del sistemaoperativo para el Raspberry Pi hasta las ejecuciones de los binarios en todos los casos. 

> [!IMPORTANT]
> En este proyecto se usan dos computadoras. La primera integrada en el vehículo el cual es el Raspberry Pi el cual procesa, recibe y envía información. La segunda, es la computadora receptora de toda la información y así también el envío de comandos hacia la computadora del vehículo. En este documento se hará la diferenciación entre ambas computadoras al momento de ejecutar comandos, compilar y/o ejecutar determinado código. 

> [!IMPORTANT]
> Ambas computadoras mencionadas anteriormente tienen como sistema operativo en base al *kernel* **Linux** y especificamente basados en la distribución **Debian GNU/Linux**, parte de los comandos que se presentan aquí pertenecen exlusivamente a la distribución mencionada.

## Instalación del Sistema Operativo para el Raspberry Pi V.3

## Compilación del Programa para el Funcionamiento del Sensor Lidar.
Para este punto se clona y se compila el código para ambas computadoras mencionadas anteriormente.


## Toma de datos sin visualización en tiempo real
A la toma de datos estático, se refiere a que no vamos a ver ninguna interfaz en donde se muestre la visualizacion de datos en tiempo real, simplemente todos los datos que el sensor haya tomado serán guardados en un archivo tipo `.log` dentro del directorio `./log`.
