---
layout: post
title: The Kria KV260 Starter Kit for Total MPSoC Noobs
date:  2021-07-11 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Introduction

Cheap, large, fast. 

Without reverse engineering old production FPGA boards from eBay, there has never
been an FPGA development platform that ticks these 3 boxes. One of the best deals in town
is the [$37 Arrow DECA FPGA board](/2021/04/23/Arrow-DECA-FPGA-board.html). For as long
as stock remains, it is dirt cheap, and it has enough FPGA resources to satisfy most hobby projects, but 
speed has never been the strong point of MAX10 FPGAs.

The DE10-Nano has much better credentials: $170 is still an acceptable price point. It has more
than double the FPGA resources of the DECA, a Cyclone V is quite a bit faster too. An extra
bonus is the fact that it's an SOC with an ARM Cortex-A9 CPU. The DE10-Nano is very popular because
it's the basis of the Mister FPGA Retro Gaming platform.

And for the longest time, that's about where things ended for the ambitious hobbyist.

That is... until a couple of months ago, when Xilinx introduced the 
[Kria KV260 Vision AI Starter Kit](https://www.xilinx.com/products/som/kria/kv260-vision-starter-kit.html).
The KV260 is not intended to be a generic FPGA platform: it's Xilinx' attempt to make a dent in
machine learning market. The core product is a System-on-Module (SOM), a small PCB with an FPGA, DRAM, 
some flash storage, power regulation and connectors to plug the board into a solution specific board.
The KV260 is the combination of a SOM and a solution board that's targeted towards vision
applications. There are a number of image capture interfaces, as well as a bunch of generic IO 
ports: 4 USB 3.0 ports, Gigabit Ethernet, HDMI or DisplayPort output.

The Kria KV260 is being brought to market in a very similar way as the [Nvidia's Jetson Nano](https://developer.nvidia.com/embedded/jetson-nano-developer-kit):
for both, the price of the plug-in module/SOM alone is higher than the price of the development kit
and the plug-in module combined! And what an attractive price it is: $199 will get you a development system
with an FPGA from the Zynq MPSoC family that has roughly twice the logic resources of the DE10-Nano, and an SOC system with 4
fast ARM Cortex A53 application CPUs, 2 Cortex R5F real-time CPUs, a Mali GPU, 1MB of L2 cache, and 256KB of 
tightly coupled memory (TCM).

Everything about the KV260 documentation is geared towards machine learning. The documentation doesn't 
even hint at using it for traditional FPGA usage, but that doesn't mean it's not possible. 

Let's be honest, for machine learning, you're much better off using Nvidia solution. (Disclaimer: 
Nvidia is my employer.) So why don't we look at the KV260 as a regular FPGA development 
platform, not the machine learning engine that Xilinx wants it to be? 

In this blog post, I will try to do exactly that. 

Everything you'll find below has been written from the perspective of somebody who's intimately familiar 
with Intel FPGAs and Quartus, Intel's FPGA design tool, but no prior knowledge of Xilinx MPSoC FPGAs or 
Vivado/Vitis, the Xilinx's FPGA tools. 

# The KV260 in Closeup

It's probably not a bad idea to first go into details about the KV260 offers... and what it doesn't.

The Xilinx Kria product page currently shows 3 products: the KV260 Starter Kit ($199), and the K26c ($250) and K26i ($350)
SOMs. The 2 SOMs only different in their supported temperature range. One could easily be assume that the
KV260 contains a K26c SOM (I definitely did!) but that's it not the case. 

The SOM on the KV260 lacks a few features:

* no 16GB eMMC

    While the KV260 has a 512Mbit configuration QSPI flash, it requires a user supplied SDcard
    as secondary boot memory to store the main OS.

* Only 1 240-pin IO connector

    The second 240 SOM connector on the K26 board supports 132 GPIOs and 4 high-speed links. The KV260
    SOM has to make do with a much lower number. 

When considered as an integral part of the overall system, these limitation don't matter in practice, since
there's an alternative to the lack of storage flash, and because the number of IO pins on the SOM is 
sufficient to service all the functional blocks on the carrier card. Just don't buy the KV260 with the
goal of removing the SOM and using it as a cheap KV26c/i alternative.

# The FPGA Itself

Xilinx created a dedicated FPGA SKU for this KV260 and K26 SOMs, but the specifications exactly 
match the ones of the Zynq ZU5EV.


| FPGA                   | XCK26-SFVC784 |
|------------------------|:-------------:|
| Application CPUs       | 4x Cortex-A53 |
| L2 Cache (MByte)       |       1       |
| Real-Time CPUs         | 2x Cortex-R5F |
| TCM (KByte)            |     2x 128    |
| GPU                    |  Mali-400 MP2 |
| Logic Cells            |    256,200    |
| CLB Flip-Flops         |    234,240    |
| CLB LUTs               |    117,120    |
| Distributed RAM (Mbit) |      3.5      |
| Block RAM blocks       |      144      |
| Block RAM (Mbit)       |      5.1      |
| UltraRAM blocks        |       64      |
| UltraRAM (Mbit)        |      18.0     |
| DSP slices             |      1248     |
| Video Codec            |       1       |

# General MPSoC Boot Procedure

Getting an MPSoC up and running is no laughing matter. Yes, just like regular FPGAs, there's QSPI flash on the module
to configure the system, but this flash is used to bring up the SOC. It's then up to the software of the SOC to load
the bitstream in the PL. *Unlike regular FPGAs, there is no automatic way in which the PL becomes master of the
QSPI and sucks in the bitstream.*

Booting the MPSoC is a complex, multi-stage process that starts with a fixed boot ROM inside the chip itself.

# K26/KV260 MPSoC Boot Procedure

For the K26 or KV260 products, Xilinx decided to lock things down a bit to prevent customers
from shooting themselves in the foot. That's not a bad thing: 

Reading the QSPI information:

* Boot without SDcard inserted.
* Check that QSPI reading is fine

    ```
sf probe
SF: Detected n25q512a with page size 256 Bytes, erase size 64 KiB, total 64 MiB
    ```

* Read data from QSPI address 0x2240000 and copy it to address 0x08000000 in RAM

    ```
sf read 0x08000000 0x2240000 32
SF: 50 bytes @ 0x2240000 Read: OK
    ```

* Dump the data that was copied to address 0x08000000

    ```
md 0x08000000
08000000: 696c6958 6f53786e 73515f6d 6d496970    XilinxSom_QspiIm
08000010: 5f656761 312e3176 3230325f 32343031    age_v1.1_2021042
08000020: 00000a32 00000000 00000000 00000000    2...............
08000030: f3930000 fffab9b6 ef1fcefe da3fffee    ..............?.
    ```

    According to the [Xilinx KV260 Wiki](https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/1641152513/Kria+K26+SOM#Boot-FW-HW-Details), 
    address 0x2240000 contains QSPI Image Information. It's a read-only QSPI sector, so there's
    nothing here for us to change.


# Boot Image Recovery

* [Board Reset, Firmware Update, and Recovery](https://www.xilinx.com/support/documentation/user_guides/som/1_0/ug1089-kv260-starter-kit.pdf#_OPENTOPIC_TOC_PROCESSING_d114e2663)

   Update BOOT.BIN either from Linux (when the QSPI BOOT.BIN allows it) or with the Ethernet Recovery Tool.


* On Ubuntu 20.4: Works with Chrome only! Firefix gives the following error:
   
   ```
Making the boot img A non-bootable
Initiating img A upload
Size of Image to be downloaded = 1409400
Erasing img
Erasing complete
Starting image update
Validating CRC
ERROR: Crc mismatch
Flash Img CRC = 00000000, Sender Crc = B14C3A9B
    ```

* Restoring "KV260 2020.2.2 Boot FW Update - Early Launch":

    ```
Making the boot img A non-bootable
Initiating img A upload
Erasing img
Erasing complete
Size of Image to be downloaded = 1409400
Validating CRC
CRC matches
Flash Img CRC = B14C3A9B, Sender Crc = B14C3A9B
Making the boot image A requested image
    ```

* Restoring "KV260 2020.2.2 Boot FW Update - 2020.2.2":

    ```
Making the boot img A non-bootable
Initiating img A upload
Erasing img
Erasing complete
Size of Image to be downloaded = 1409400
Validating CRC
CRC matches
Flash Img CRC = A7CED268, Sender Crc = A7CED268
Making the boot image A requested image
Download Complete....
    ```

* Recovery mode UART log: 

   ```
Release 2020.2   Apr 22 2021  -  17:48:34
MultiBootOffset: 0x3C0
Reset Mode      :       System Reset
Platform: Silicon (4.0), Running on A53-0 (64-bit) Processor, Device Name: XCZUUNKNEG
QSPI 32 bit Boot Mode
FlashID=0x20 0xBB 0x20
PMU-FW is not running, certain applications may not be supported.
Protection configuration applied
Exit from FSBL
[Flash Image Info]
         Flash size : 64MB
        Sector size : 64KB
        PageSize in bytes: 0x00000100

[Boot Image Info]
                         Ver: 1
                      Length: 4
                    Checksum: 0xAEB2BDB9
        Persistent State Reg: 0x01000000
                Img A Offset: 0x00200000
                Img B Offset: 0x00F80000
         Recovery Img Offset: 01E00000

Start PHY autonegotiation
Waiting for PHY to complete autonegotiation.
autonegotiation complete
link speed for phy address 1: 1000
Configuring default IP 192.168.0.111

-[Network Interface]------------------------
        Board IP: 192.168.0.111
        Netmask : 255.255.255.0
        Gateway : 192.168.0.1

Xilinx boot image recovery tool web server is running on port 80
Please point your web browser to http://192.168.0.111
    ```

* Erase Boot A:

    ```
ZynqMP> sf erase 0x200000 0x10000
SF: 65536 bytes @ 0x200000 Erased: OK
    ```


# Flashing QSPI from Vitis

```

program_flash -f \
/home/tom/projects/kv260_sw_test/vitis_workspace/hello_world_system/Debug/sd_card/BOOT.BIN \
-offset 0 -flash_type qspi-x4-single -fsbl \
/home/tom/projects/kv260_sw_test/vitis_workspace/kv260_sw_platform/export/kv260_sw_platform/sw/kv260_sw_platform/boot/fsbl.elf \
-cable type xilinx_tcf url TCP:127.0.0.1:3121 

****** Xilinx Program Flash
****** Program Flash v2021.1 (64-bit)
  **** SW Build 3246112 on 2021-06-09-14:19:56
    ** Copyright 1986-2020 Xilinx, Inc. All Rights Reserved.


Connected to hw_server @ TCP:127.0.0.1:3121

Retrieving Flash info...

Initialization done
Using default mini u-boot image file - /home/tom/tools/Xilinx/Vitis/2021.1/data/xicom/cfgmem/uboot/zynqmp_qspi_x4_single.bin
===== mrd->addr=0xFF5E0204, data=0x00000222 =====
BOOT_MODE REG = 0x0222
WARNING: [Xicom 50-100] The current boot mode is QSPI32.
Flash programming is not supported with the selected boot mode.If flash programming fails, configure device for JTAG boot mode and try again.
Downloading FSBL...
Running FSBL...
Finished running FSBL.
Xilinx Zynq MP First Stage Boot Loader 

Release 2021.1   Jul 14 2021  -  03:36:32
PMU-FW is not running, certain applications may not be supported.



U-Boot 2021.01-08077-gfb43236 (May 17 2021 - 10:24:23 -0600)

Model: ZynqMP MINI QSPI SINGLE
Board: Xilinx ZynqMP
DRAM:  WARNING: Initializing TCM overwrites TCM content
256 KiB
EL Level:	EL3
Multiboot:	64
In:    dcc
Out:   dcc
Err:   dcc
ZynqMP> sf probe 0 0 0

SF: Detected n25q512a with page size 256 Bytes, erase size 64 KiB, total 64 MiB
ZynqMP> Sector size = 65536.
f probe 0 0 0

Performing Erase Operation...
sf erase 0 30000

jedec_spi_nor flash@0: Erase operation failed.
jedec_spi_nor flash@0: Attempted to modify a protected sector.
SF: 196608 bytes @ 0x0 Erased: ERROR
ZynqMP> f erase 0 30000

Erase Operation failed.
INFO: [Xicom 50-44] Elapsed time = 0 sec.

ERROR: Flash Operation Failed
```

# The Zynq FPGA Mental Model 

All FPGAs of the Zynq product line have 2 major functional blocks: 
the processing system (PS) and the programmable logic (PL). The PS contains the SOC part:
fixed logic such as CPUs, caches, GPU, major IO blocks etc. The PL contains what
you'd find in a traditional FPGA.

While there are interfaces, AXI buses primarily, that form a bridge the PS and the PL domain, 
it is extremely important keep in mind that the PS and the PL part are in essence 2 completely
different systems. You could design the bitstream of the PL without major knowledge of the PS,
and vice versa. 

A bitstream can be loaded into the PL by some kind of software running on the PS, or you
do so through the JTAG port just like you'd do with a regular FPGA. The software on the PS could 
be a relatively simple baremetal piece of code, or a full featured Linux-based operation system 
complete with GUI and all. 

While the PL can be informed about some aspects in which the PS has been configured, such 
which clocks have been configured or which interfaces are active, the PS is master of its
own domain and software on the PS can reprogram these aspects at will.

# IOs 


# Vivado Installation

* Download installer: `Xilinx_Unified_2021.1_0610_2318_Lin64.bin`
* Run installer and then download a local network drive image

    This makes it easier to install on multiple PCs later...

* For Ubuntu 2.04, before running `./xsetup`, first do the following:

    `sudo ln -s /lib/x86_64-linux-gnu/libtinfo.so.6  /lib/x86_64-linux-gnu/libtinfo.so.5` 

    If you don't do this, the installer will fail at a later stage.

* run `./xsetup`
* Install Vitis: this includes Vivado!
* Install PetaLinux

# KV260

* [Official Documentation](https://www.xilinx.com/products/som/kria/kv260-vision-starter-kit.html#documentation)
* [Motherboard Schematic](https://www.xilinx.com/member/forms/download/design-license.html?cid=3eb7e365-5378-461f-b8b0-bb3dad84eb4e&filename=xtp682-kria-k26-carrier-card-schematic.zip)
* [Kria K26 SOM Wiki](https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/1641152513/Kria+K26+SOM)

* [Kria SOM Carrier Card - Design Guide](https://www.xilinx.com/support/documentation/user_guides/som/ug1091-carrier-card-design.pdf)
	
	* How to design a board that uses a Kria SOM.
	* Figure 1 is important because it shows which SOM pins are going where.

* [Kria K26 SOM Data Sheet](https://www.xilinx.com/support/documentation/data_sheets/ds987-k26-som.pdf)

	* Quite a bit of overlap with the SOM Carrier Card Design Guide.

* [Kria KV260 Vision AI Starter Kit DataSheet](https://www.xilinx.com/support/documentation/data_sheets/ds986-kv260-starter-kit.pdf)

	*  Low of useful info.

* [Kria KV260 Vision AI Starter Kit User Guide](https://www.xilinx.com/support/documentation/user_guides/som/1_0/ug1089-kv260-starter-kit.pdf)

	* Describes connectors, boot devices and firmware, getting started info, tools integration overview, board reset and firmware update/recovery.
	

* Download petalinux image from [this getting started link](https://www.xilinx.com/products/som/kria/kv260-vision-starter-kit/kv260-getting-started/setting-up-the-sd-card-image.html), 
  not from [this one](https://xilinx.github.io/kria-apps-docs/docs/smartcamera/smartcamera_landing.html).
* Once the initial getting started is up and running, then use the command line options of the github smartcamera page.
	* E.g. try with different resolution, try with rtsp -> VLC


* [KV260 Vitis - Design Examples Repo](https://github.com/Xilinx/kv260-vitis)

	* [Board Files](https://github.com/Xilinx/kv260-vitis/tree/release-2020.2.2_k26/platforms/vivado/board_files)

# SOM240 pinout to Start Kit

* Based on schematic, board files, and project xdc

	* [kv260_ispMipiRx_vcu_DP](https://github.com/Xilinx/kv260-vitis/blob/release-2020.2.2_k26/platforms/vivado/kv260_ispMipiRx_vcu_DP/xdc/pin.xdc)



* IAS0 connector: OnSemi image access system (IAS) camera module interfacesupporting four MIPI lanes. 
  Connects to OnSemi AP1302 ISP device sensor 0 interface.
* IAS1 connector: OnSemi IAS camera module interface supporting four MIPI lanes.
* JTAG: when FTDI chip has `LS_OE_B` pin asserted then JTAG pins are driven. Otherwise, the JTAG connector can take over.


# Tutorial

* [Xilinx ZCU102 Tutorial](https://xilinx.github.io/Embedded-Design-Tutorials/master/docs/Introduction/ZynqMPSoC-EDT/README.html)

* [Zynq UltraScale+ Device - Technical Reference Manual](https://www.xilinx.com/support/documentation/user_guides/ug1085-zynq-ultrascale-trm.pdf)

    Required reading for better general understanding of how IOs are mapped etc.
