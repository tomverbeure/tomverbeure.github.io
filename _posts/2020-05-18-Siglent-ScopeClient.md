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

* LXI

    Lan eXtensions for Instrumentation

    Most LXI instruments use either VXI-11 or HiSLIP to communicate.

    * [List of LXI Ports, Protocols, and Services](https://www.lxistandard.org/About/LXI-Protocols.aspx)
    * [LXI Standard Revision 1.0](https://www.lxistandard.org/Documents/Specifications/LXI_Revision_1_0.pdf)

* PortMap
    * Port 111: RPC portmapper. PyVisa code: /home/tom/.local/lib/python3.7/site-packages/pyvisa-py/protocols/rpc.py

        [Remote Procedure Call and the portmapper daemon](http://ibgwww.colorado.edu/~lessem/psyc5112/usail/network/services/portmapper.html) :

        "It maps RPC program numbers to the TCP/IP ports on which their servers are listening. When an RPC server starts, it picks an available port, 
        and then registers that port and what RPC program numbers it will serve with the portmapper daemon. When a client program needs to access a 
        service, it first queries the portmapper on the RPC server's host which reports the TCP and UDP port on which the server is listening, and then 
        it contacts that port to request its service."

    * [portmap Protocol](https://docs.oracle.com/cd/E19683-01/816-1435/6m7rrfnab/index.html)
    * [RPC manpage](https://docs.oracle.com/cd/E19620-01/805-3175/6j31emp62/index.html)
    * [Linux Journal - Remote Procedure Calls](https://www.linuxjournal.com/article/2204)
    * [Siglent SDS1004X-E Bode Plot](https://github.com/4x1md/sds1004x_bode/blob/ec73af7c59d52f662f2d918d9a1239f6f69afae8/sds1004x_bode/awg_server.py#L124)

        This implements a VXI-11 *server* instead of a client.

        The goal is to fake a Siglent waveform generator.

    * Use [liblxi](https://github.com/lxi-tools/liblxi)...

        `sudo apt install liblxi-dev`

    * Structure:

- SCPILxiTransport : public SCPITransport       (Similar to SCPISocketTransport)

```

/home/tom/.local/lib/python3.7/site-packages/vxi11/rpc.py: TCPClinet.__init__:

    calls pmap.get_port

/home/tom/.local/lib/python3.7/site-packages/vxi11/rpc.py: TCPClinet.get_port:

    mapping parameters: (prog = 395183, vers = 1, IPPROTO_TCP:6, 0)

    Per VXI11 spec: Core Channel = RPC program number 395183 / 0x607af, version 1, TCP

/home/tom/.local/lib/python3.7/site-packages/vxi11/rpc.py: make_call:
    Packs all RPC parameters 
        First default parameters (start_call)
        Then specific parameters (args)
    Does the RPC call
    Unpacks the parameters
    result is 9009: port number
```

    * [Discussion about an RPC VXI-11 call with C code](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/Does-VISA-have-VXI-11-Server-implement-to-serve-the-interrupt/td-p/546919?profile.language=en)
    * [VXI11 Ethernet Protocol for Linux](http://optics.eee.nottingham.ac.uk/vxi11/)

        * Code also on GitHub: https://github.com/applied-optics/vxi11
        * Lots of VXI-11 information here, but not about portmap

    * [VXI-11 RPC Programming Guide for the 8065 - An Introduction to RPC Programming](https://www.icselect.com/pdfs/ab80_3.pdf)

    

* VXI-11

    Protocol over TCP/IP to send and receive commands and data to/from instruments. At its core, it uses
    RCP calls.

    Defined in 1995, it has a pretty low performance due to its synchronous nature.

    Supported by the Siglent SDS 2304X.

    [VXI Specifications](http://www.vxibus.org/specifications.html)

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

* VICP

    LeCroy Versatile Instrument Control Protocol

    [LAB_WM827 - Understanding VICP and the VICP Passport](https://teledynelecroy.com/doc/understanding-vicp-and-the-vicp-passport)

    Uses TCP/IP port 1861

    Seems to be similar to SCPI, but proprietary.
    
    

So the overall communications stack looks like this:

There are standardized commands that are understood by all devices due to SCPI. The syntax of these commands follows the
IEE 488.2 standards. The commands are issued by a program through the VISA API. The VISA API can work with pretty much
any low level communication protocol (VX-11/HiSLIP/USBTMC/...). These low level protocols sit on top of generic communication
standards such as TCP/IP, USB, GPIB etc.

# Siglent

All Siglent scopes are using SCPI commands. However, it seems like different Siglnet scope support different low-level transport protocols.

* SDS 2304X

    My SDS 2304X definitely supports VXI-11 over TCP/IP. It uses ports 111 and ports 9009. 
    (See [here](https://www.eevblog.com/forum/testgear/siglent-sds1000x-how-to-make-direct-ethernet-connection/msg1650191/#msg1650191).

    It seems to go as follows: a request to port 111 (portmapper) maps an RPC program number to TCP/IP port 9009 as a VXI-11 compatible port.

    * [Siglent - Programming Example: Using VXI11 (LXI) and Python for LAN control without sockets](https://int.siglent.com/resource-detail/10/)
    

* SDS 1104X-E

    In [this eevblog thread](https://www.eevblog.com/forum/testgear/siglent-sds1000x-how-to-make-direct-ethernet-connection/msg1648898/#msg1648898),
    the way to connect to an SDS 1104X-E is to telnet to port 5024. This doesn't work on the SDS 2304X.

    It uses standard TCP/IP sockets without a VXI-11 layer. You can use telnet with this.

    * [Siglent - Verification of a LAN connection using Telnet](https://int.siglent.com/resource-detail/13/)
    * [Code Example on Siglent website](https://siglentna.com/application-note/python-sdg-x-basics-lan/)


# VXI-11

The Siglent scope uses the VXI-11 over TCP/IP protocol to receive commands and return data to an external client.

VXI-11, defined in 1995, is a network instrument protocol that specified how instruments can be connected to a standard
network.	


# VISA

VISA is the most generic API, so let's use that one.

# Low Level Connection to Siglent Scope through Ethernet

* Plug in Ethernet cable
* Power cycle
* Utility -> I/O (Page 2) -> Lan
    * DHCP: Enable
    * Check (and write down) IP address

# Github Repo

https://github.com/tomverbeure/siglent_remote

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
