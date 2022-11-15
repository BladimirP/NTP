/* 
end map para saber puertos disoinibles, tienen que ser mayores 9000 
06 NOV 1era Version
16 NOV 2da Version
23 NOV Terminar
*/
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
/*
- Timestamps 64 bits 
- La parte entera son 32 bits
- La parte flotante son los ultimos 32
- Esto es cuanto tiempo a pasado en seg desde las 00:00 del 01.01.1900
*/

/*

LEAP INDICATOR (LI) : 2 bits
- Indica si para un año se necesita más o menos 1 seg

VERSION NUMBER (VN) : 3 bits
- Version SNTP

MODE: 3 bits
- 0, reservado
- 1, simetria activada
- 2, simetria pasiva
- 3, cliente
- 4, servidor
- 5, broadcast
- 6, reservado para msj de control NTP
- 7, reservado para uso privado

STRATUM : 8 bits
- 0,        sin especificar
- 1,        referencia primaria
- [2, 15]   referencia secundaria
- [16, 255] reservado

POLL INTERVAL : 8 bits
- Entero que indica el maximo intervalo entre mensajes sucesivos.
- Indica los segundos a la potencia de dos mas cercana

PRECISION : 8 bits
- Precision del reloj local en seg en comparacion a la potencia de 2 mas cercana.
- -6 < valor < -18

ROOT DELAY : 32 bits
- Retardo total de una roundtrip
- Pueder ser positivo y negativo.
- Indica seg, punto decimal entre el bit 15 y 16

ROOT DISPERSION : 32 bit
- Valor flotante sin signo
- Que indica seg del error relativo maximo comparado a la referencia primaria
- punto entre el bit 15 y 16

RERERENCE CLOCK IDENTIFIER : 32 bit
- identifica un reloj en particular
- depende del valor del stratum
    - 0 ó 1 : String ASCII, sin margen, justificado hacia la izquierda, en 4 octetos.
    - ver tabla

Reference Timestamp : 64 bits
- La ultima hora sincronizda

Originate Timestamp : 64 bits
- Establecido por el cliente
- Es su hora al enviar la peticion

Receive Timestamp: 64 bits
- Establecido por el server
- Hora en que me llego la peticion

Transmit Timestamp : 64 bits
- establecido por el server
- la hora de respuesta

Total : 384 bits
*/