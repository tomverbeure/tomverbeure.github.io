---
layout: post
title: Siglent SDS 2304X Remote Control
date:  2020-05-18 00:00:00 -1000
categories:
---

* TOC
{:toc}


* Compile on Ubuntu 18.04.
    * Does not compile with 16.04.
* Change source code to point to local shaders in ./src/glscopeclient/main.c: ...chdir...
*

# Communication Standards for Test and Measurement Equipment

* VXI-11

    Protocol over TCP/IP to send and receive commands and data to/from instruments. At its core, it uses
    RCP calls.

    Defined in 1995, it has a pretty low performance due to its synchronous nature.

    Supported by the Siglent SDS 2304X.

* HiSLIP

    [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol)

    More modern and faster alternative for VXI-11.

* USBTMC

    [USB Test and Measurement Class](https://sigrok.org/wiki/USBTMC).

    USB device class specification for measurement equipement.

* VISA

    [Virtual Instrument Software Architcture](https://en.wikipedia.org/wiki/Virtual_instrument_software_architecture).

    Generic software API to connect to instruments, using protocols like VXI-11, HiSLIP, USBTMC.

* IEEE 488.2

    Standard command syntax to test and measurement equipment.

* SCPI ('skippy')

    [Standard Commands for Programmable Instruments](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments).

    A set of standard commands for test and measurement equipment that uses the IEEE 488.2 syntax.

So the overall communications stack looks like this:

There are standardized commands that are understood by all devices due to SCPI. The syntax of these commands follows the
IEE 488.2 standards. The commands are issued by a program through the VISA API. The VISA API can work with pretty much
any low level communication protocol (VX-11/HiSLIP/USBTMC/...). These low level protocols sit on top of generic communication
standards such as TCP/IP, USB, GPIB etc.

# VXI-11

The Siglent scope uses the VXI-11 over TCP/IP protocol to receive commands and return data to an external client.

VXI-11, defined in 1995, is a network instrument protocol that specified how instruments can be connected to a standard
network.	


# VISA

VISA is the most generic API, so let's use that one.

# Connecting with Python using USB

```
pip3 install python-usbtmc
```

(See http://alexforencich.com/wiki/en/python-usbtmc/readme)

# Connecting with Python using VXI-11

```
pip3 install python-vxi11
```

Python code:

```python
#! /usr/bin/env python3

import vxi11

instr = vxi11.Instrument("192.168.1.176")
print(instr.ask("*IDN?"))
```

Result:

```
*IDN SIGLENT,SDS2304X,xxxxxxxxxxxxxx,1.2.2.2 R10
```

# Connecting with Python using VISA

```
pip3 install pyvisa pyvisa-py
```

Python code:

```python
#! /usr/bin/env python3

import pyvisa

rm = pyvisa.ResourceManager()
siglent = rm.open_resource("TCPIP::192.168.1.176::INSTR")
print(siglent.query('*IDN?'))
```

Result:
```
*IDN SIGLENT,SDS2304X,xxxxxxxxxxxxxx,1.2.2.2 R10
```



Resources:

* [Connection with Python and VXI11](https://siglentna.com/application-note/programming-example-vxi11-python-lan/)
* [VXI-11 Specification](https://www.vxibus.org/specifications.html)
* [Siglent Remote Control Manual](https://siglentna.com/USA_website_2014/Documents/Program_Material/SIGLENT_Digital_Oscilloscopes_Remote%20Control%20Manual.pdf)
* [PyVisa](https://pyvisa.readthedocs.io/en/1.8/index.html)
