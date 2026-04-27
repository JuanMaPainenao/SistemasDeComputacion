# Sistemas de Computacion
## TP3 - Modo real vs modo protegido


### Creacion de una imagen booteable

Crear imagen booteable simple:
```
printf '\364%509s\125\252' > main.img
```

Correr la imagen en Quemu. Quemu es un emulador y virtualizador de hardware de codigo abierto. Como emulador traduce instrucciones de una arquitectura a otra y como virtualizador, cuando la arquitectura coincide con la del host puede usar aceleracion por hardware.

Instalacion de Quemu:

```
sudo apt install qemu-system-x86
```

El comando:
```
qemu-system-x86_64 --drive file=main.img,format=raw,index=0,media=disk
```
Crea una PC virtual completa y arranca la imagen como lo haria hardware real.

#### Gif con todo el proceso
![QEMU corriendo main.img](img/1.gif)

La maquina donde se realizo esta consigna no cuenta con el modo CSM (Compatibility Support Module), lo que imposibilita poder seguir arrancando cosas legacy/MBR. Por ende el pendrive no aparece entre las opciones de arranque.

### UEFI y Coreboot

### ¿Qué es UEFI? ¿como puedo usarlo? Mencionar además una función a la que podría llamar usando esa dinámica.  
UEFI (Unified Extensible Firmware Interface) es el reemplazo moderno del antiguo BIOS (Basic Input/Output System), que era el sistema de firmware que arrancaba computadoras, desarrolado por Intel. UEFI ofrece una interfaz estandar entre el sistema operativo y el firmware de la maquina. 
A diferencia de la BIOS que era basica y corria en modo real de 16 bits, lo que significaba que tenia accesos a solo 1MiB de memoria, UEFI pasa inmediatamente a modo protegido de 32 o 64 bits con acceso a espacio de memoria de 4GiB en 32 bits y 16EiB en 64, lo que le permite el acceso total a la memoria RAM desde el arranque.
La BIOS permitia hasta 4 particiones primarias y discos de 2TiB mientras que UEFI usa GPT (GUID Partition Table) que soporta hasta 128 particiones y 9.4 ZiB de capacidad de discos.
La UEFI implementa tambien un sistema de verificacion criptografica donde el firmware solo ejecuta bootloaders firmados con claves autorizadas (Secure Boot).
El CSM es un componente adicional que traen algunas EUFI para emular una bios tradicional y poder ejecutar imagenes MBR legacy.

Para poder usar UEFI se debe: crear un programa en c, compilarlo con las librerias UEFI que proporcionan los headers con las definiciones de los protocolos y servicios y generar un ejecutable .efi. Luego se coloca ese archivo en la EFI system partition y el firmware lo encuentra y lo ejecuta al arrancar.

Ejemplos de funciones:
- Boot Services: disponibles solo durante el arranque. Incluyen funciones para gestionar memoria, cargar imágenes ejecutables, manejar eventos y timers, y acceder a protocolos de dispositivos.

### ¿Menciona casos de bugs de UEFI que puedan ser explotados?

- Caso LogoFAIL: un bug que podia ser explotado para entregar un payload malicioso y eludir seguridad como Secure Boot, Intel Boot Guard, entre otras. Ademas, estas vulnerabilidades facilitaban la entrega de malware persistente a sistemas comprometidos durante la fase de arranque , al inyectar un archivo de imagen de logo malicioso en la particion del sistema EFI.

### ¿Qué es Converged Security and Management Engine (CSME), the Intel Management Engine BIOS Extension (Intel MEBx).?

CSME

CSME surge en 2017/2028 como renombre de loq ue era ME (Intel Management Engine) un subsistemadesarrollado en 2006. El CSME es un microcontrolador independiente que se encuentra en el chipset y cuenta con microprocesador propio, tiene su propia ram y corre su propio sistema operativo. Funciona completamente independiente de la CPU principal, funciona siempre que la placa madre tenga tension, incluso cuando el SO esta apagado o la maquina en estado de suspension.
Las principales funciones de CSME son:
- Seguridad del firmware: es el primer codigo que se ejecuta cuando se energiza la placa madre, verifica la integridad criptografica de la UEFI
- Gestion remota: permite encender, apagar, reiniciar, acceder a la consola, redirigir el teclado y el video, o reinstalar el SO de forma remota.
- Boot guard: permite "quemar" en fusibles permanentes un hash del firmware legitimo, de modo que si alguien modifica la BIOS, el sistema no arranca.

Intel MEBx

Es la interfaz de configuracion del CSME durante el arranque del sistema, de manera similar  a como la UEFI/BIOS permite configurar parametros del hardware.
Desde el MEBx se puede:
- Habilitar o deshabilitar AMT
- COnfigurar credenciales de acceso remoto
- Configurar la interfaz de red que se usara para la gestion
- Establecer politicas de acceso
- Activar KVM (Keyboard Video Mouse) remoto por hardware

