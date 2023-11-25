---
layout: post
title: Colorlight 5A-75B
date:   2023-10-15 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

# OpenOCD

```sh
openocd \
    -f /usr/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg \
    -c "adapter_khz 1000; transport select jtag" \
    -c "jtag newtap test tap -irlen 8 -expected-id 0x41111043"
```

# openFPGALoader

Check if a USB-JTAG cable is detected:

```sh
tom@zen:~$ openFPGALoader --scan-usb
```

```
found 15 USB device
Bus device vid:pid       probe type      manufacturer serial               product
001 026    0x0403:0x6014 ft232H          Digilent     210251A08870         Digilent USB Device
```

Scan the JTAG chain for devices:

```sh
tom@zen:~$ openFPGALoader  -d /dev/ttyUSB0 --detect
```
```sh
tom@zen:~$ openFPGALoader --vid 0x0403 --pid 0x6014 --detect
```

```
Jtag frequency : requested 6.00MHz   -> real 6.00MHz  
index 0:
	idcode 0x1111043
	manufacturer lattice
	family ECP5
	model  LFE5UM-25
	irlength 8
```

# ecpprog

```sh
tom@zen:~$ ecpprog -t
```
```
init..
IDCODE: 0x41111043 (LFE5U-25)
ECP5 Status Register: 0x00200100
flash ID: 0xC8 0x40 0x15
Bye.
```
# OSS-CAD-Suite

https://github.com/YosysHQ/oss-cad-suite-build/releases

```
export PATH="/opt/oss-cad-suite/bin:$PATH"
```

