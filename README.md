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

## Compilación del Programa SDK para el Funcionamiento del Sensor Lidar.
Para este punto se clona y se compila el código para ambas computadoras mencionadas anteriormente.

Antes de iniciar, se deben actualizar los repositorios y paquetes instalados en las computadoras, estos comandos sirven para ambos:

```bash
sudo apt-get update && sudo apt-get upgrade -y

```

Instalar los paquetes necesarios:

```bash
sudo apt-get install git ssh build-essential cmake

```

	1. Clonar repositorio para ambas computadoras.

	```bash
	cd ~/
	git clone https://github.com/kvito26/proy_disegno_mec.git
	```

	2. Compilación del Programa
		- Compilación del Programa para la Computadora Receptora (amd64).
			Ir dentro del directorio del repositorio clonado y crear un nuevo directorio `build`
			```bash
			cd proy_disegno_mec/ && mkdir build
			```

			Ir dentro del nuevo directorio `build/` y ejecutar `cmake`.
			```bash
			cd build/
			cmake ../
			```
			Un vez ejecutado el comando `cmake`, se tendría que apreciar lo siguiente:

			<pre>
			kevin@vito-asus:~/proy_disegno_mec/build$ cmake ../
			-- The C compiler identification is GNU 10.2.1
			-- The CXX compiler identification is GNU 10.2.1
			-- Detecting C compiler ABI info
			-- Detecting C compiler ABI info - done
			-- Check for working C compiler: /usr/bin/cc - skipped
			-- Detecting C compile features
			-- Detecting C compile features - done
			-- Detecting CXX compiler ABI info
			-- Detecting CXX compiler ABI info - done
			-- Check for working CXX compiler: /usr/bin/c++ - skipped
			-- Detecting CXX compile features
			-- Detecting CXX compile features - done
			-- Mode: Debug
			-- optional:-std=c++11 -Wall -Wextra -Wpedantic -g2 -ggdb
			-- Configuring done
			-- Generating done
			-- Build files have been written to: /home/kevin/proy_disegno_mec/build
			</pre>
			
			Compilar el programa:
			```bash
			make
			```

			Al copilar el programa, se debería observar la siguiente salida estandar:

			<pre>
			kevin@vito-asus:~/proy_disegno_mec/build$ make
			Scanning dependencies of target ldlidar_driver_shared
			[  6%] Building CXX object CMakeFiles/ldlidar_driver_shared.dir/ldlidar_driver/src/core/ldlidar_driver.cpp.o
			[ 12%] Building CXX object CMakeFiles/ldlidar_driver_shared.dir/ldlidar_driver/src/dataprocess/lipkg.cpp.o
			[ 18%] Building CXX object CMakeFiles/ldlidar_driver_shared.dir/ldlidar_driver/src/filter/tofbf.cpp.o
			[ 25%] Building CXX object CMakeFiles/ldlidar_driver_shared.dir/ldlidar_driver/src/logger/log_module.cpp.o
			[ 31%] Building CXX object CMakeFiles/ldlidar_driver_shared.dir/ldlidar_driver/src/networkcom/network_socket_interface_linux.cpp.o
			[ 37%] Building CXX object CMakeFiles/ldlidar_driver_shared.dir/ldlidar_driver/src/serialcom/serial_interface_linux.cpp.o
			[ 43%] Linking CXX shared library libldlidar_driver.so
			[ 43%] Built target ldlidar_driver_shared
			Scanning dependencies of target ldlidar_driver_static
			[ 50%] Building CXX object CMakeFiles/ldlidar_driver_static.dir/ldlidar_driver/src/core/ldlidar_driver.cpp.o
			[ 56%] Building CXX object CMakeFiles/ldlidar_driver_static.dir/ldlidar_driver/src/dataprocess/lipkg.cpp.o
			[ 62%] Building CXX object CMakeFiles/ldlidar_driver_static.dir/ldlidar_driver/src/filter/tofbf.cpp.o
			[ 68%] Building CXX object CMakeFiles/ldlidar_driver_static.dir/ldlidar_driver/src/logger/log_module.cpp.o
			[ 75%] Building CXX object CMakeFiles/ldlidar_driver_static.dir/ldlidar_driver/src/networkcom/network_socket_interface_linux.cpp.o
			[ 81%] Building CXX object CMakeFiles/ldlidar_driver_static.dir/ldlidar_driver/src/serialcom/serial_interface_linux.cpp.o
			[ 87%] Linking CXX static library libldlidar_driver.a
			[ 87%] Built target ldlidar_driver_static
			Scanning dependencies of target ldlidar_stl_node
			[ 93%] Building CXX object CMakeFiles/ldlidar_stl_node.dir/src/linux_demo/demo.cpp.o
			[100%] Linking CXX executable ldlidar_stl_node
			[100%] Built target ldlidar_stl_node
			</pre>

		- Compilación del Programa para la Computadora del Vehículo (arm64).

			Para integrar el mismo programa para la Computadora Raspberry Pi, se debe seguir exactamente el anterior punto.

			Sin embargo, se hizo una modificación el código original para su correcta compilación. El detalle de la modificación es la siguiente:

			- Se agregó el siguiente *header* 
				```
				#include <pthread.h> 
				```	

				en el archivo `log_module.cpp` que esta localizado en la siguiente dirección:
				```bash
				cd ~/proy_disegno_mec/ldlidar_driver/src/logger
				```

			Ya que en dispositivos con procesadores con arquitectura arm64 no enlazan el *header* por defecto o automaticamente.


## Toma de datos sin visualización en tiempo real
A la toma de datos estático, se refiere a que no vamos a ver ninguna interfaz en donde se muestre la visualizacion de datos en tiempo real, simplemente todos los datos que el sensor haya tomado serán guardados en un archivo tipo `.log` dentro del directorio `./log`.