### ¿Qué es coreboot ? ¿Qué productos lo incorporan ?¿Cuales son las ventajas de su utilización?

Coreboot se diferencia de la BIOS/UEFI, ya que en lugar de ser un firmware monolitico que implementa toda una interfaz de compatibilidad con hardware antiguo, coreboot hace lo minimo indispensable en hardware y delega todo lo demas a un payload separado.
Los productos que lo incorporan son:
- Google chromebooks
- System 76: fabricante de laptops y workstations linux
- Purims: fabricante de laptops orientadas a privacidad
- Qemu: firmware de maquinas virtuales

Las ventajas de Coreboot son:
- Velcidad de arranque: Al no cargar decadas de compatibilidad legacy, coreboot puede inicializar el hardware y entregar control al SO en tiempos dramaticamente menores.
- Transparencia y auditabilidad: Es codigo abierto, cualquiera puede aauditar exactamente que hace el firmware.
- Menor superficie de ataque: Al tener lo minimo la superficie de ataque es menor
- Modularidad: La arquitectura payload permite adaptar el firmware
- Independencia del vendedor: Al no depender del codigo del propietario, se puede actualizar el firmaware de equipos que el fabricante ya no soporta.  


### Linker

### ¿Que es un linker? ¿que hace ? 

El linker es una herramienta que toma uno o mas archivos .o y los combina en un unico archivo. Resuelve referencias, cuando el codigo tiene una etiqueta como msg que aputana  un string , el ensamblador no sabe en que direccion de memoria va a quedar ese string. El linker asigna las direcciones definitivas a cada simbolo y parchea todas las intrucciones que los referencian con la direccion correcta.

### ¿Que es la dirección que aparece en el script del linker?¿Porqué es necesaria ?

La línea . = 0x7c00 establece el el contador de posición del linker en la dirección 0x7C00. Esto le dice al linker que el programa va a estar ubicado en esa dirección de memoria cuando se ejecute. Es necesaria porque la BIOS, al encontrar un MBR válido, siempre lo carga en la dirección 0x7C00 y salta ahí. Si el linker no supiera esto, calcularía las direcciones de las etiquetas (como msg) asumiendo que el programa empieza en 0, y todas las referencias a datos serían incorrectas cuando el código se ejecute realmente en 0x7C00.

### Compare la salida de objdump con hd, verifique donde fue colocado el programa dentro de la imagen. 

Salida con hd:
![alt text](img/4.gif)

Salida con objdump:
![alt text](img/5.gif)

El programa ejecutable ocupa los primeros 15 bytes de la imagen (posiciones 0x00 a 0x0E). Son las instrucciones mov, lods, or, je, int, jmp y hlt que conforman el loop de impresión. En hd se ven como bytes hexadecimales (be 0f 7c b4 0e ac 08 c0 74 04 cd 10 eb f7 f4), y en objdump se ven como instrucciones desensambladas.

### Grabar la imagen en un pendrive y probarla en una pc y subir una foto 

![alt text](img/6.gif)

### ¿Para que se utiliza la opción --oformat binary en el linker?

Le dice al linker que genere un archivo binario plano (raw binary), sin ningún header ni metadata, solo los bytes del código y datos tal cual deben aparecer en memoria.


### Modo protegido

Para pasar de Modo Real (16 bits) a Modo Protegido (32 bits), es necesario deshabilitar las interrupciones, cargar una Tabla Global de Descriptores (GDT) en memoria para configurar la MMU del hardware, cambiar el bit 0 del registro de control `CR0` y limpiar el pipeline del procesador mediante un salto largo (*far jump*).

#### 1. Código Assembler: GDT con dos descriptores y Segmento Read-Only

A continuación se detalla cómo configurar la GDT para tener un segmento de código y un segmento de datos diferenciado y de solo lectura.

