---
layout: post
title: Making Sense of Test and Measurement Protocols
date:  2020-06-07 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

With the whole shelter in place going on, I've been spending a lot of time in my garage, now
serving as my work office and lab. And that includes quality time with my oscilloscope, 
a [Siglent SDS2304X](https://siglentna.com/product/sds2304x/).

![Siglent SDS2304X](/assets/siglent/SDS2000Xa.png)

One feature that I have used quite a bit is the ability to take screenshots to add as 
illustration to 
[some of my blog posts](/2019/10/03/Pixel-Purse.html#audio-upload-interface). But I've
always used them the primitive way: by saving the screenshot on a USB drive that's plugged
into the USB type A connector on the front of the scope.

![Scope Screenshot](/assets/pixel_purse/audio_digital_signal.png)

The problem with that is that you can end up with a USB drive full of screenshot bitmap files 
that are sequentially numbered without any futher annotation or context. It'd be much easier
if I could immediately save the screenshot from the scope straight onto my computer and give
them a clarifying filename.

I knew that the Ethernet and USB type B connectors on the back could be used to remote control 
the scope, but I had never tried.

![Siglent SDS2304X Back](/assets/siglent/SDS2000Xb-back.png)

And thus starteth my descent into the world of protocols to control test equipment.

*I first start by looking at the general parts of the whole protocol stack. In later blog posts, 
things will get more specific.*

# An Overview of the Test and Measurement Equipment Protocol Stack

When you've never dealt with these kind of protocols before, it's easy to get overwhelmed with all kinds of 
protocols, protocol layers, and APIs. It took me a while to see the forest through the trees, but here's what 
I ended up with:

![Instrument Control Protocols]({{ "/assets/siglent/Instrument_Control_Layers.svg" | absolute_url }})

There are essentially 3 layers. They probably have an official name, but I've named them myself as follows.

* physical layer

    The physical method by which the scope is connected to your computer. Today, the 2 most common
    interfaces are Ethernet and USB, but older ones include 
    [GPIB (IEEE-488.1)](https://en.wikipedia.org/wiki/IEEE-488), 
    [RS-232](https://en.wikipedia.org/wiki/RS-232), 
    [RS-422](https://en.wikipedia.org/wiki/RS-422), 
    and [VXI bus](https://en.wikipedia.org/wiki/VME_eXtensions_for_Instrumentation).

* transport layer

    This is the higher level protocol that is used on top of the physical layer. When
    using USB, this layer is almost always [USB Test and Measurement Class](https://sigrok.org/wiki/USBTMC) (USBTMC). 
    For Ethernet, telnet, raw sockets or VXI-11 are commonly used. Some devices support
    the more modern [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol) (HiSLIP).

    In some cases, a name will cover the physical layer and the transport layer: GPIB/IEEE 488.1
    nomenclature is used for both the physical layer and the transport layer.


* command layer

    This specifies the syntax of commands that are issued over the transport layer. Most
    equipment supports 
    [SCPI (Standard Commands for Programmable Instruments, aka 'Skippy')](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments). 

    While SCPI is a standard at the lowest level, each brand has its own variant with it
    comes to commands and how they are formatted.

If this sounds all simple enough, don't worry: it's not as clear-cut as I'm making it out to be.
For example, USBTMC has a messaging system that has been borrowed almost entirely from GPIB/IEEE-488.2

To make things even more fun, the fact that these standards are well defined doesn't mean that
equipment follows them. Rigol oscilloscopes are known to use a different TCP/IP port number than those
mandated by the standard. USBTMC has seen very buggy implementations. Some Siglent oscilloscopes
support raw TCP/IP sockets as transport layer while others only support VXI-11.

When tying all of this together in an automation setup, there's a lot of complexity to manage.
But fear not: other standards were created to bring some uniformity to the whole deal. The 
[Lan eXtensions for Instrumentation](https://www.lxistandard.org/) (LXI) consortium oversees standards
that are related to LAN/Ethernet communication, and the
[Virtual Instrument Software Architecture](https://en.wikipedia.org/wiki/Virtual_instrument_software_architecture) (VISA)
tries to abstract all these transport methods behind one API.


# LAN - VXI-11

VXI-11 dates all the way back to 1995. It is layered on top of the 
[ONC Remote Procedure Call](https://en.wikipedia.org/wiki/Open_Network_Computing_Remote_Procedure_Call) 
(RPC) protocol, which itself is layered on top of TCP/IP. You can find the VXI-11 Specification 
[here](http://www.vxibus.org/specifications.html).

RPC is synchronous by nature, which means that a request needs to be completed before the next one
can be issued. (This can be a performance bottleneck when there's a sequence of many small calls, which
is why HiSLIP was developed as an alternative.)

One interesting feature of VXI-11 is the ability to discover connected devices on the network: instead of
explicitly specifying the IP address or hostname of your device, devices make themselves know by responding 
to a broadcast transmission.

**While it's supposed to be supported, I have not been able to to make this work with my scope!**

*Everything that follows in this section is nicely hidden behind APIs, but it took me a long time to figure 
this all out, so I'm recording it here for posterity. Feel free to skip.*

Under the hood, making a connection to a VXI-11 enabled device goes in two phases:

* RPC PortMap call to request TCP/IP communication port - Port 111

    All TCP/IP connections go over ports. There is no standard port assigned for VXI-11 transactions, but
    RPC enabled servers often (always?) run a PortMap service on port 111.

    When a client wants to establish an RPC connection, the client first issues a request to the PortMap
    port to ask which TCP/IP port should be used for a particular RPC service. Each RPC service is
    assigned a so-called program number. The program number of the VXI-11 core channel is 395183 / 0x607af.
    (There's also a VXI-11 Abort Channel and a VXI-11 Interrupt channel, which have program numbers
    395184 and 395185 resp.) (Section B.6 of the VXI-11 spec.)

    The PortMap server replies with the port number that should be used for the actual VXI-11 RPC transaction.

    In my case, the port number returned by the PortMap call is 9009. This seems to be a number that's
    commonly used by Siglent scopes.

* Actual VXI-11 transactions over the assigned port - Port 9009

    Like all RPC programs, the VXI-11 RPC calls are specified in [RPCL](https://en.wikipedia.org/wiki/RPCGEN)
    (Remote Procedure Call Language), a formal description that can be used for code generators such as RPCGEN
    to automatically create client and server stubs for implementation. (Section C of the VXI-11 spec.)

Wireshark was really useful to dump all the traffic between my PC and the scope, and it has built-in
support for VXI-11 RPC calls!

Various documentation, code, references:
* VXI-11 Specific
    * [Discussion about an RPC VXI-11 call with C code](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/Does-VISA-have-VXI-11-Server-implement-to-serve-the-interrupt/td-p/546919?profile.language=en)
    * [VXI11 Ethernet Protocol for Linux](http://optics.eee.nottingham.ac.uk/vxi11/)
        * Code also on [GitHub](https://github.com/applied-optics/vxi11)
        * Lots of VXI-11 information here, but not about portmap
    * [VXI-11 RPC Programming Guide for the 8065 - An Introduction to RPC Programming](https://www.icselect.com/pdfs/ab80_3.pdf)
    * [Siglent SDS1004X-E Bode Plot](https://github.com/4x1md/sds1004x_bode/blob/ec73af7c59d52f662f2d918d9a1239f6f69afae8/sds1004x_bode/awg_server.py#L124)

        This implements a VXI-11 *server* instead of a client.

        The goal is to fake a Siglent waveform generator.

* Generic RCP and portmap info:
    * [portmap Protocol](https://docs.oracle.com/cd/E19683-01/816-1435/6m7rrfnab/index.html)
    * [RPC manpage](https://docs.oracle.com/cd/E19620-01/805-3175/6j31emp62/index.html)
    * [Linux Journal - Remote Procedure Calls](https://www.linuxjournal.com/article/2204)
    * [Remote Procedure Call and the portmapper daemon](http://ibgwww.colorado.edu/~lessem/psyc5112/usail/network/services/portmapper.html) :

# LAN - TCP/IP Raw Sockets

Instead of using a VXI-11 (which is a layer on top of TCP/IP sockets), some equipment doesn't bother and simply
transmits and receives commands and data using raw sockets.

VXI-11 offers additional features such as abort and interrupt channels, but more often than not, this is not
needed.

One benefit of raw sockets is that you're not constrained by the synchronous nature of RPC calls: if you like,
you can issue multiple request before fetching the data.

# LAN - Telnet 

Telnet is a relatively thin layer over raw sockets: it's totally possible (and common) to `telnet` into a server
which supports regular sockets and type the command that would otherwise be entered by a client.

As a result, it's not clear to me whether there's a real difference in service on a scope that annouces raw
sockets and telnet support over Ethernet.

# LAN - HiSLIP

Defined by the [Interchangable Virtual Instruments (IVI) Foundation](https://www.ivifoundation.org) (which
also manages the VISA API and the SCPI specifications), the
[High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol) is
a modern and faster alternative for VXI-11. 

Its primary benefit is the asynchronous 'overlap mode', which allows multiple commands to be transmitted
without first waiting for their return data. This makes it possible to fully use the bandwidth of the
Ethernet channel.

The official specification is 
[here](https://www.ivifoundation.org/downloads/Protocol%20Specifications/IVI-6.1_HiSLIP-1.1-2011-02-24.pdf).

I didn't run into any equipment with HiSLIP support (but I also didn't look for it!).

# LAN - VICP

The Versatile Instrument Control Protocol (VICP) is another transport protocol on top of TCP/IP. It's
specific to LeCroy. While it's still supported on many modern LeCroy oscilloscopes, most of them also
support VXI-11.

I couldn't find a real VICP specification, but you can find an 
[open source support library](https://sourceforge.net/projects/lecroyvicp/), published by LeCroy engineers, on SourceForge.

References:
* [LAB_WM827 - Understanding VICP and the VICP Passport](https://teledynelecroy.com/doc/understanding-vicp-and-the-vicp-passport)
* [Introduction the LXI Interface](https://teledynelecroy.com/doc/introducing-the-lxi-interface)

# LAN - LXI Oversees LAN Instrumentation Standards

The [Lan eXtensions for Instrumentation](https://en.wikipedia.org/wiki/LAN_eXtensions_for_Instrumentation)
(LXI) consortium oversees a number of standards related to communication protocols for instrumentationa and
data acquisition that use Ethernet.

The list of standards can be found [here](https://lxistandard.org/Specifications/Specifications.aspx) and
includes the LXI Device Specification, HiSLIP, Clock Synchronization etc.

# USB - USBTMC

In the USB world, there are base USB specifications, which detail everything from the mechanical properties
of connectors to overall protocol used to exchange data. And then there are numerous additional class
specifications that describe how devices of a certain class are supposed to exchange data with a host.

The [USB Test and Measurement Class Specification](https://sigrok.org/wiki/USBTMC) is the device class for, 
well, test and measurement equipment.

The [specification](https://www.usb.org/document-library/test-measurement-class-specification)
is a suprisingly short 40 pages and more or less readable.

It defines a number of endpoints (virtual data channels) that must be used to transmit and receive data, 
message types, packet headers, and how data needs to be encapsulated inside those packets.

There is also a subclass specification that defines the communication of IEEE-488 traffic over USB.

Almost all modern test and measurement equipment today has a USBTMC compatible USB port.

# USB - Serial

Some devices support the serial-over-USB protocol. These are often cheaper devices that just need a
few simple ways to configure themselves.

# GPIB / IEEE-488

Going back all the way to the late 1960s, there was a time when all T&M equipment was equiped with
a GPIB interface. 

Standarized as [IEEE-488](https://en.wikipedia.org/wiki/IEEE-488), it supports an 8-bit parallel bus 
that can transfer at speeds of up 8MByte/s (1MByte/s on older devices), up to 15 devices in a daisy-chained 
cable configuration, separation of control and data transfers (a controller can instruct one device to 
send data directly to multiple listening devices without being involved in the data transfer itself), 
device service requests (interrupts) using serial or parallel polling, etc.

There are 2 parts to the specification: IEEE-488.1 deals with the phyisical aspects and electrical signalling 
while IEEE-488.2 defines the command structure. The more recent SCPI standard (see below) is layered on top
of the IEEE-488.2 specification.

One of the major factors behind its demise were the cost of the GPIB connector itself and the cable.

Modern equipment has dropped the GPIB connector for LAN and USB ports, but you can still find plenty of
GPIB equipment in the lab. (A kick-ass power supply or 6-digit multimeter from 30 years ago is very likely
still a kick-ass power supply or multimeter today! And that's reflected in their prices on eBay.)

If you want to control a GPIB-equiped device today, there are 
[USB interface dongles](/2020/06/27/Tektronix-TDS420A-Remote-Control-over-GPIB.html#acquiring-a-usb-to-gpib-dongle) 
such as the National Instruments GPIB-USB-HS or the Agilent 82375B. One eBay, they can be found for prices of $70
and up.

The official IEEE-488 specifications are only available behind a paywall. Getting your hands on it will
depends on your wallet or on your persistence in going through Google search results for the term
"ieee standard digital interface for programmable instrumentation".

Resources: 
* [Fundamentals of GPIB](https://www.youtube.com/watch?v=MH-srU3bPmU)

    The first half of this 1988 video is suprisingly insructive!

* [What is GPIB / IEEE 488 Bus](https://www.electronics-notes.com/articles/test-methods/gpib-ieee-488-bus/what-is-gpib-ieee488.php) 

    A pretty comprehesive article that covers low level signalling protocol, connector pinout, 
    addressing, and more.

* [IEEE-488.2 Command Command](http://rfmw.em.keysight.com/spdhelpfiles/truevolt/webhelp/US/Content/__I_SCPI/IEEE-488_Common_Commands.htm)

    Lists various command IEEE-488.2 commands, with examples on how to use them.


# VISA - One API that Rules Them All

With all these different transport standards, you'd think it'll be a nightmare to remote control
various instruments, but you'd be wrong (to a certain extent...)

The IVI Foundation has the VISA API specification: an generic API that hides the lower level details
of each transport protocol.

There are commercial and open source implementation for different operating systems.

[NI VISA](https://www.ni.com/en-us/support/documentation/supplemental/06/ni-visa-overview.html) by National
Instruments is one such commercial implementation. [PyVISA](https://pyvisa.readthedocs.io/en/latest/) is
probably the most common open source one.

To give an idea about how easy it is to connect to my Siglent scope with PyVISA, the following code queries
and prints the scope identification string over VXI-11:

```python
import pyvisa

rm = pyvisa.ResourceManager('@py')
siglent = rm.open_resource("TCPIP::192.168.1.177")
print(siglent.query('*IDN?'))
```

And this code does the same using USBTMC:

```python
import pyvisa

rm = pyvisa.ResourceManager('@py')
siglent = rm.open_resource("USB0::0xF4EC::0xEE3A7:SDS2Xxxxxxxxxx")
print(siglent.query('*IDN?'))
```

All it took was changing the resource path... Accessing a device over GPIB wouldn't be any more complicated.

Strictly speaking, `PyVISA-py` is the library that implements the Python VISA backends, while `PyVISA` is a
utility library on top of that. In addition to `PyVISA-py`, `PyVISA` can also use the NI VISA or other
backends.

# SCPI - The 'Universal' Command Language

After going through all these transport layers, it finally time to go up one level in the stack.

The [Standard Commands for Programmable Instruments](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments)
(SCPI aka 'skippy') standard is a specification from 1999 that's layered on top of the IEEE-488.2 command
specification. It can be downloaded [here](https://www.ivifoundation.org/docs/scpi-99.pdf).

Let's to go straight to the source to see what SCPI is trying to achieve:

> Standard Commands for Programmable Instruments (SCPI) is the new instrument command language 
> for controlling instruments that goes beyond IEEE 488.2 to address a wide variety of instrument 
> functions in a standard manner. SCPI promotes consistency, from the remote programming standpoint, 
> between instruments of the same class and between instruments with the same functional capability. 
> For a given measurement function such as frequency or voltage, SCPI defines the specific command 
> set that is available for that function. Thus, two oscilloscopes made by different manufacturers 
> could be used to make frequency measurements in the same way. It is also possible for a SCPI counter 
> to make a frequency measurement using the same commands as an oscilloscope.

It's questionable whether or not SCPI achieved that goal.

To fetch an acquired waveform from an oscilloscope, SCPI defines the `DATA(CURVe(..))` command. 
My [Tektronix TDS 420A](/2020/06/27/In-the-Lab-Tektronix-TDS420A.html), has the 
[`CURVe?`](/2020/06/27/Tektronix-TDS420A-Remote-Control-over-GPIB.html#fetching-a-waveform---the-bare-minimum) 
command (no `DATA(...)`) required, my Siglent uses `WF?`, a Rigol scope uses `WAV:DATA?`, 
and Rohde-Schwartz has `:DATA?`.

The only consistency here is that there is none.

In practise, every kind of instrumentation equipment will need a vendor or even device specific driver 
for remote control...

# To Be Continued...

So far, everything covered here is only describes what's out there and how it all plays with eachother.

The next step is to show how all of this can be made to work, the pitfalls etc.

That's for upcoming blog posts...


