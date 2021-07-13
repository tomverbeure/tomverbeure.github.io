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