```assembly
.code16
.global _start

_start:
    cli                     # Deshabilitar interrupciones por hardware
    lgdt gdtr               # Cargar el puntero de nuestra GDT en el procesador

    # Encender el Modo Protegido (Setear el bit 0 del registro CR0)
    mov %cr0, %eax
    or $1, %eax
    mov %eax, %cr0

    # Salto largo (Far Jump) para limpiar el pipeline y aplicar el nuevo CS
    # 0x08 es el índice que apunta al Descriptor de Código en la GDT
    jmp $0x08, $modo_protegido

.code32
modo_protegido:
    # 0x10 es el índice que apunta al Descriptor de Datos en la GDT
    mov $0x10, %ax
    mov %ax, %ds
    
    # INTENTO DE ESCRITURA EN SEGMENTO READ-ONLY
    # Esto provocará un fallo de hardware.
    movl $0xDEADBEEF, (0x1000) 

    hlt

# --- TABLA GDT ---
.align 4
gdt_start:
null_descriptor:
    .quad 0                 # El offset 0x00 siempre debe ser nulo por arquitectura

code_descriptor:            # Offset 0x08
    .word 0xffff            # Límite (bits 0-15)
    .word 0x0000            # Base física (arranca en 0x0)
    .byte 0x00              
    .byte 0b10011010        # Access Byte: Presente, Ejecutable, Lectura permitida.
    .byte 0b11001111        
    .byte 0x00              

data_descriptor:            # Offset 0x10
    .word 0xffff            # Límite
    .word 0x1000            # Base física DIFERENTE (arranca en 0x1000)
    .byte 0x00              
    .byte 0b10010000        # Access Byte: READ-ONLY (El bit de Writable está en 0)
    .byte 0b11001111        
    .byte 0x00              
gdt_end:

gdtr:
    .word gdt_end - gdt_start - 1 # Tamaño de la tabla
    .long gdt_start               # Puntero a la tabla
```

#### 2. ¿Cómo sería un programa que tenga dos descriptores de memoria diferentes?
Para que los descriptores apunten a bloques de memoria lógicamente separados, se debe modificar la dirección **Base física** dentro de la estructura de la GDT. En el código proporcionado, el `code_descriptor` inicia su bloque en la dirección física `0x0000`, mientras que el `data_descriptor` establece su base desplazada en la dirección `0x1000`. De esta manera, el hardware (a través de la MMU) aísla completamente la memoria de programa de la memoria de datos.

#### 3. Intento de escritura en un segmento de Solo Lectura (Read-Only)
Para crear un segmento de solo lectura, se configuró el *Access Byte* del descriptor de datos en la GDT, forzando el bit *Writable* (modificable) a `0`. 

**¿Qué sucede al ejecutar `movl $0xDEADBEEF, (0x1000)`?**
La MMU (Memory Management Unit) intercepta la instrucción antes de que las señales eléctricas lleguen a la memoria RAM. Al leer la configuración de la GDT, el procesador detecta que el segmento carece de permisos de escritura y dispara una interrupción por hardware conocida como **General Protection Fault (Excepción #13)**. 

Al no haber configurado previamente un vector de interrupciones (IDT) para atajar y manejar esta excepción, la CPU sufre un *Double Fault*, seguido inmediatamente de un *Triple Fault*. A nivel arquitectónico, un *Triple Fault* activa el pin de reset del procesador, provocando que la máquina (o el emulador QEMU) aborte la ejecución y entre en un bucle infinito de reinicios.

#### 4. En modo protegido, ¿Con qué valor se cargan los registros de segmento? ¿Por qué?
A diferencia del Modo Real donde los registros de segmento guardaban direcciones físicas de memoria directas (ej. `0x07C0`), en Modo Protegido registros como `%cs`, `%ds` o `%es` se cargan con **Selectores de Segmento**.

Un selector es un valor de 16 bits que funciona como un **índice** apuntando a una fila específica de la GDT. Por ejemplo, al cargar el registro de datos `%ds` con el valor `0x10`, no se le está indicando a la CPU una dirección RAM, sino que se le instruye que aplique las reglas de seguridad, límites y offset físico definidas en el tercer descriptor de la tabla GDT.

### Conclusión

Este trabajo práctico permitió comprender la evolución y el funcionamiento del proceso de arranque de una computadora desde su nivel más bajo. A través de la investigación y la experimentación práctica, logramos:
* Entender la transición histórica y técnica desde el antiguo BIOS/MBR hacia las implementaciones modernas con UEFI y Coreboot.
* Identificar el rol crítico del linker en la asignación de direcciones de memoria físicas (como el clásico `0x7C00`).
* Desmitificar el paso de Modo Real a Modo Protegido, comprobando cómo el procesador delega la seguridad y la segmentación de la memoria al hardware (MMU) a través de la configuración de la GDT y los selectores de segmento.

En resumen, el trabajo demuestra cómo las abstracciones de software se apoyan fundamentalmente en la configuración estricta de los transistores y registros del microprocesador.

### Bibliografia
- https://www.lenovo.com/ar/es/glosario/uefi/?orgRef=https%253A%252F%252Fwww.google.com%252F&srsltid=AfmBOoqRwmyjiC2P8mG_-BWqRwpSsGSIz4byrFluFUqVfA7tWc6FsPN8
- https://unaaldia.hispasec.com/2023/12/vulnerabilidades-criticas-en-uefi-logofail-expone-a-dispositivos-x86-y-arm.html
