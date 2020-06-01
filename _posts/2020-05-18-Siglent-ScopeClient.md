---
layout: post
title: Siglent SDS2304X Remote Control
date:  2020-05-18 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

With the whole shelter in place going on, I've been spending a lot of time in my garage, now
serving as my work office and lab. And that includes quite a bit of quality time with my
oscilloscope, a [Siglent SDS2304X](https://siglentna.com/product/sds2304x/).

I've had it for more than 2 years now. With 4 channels, 300MHz BW, and some of the additonal
options (16-channel logic analyzer, 25MHz function generator, and various serial protocol
decoders), it was quite the splurge.

But I came to realization that I'm only ever used a fraction of its capabilities. The cable for
the 16-channel logic analyzer is still in the box. The function generator has only be switched on 
to verify that, yes, it actually works. And while I have used the I2C and UART decoders a few
times, when I really want to decode these kind of traces, a [Saleae logic analyzer](https://www.saleae.com) 
is usually a much better choice.[^1]

[^1]: Due to the shelter in place, the Saleae Logic Pro 16 from work is now at home, and it's 
    amazing.  I love its ability to do long term analog traces at 50MS/s.

One feature that I have used is that ability to take screenshots to add as illustration to 
[some of my blog posts](/2019/10/03/Pixel-Purse.html#audio-upload-interface). But I've
always used them the primitive way: by saving the screenshot on a USB drive that's plugged
into the USB type A connector on the front of the scope.

The problem with that is that you can end up with a USB drive full of screenshot bitmap files 
that are sequentially numbered without any futher annotation or context. It'd be much easier
if I could immediately save the screenshot from the scope straight onto my computer and give
them a clarifying filename.

I knew that the Ethernet and USB type B connectors on the back could be used to remote control 
the scope, but I had never tried.

And thus starteth my descent into the world of protocols to control test equipment.

# A Quickstart Guide to the Test and Measurement Equipment Protocol Stack

When you've never dealt with these kind of protocol before, as was the case for me, you get
bombared with all kinds of protocols and protocol layers. It took me a little bit to see
the forest through the trees.

But here's what I ended up with:

![Instrument Control Protocols]({{ "/assets/siglent/Instrument_Control_Protocols.svg" | absolute_url }})

There are essentially 3 layers. They probably have an official name, but I've named them myself as follows.

* physical layer

    The method by which the scope is connected to your computer. Today, the 2 most common
    interfaces are Ethernet and USB, but older ones include 
    [RS-232](https://en.wikipedia.org/wiki/RS-232), 
    [RS-422](https://en.wikipedia.org/wiki/RS-422), 
    [GPIB (IEEE-488.1)](https://en.wikipedia.org/wiki/IEEE-488), 
    and [VXI bus](https://en.wikipedia.org/wiki/VME_eXtensions_for_Instrumentation).

* transport layer

    This is the higher level protocol that is used on top of the physical layer. When
    using USB, this layer is almost always USB Test and Measurement Class (USBTMC). For
    Ethernet, telnet, sockets or VXI-11 are commonly used. Some devices support
    the more modern HiSLIP.

* command layer

    This specifies the syntax of commands that are issued over the transport layer. Most
    equipment supports 
    [SCPI (Standard Commands for Programmable Instruments, aka 'Skippy')](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments). 


If this sounds all simply enough, don't worry: it's not as clear-cut as I'm making it out to be.
LeCroy has a thing called VICP (Versatile Instrument Control Protocol), a protocol that seems cover
both the transport layer (running on top of TCP/IP and the command layer). And USBTMC uses a messaging
system that uses GPIB/IEEE-488 messaging. 

To make things even more fun, the fact that these standards are well defined doesn't mean that
equipment follows them. Rigol oscilloscopes are known to use different TCP/IP port number than those
mandated by the standard. USBTMC has seen very buggy implementations. Some Siglent oscilloscopes
support raw TCP/IP sockets as transport layer while others only support VXI-11... and it's impossible
to find documentation that illustrates this. And so forth.




# References:
* [Standard Commands for Programmable Instruments (SCPI) Specification](https://www.ivifoundation.org/docs/scpi-99.pdf)


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
