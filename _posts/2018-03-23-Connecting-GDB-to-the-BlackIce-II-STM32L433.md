---
layout: post
title:  Connecting GDB to the BlackIce-II STM32L433 with the Black Magic Probe
date:   2018-03-23 00:00:00 -1000
categories: 
---

* TOC
{:toc}

In [yesterday's log](/2018/03/22/stlink-blue-pill-stm32l4xx-debug.html), I wrote about not being able to 
connect the STLink v2 to the STM32 of the BlackIce-II board. 

Right now, that still doesn't work, but I found a work-around: I installed the wonderful 
[Black Magic Probe firmware](https://github.com/blacksphere/blackmagic) on the Blue Pill STM32F103 board, 
which converts the Blue Pill into a debugging dongle that's actually more powerful than the STLink v2!

An STLink v2 is essentially a protocol converter from USB to SWD. You still need OpenOCD as an intermediary 
GDB server to link GDB to your STM32.

Not so with the Black Magic Probe: it acts like a serial port on the USB side and has a GDB server built-in which drives 
a SWD or JTAG interface. OpenOCD is not needed anymore: you connect GDB straight to the dongle!

How did I get there?

# Install Black Magic Probe on the Blue Pill

This turned out to be a combination of 
[this article: "Converting an STM32F103 board to a Black Magic Probe"](https://medium.com/@paramaggarwal/converting-an-stm32f103-board-to-a-black-magic-probe-c013cf2cc38c)
and [this article: "Programming an STM32F103XXX with a generic "ST Link V2" programmer from Linux"](https://github.com/rogerclarkmelbourne/Arduino_STM32/wiki/Programming-an-STM32F103XXX-with-a-generic-%22ST-Link-V2%22-programmer-from-Linux) 
(which I already reference earlier.)

The first article assumes that you don't have an STLink v2 dongle and compiles then installs the Black Magic firmware 
using a USB to Serial dongle instead. The second one tells you how to install anything with the STLink dongle.

I wanted to use the STLink dongle to install the Black Magic firmware.

All in all, the procedure was pretty straightforward.

* Compile the Black Magic firmware until you have `blackmagic_dfu.bin` and `blackmagic.bin`
    * Download Black Magic from [GitHub](https://github.com/blacksphere/blackmagic)
    * Run:

    ```
make
cd src
make clean && make PROBE_HOST=stlink
    ```

* Install `blackmagic_dfu.bin` with the STLink dongle

    Steps:

    ```
openocd -f /usr/local/share/openocd/scripts/interface/stlink-v2.cfg -f /usr/local/share/openocd/scripts/target/stm32f1x.cfg
telnet localhost 4444
reset halt       <<< in combination with pressing the Blue Pill reset button!
flash write_image erase blackmagic_dfu.bin 0x08000000
    ```

    Once installed, the Blue Pill device is now DFU capable. This means that new firmware can be installed 
    over USB. You do not need the STLink dongle anymore to install additional firmware! 

* Install `blackmagic.bin` (without STLink)

    `dfu-util -d 1d50:6018,:6017 -s 0x08002000:leave -D blackmagic.bin`

In the process of all this, I learned a little bit about this all works:

* The STM32F1 starts executing at address 0x08000000. 

    This is why earlier the `blackmagic_dfu.bin` firmware was flashed to that address.

* The `blackmagic_dfu.bin` has two features:
    * It tests if there is valid firmware at 0x08002000. 
    * If there is, it jumps to that address and its job is done. You can see that piece of code 
      [here](https://github.com/blacksphere/blackmagic/blob/a9219c3616858149fdc252a3fef52c42252a66c9/src/platforms/stlink/usbdfu.c#L65).
    * When there isn't any valid code, then it sets itself up as a [USB DFU](http://wiki.openmoko.org/wiki/USB_DFU_-_The_USB_Device_Firmware_Upgrade_standard) 
      device, making it possible to flash valid firmware. You can see this just 
      [a few lines](https://github.com/blacksphere/blackmagic/blob/a9219c3616858149fdc252a3fef52c42252a66c9/src/platforms/stlink/usbdfu.c#L78) 
      further down.

* Consequently, `blackmagic.bin` is located at address 0x08002000. Since it completely takes 
  over the board, this one also needs to implement DFU mode, otherwise you'd still need an additional 
  dongle (like the original STLink) to install improved Black Magic firmware later on!

* The Black Magic firmware implements 
  [3 'functionalities'](https://github.com/blacksphere/blackmagic/blob/a9219c3616858149fdc252a3fef52c42252a66c9/src/platforms/common/cdcacm.c#L350-L374) 
  on a single USB device:
    * DFU
    * a GDB server (which uses a USB-to-Serial port)

        This ultimately controls SWD and JTAG pins on your Blue Pill

    * UART (also using USB-to-Serial port)

        This controls UART pins on the Blue Pill.

* Instead of using the standard STM32 libraries, Black Magic uses [libopencm3](https://github.com/libopencm3/libopencm3), 
  which is an open-source equivalent that can be used to many different Cortex devices from other 
  chip companies.

# Connecting the Black Magic to the BlackIce-II

I wired the following signals:

* Blue Pill GND -> GND (pin 9 of the BlackIce-II RPi connector)
* Blue Pill SWDIO (pin PB14) -> SWDIO (pin 11 of the BlackIce-II RPi connector)
* Blue Pill SWCLK (pin PA5) -> SWCLK (pin 7 of the BlackIce-II RPi connector)

Once you have Black Magic Probe running on the Blue Pill, you can connect to it directly with gdb:

* `arm-none-eabi-gdb -ex "target extended-remote /dev/ttyACM0"`

    On my Linux machine, the Black Magic Probe created `/dev/ttyACM0` (GDB) and `/dev/ttyACM1` (UART). 

    If you do `ls /dev/serial/by-id`, you can see more descriptive names to connect to.

    You should see "Remove debugging using \<some interface\>:

    ```
    ubuntu@ubuntu-xenial:~/projects/BlackIce-II/firmware/iceboot$ arm-none-eabi-gdb  -ex "target extended-remote /dev/ttyACM0"
    GNU gdb (GNU Tools for Arm Embedded Processors 7-2017-q4-major) 8.0.50.20171128-git
    Copyright (C) 2017 Free Software Foundation, Inc.
    License GPLv3+: GNU GPL version 3 or later 
    This is free software: you are free to change and redistribute it.
    There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
    and "show warranty" for details.
    This GDB was configured as "--host=x86_64-linux-gnu --target=arm-none-eabi".
    Type "show configuration" for configuration details.
    For bug reporting instructions, please see:
    .
    Find the GDB manual and other documentation resources online at:
    .
    For help, type "help".
    Type "apropos word" to search for commands related to "word".
    Remote debugging using /dev/ttyACM0
    (gdb)
    ```

* You now need to scan for STM32 devices:

    `monitor swdp_scan`

    Note that this didn't work at first. Initially, I saw the following:

    ```
    (gdb) monitor swdp_scan
    Target voltage: unknown
    SW-DP scan failed!
    ```

    It took me a long to time figure what was wrong. In the end, I solved it by wiring an additional 
    GND wire between the Blue Pill board and the BlackIce-II board. So simple!

    ```
    (gdb) monitor swdp_scan
    Target voltage: unknown
    Available Targets:
    No. Att Driver
     1      STM32L4xx
    ```

    Hurray!

* Next, you need to tell GDB to connect to this device:

    `attach 1`:

    ```
    (gdb) attach 1
    Attaching to Remote target
    warning: No executable has been specified and target does not support
    determining executable automatically.  Try using the "file" command.
    0x080008e2 in ?? ()
    ```

    What happened now is that GDB has taken control of the ARM CPU. Whatever it was 
    executing has been stopped now and that is that.

    If you never replaced the firmware of the BlackIce-II STM32 controller, you interrupted the `iceboat`
    firmware, which allows one to download a new FPGA bitstream over the USB-to-Serial port.

# Debugging Firmware on the BlackIce-II STM32

For now, let's just use an example of the existing firmware.

* Recompile the iceboat firmware as described in my wiki page here.
* You will now have a file called `iceboot.elf` in the `./output` directory
* While in the `./firmware/iceboot` directory, attach gdb to the STM32 CPU as described earlier.
* **Press the reset button of the BlackIce-II board!**
    * This resets the CPU back to its starting position. But since GDB is attached now, it will stay there.
* Load the recompiled firmware:

    `file ./output/iceboot.elf`
* Set a breakpoint at the start of the C program

    `br main`

* Start executing

    `r`

If all goes well, the GDB will now be waiting at the first command of main.

It looks like this on my console:

```
Remote debugging using /dev/ttyACM0
(gdb) atta 1
Attaching to Remote target
warning: No executable has been specified and target does not support
determining executable automatically.  Try using the "file" command.
0x080011d6 in ?? ()
(gdb) file ./output/iceboot.elf
A program is being debugged already.
Are you sure you want to change the file? (y or n) y
Reading symbols from ./output/iceboot.elf...done.
(gdb) br main
Breakpoint 1 at 0x80012b4: file main.c, line 95.
(gdb) r
The program being debugged has been started already.
Start it from the beginning? (y or n) y
Starting program: /home/ubuntu/projects/BlackIce-II/firmware/iceboot/output/iceboot.elf
Note: automatically using hardware breakpoints for read-only addresses.

Breakpoint 1, main () at main.c:95
95      HAL_Init();
(gdb)
```

Success!
