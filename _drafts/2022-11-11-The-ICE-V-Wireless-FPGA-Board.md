---
layout: post
title: A Quick Look at the ICE-V Wireless FPGA Development Board
date:  2022-11-11 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

It's been more than 7 years now since the first public release of 
[Project IceStorm](http://bygone.clairexen.net/icestorm/).  Its goal was to reverse engineer to the internals
of Lattice ICE40 FPGA, and create all fully open source toolchain to go from RTL all the way
to place-and-routed bitstream.  Project IceStorm was a huge success and it kicked off a small
revolution in the world of hobby electronics. While it had been possible to design for FPGAs before,
it required multi-GB behemoth software installatations, and there weren't a lot of cheap development
boards.

Project IceStorm kicked off industry of small scale makers who created their own development board, each
with a distinct set of features. One crowd favorite has been the 
[TinyFPGA BX](https://www.crowdsupply.com/tinyfpga/tinyfpga-ax-bx), which is still available for
$38, one of the lowest prices to get your hands dirty with an FPGA that has a capacity that will
exceed the needs of most users.

The BX board is very bare bones: it's on BYOP, bring your own peripherals, and there's not even a PMOD 
connector for quick experimentation with external modules. That's great if you're working on a custom 
build with size constraints, but often you want to have something a bit more features.

The ICE-V Wireless is a relatively new entrant in this market. Developed by 
[Querty Embedded Design](http://www.qwertyembedded.com/), it's available at 
[GroupGets.com](https://store.groupgets.com/products/ice-v-wireless) for $99. I ran into 
its creator at the 2022 Hackaday Supercon, and he gave me a board for review.

![ICV-V Wireless board - front view](/assets/icev/ice-v_front.jpg)
*(Photo from ICE-V Wireless github page)*

Let's check it out!

# The ICE-V Wireless FPGA Board

The [ICE-V Wireless GitHub project](https://github.com/ICE-V-Wireless/ICE-V-Wireless) has schematics
and PCB layout available in KiCAD 6.0 format, but I always find a 
[PDF version of the schematic](/assets/icev/esp32c3_fpga.pdf) convenient. The schematic
is straightforward. 

Let's check out the different components:

* ESP32-C3-MINI-1 module ([datasheet](/assets/icev/esp32-c3-mini-1_datasheet_en.pdf))

    An excellent member of well-known Espressif portfolio. It includes:

    * support for 2.4 Wifi (802.11 b/g/n) and Bluetooth 5
    * a RISC-V CPU
    * 4MB flash
    * on-board PCB antenna

* ICE5LP4K-SG48 from the [Lattice iCE40 Ultra family](https://www.latticesemi.com/Products/FPGAandCPLD/iCE40Ultra)

    This FPGA is less commonly used than ICE40-UP5K FPGA, but still has a respectable number of 
    features:

    * 3520 LUTs
    * 80 kbits of block RAM
    * 4 DSPs
    * 2 I2C and SPI cores

    One of the most attractive features of iCE40 Ultra family is their ultra-low static power: just 71 uA
    for this version. This makes the FPGA particularly well-suited for battery operated use cases.

    One feature lacking from this FPGA compared to the more popular iCE40UP5K is the lack of a large slab
    of SRAM. Fear not, however, because the board also has:

* LY68L6400, a SPI/QPI serial pseudo-SRAM with a whopping 64M bits of RAM ([datasheet](/assets/icev/LY68L6400-0.4.pdf))

    The RAM is connected directly to the FPGA. It has a clock rate of 100MHz. In QPI mode, a peak transfer rate
    of 4MB/s should be sufficient for many applications. 

* 3 PMOD ports

    These are your standard double-row configuation PMOD connectors with 8 GPIOs per port, all of which are
    controlled by the FPGA. Unusual is that the power of each PMOD can be individually selected to be
    either the 3v3 rail from the on-board power regulator, or the 4v/5v rail coming from USB (when plugged in)
    or LiPo battery (when present.)

    A nice touch is that the PCB silk screen shows the FPGA pin number of each PMOD IO pin, as well as the
    polarity of differential FPGA IO pairs.

    ![PMOF FPGA pin numbering](/assets/icev/pmod_fpga_pin_numbers.png)

* Auxiliary GPIO connector

    The 8 remaining GPIOs of the FPGA and the ESP32 are routed to a 12-pin connector that can optionally
    be populated with a pin header. Reset, power and ground are also avaiable.

* Standard LiPo battery JST connector with charging logic

    It's always nice to have a charge management controller on board. This one uses a 
    [Microchip MCP73831 ](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf).

* XC6222B331MR-G 3v3 LDO Power Regulator ([datasheet](https://www.digikey.com/en/products/detail/torex-semiconductor-ltd/XC6222B331MR-G/2138187))

    This jelly bean component normally doesn't deserve special mention, but since it also
    drives the PMOD power pins, it's worth pointing out that it has a maximum output current of 700mA.

* USB-C Device Port

    The USD-C port can be used to power the whole board. It also connects to the USB port of othe ESP32 module,
    where it can either act as serial port or a JTAG controller.

* Various smaller components 

    * reset and boot buttons. The boot button can be used as general purpose button for the ESP32.
    * RGB LED connected to the FPGA.
    * various status LEDs
    * 12MHz oscillator

# Feature Discussion


# Development Package


# References

* [ICE-V Wireless Zephyr Support](https://docs.zephyrproject.org/latest/boards/riscv/icev_wireless/doc/index.html)
