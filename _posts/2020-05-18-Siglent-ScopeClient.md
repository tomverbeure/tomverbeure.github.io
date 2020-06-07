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
serving as my work office and lab. And that includes quality time with my oscilloscope, 
a [Siglent SDS2304X](https://siglentna.com/product/sds2304x/).

![Siglent SDS2304X](/assets/siglent/SDS2000Xa.png)

I've had it for more than 2 years now. With 4 channels, 300MHz BW, and some of the additonal
options (16-channel logic analyzer, 25MHz function generator, and various serial protocol
decoders), it was quite the splurge, justified by the "this will be the last scope I'll
ever buy" argument.

But I've come to realization that I've only ever used a fraction of its capabilities. The cable for
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

![Scope Screenshot](/assets/pixel_purse/audio_digital_signal.png)

The problem with that is that you can end up with a USB drive full of screenshot bitmap files 
that are sequentially numbered without any futher annotation or context. It'd be much easier
if I could immediately save the screenshot from the scope straight onto my computer and give
them a clarifying filename.

I knew that the Ethernet and USB type B connectors on the back could be used to remote control 
the scope, but I had never tried.

And thus starteth my descent into the world of protocols to control test equipment.

# A Quickstart Guide to the Test and Measurement Equipment Protocol Stack

When you've never dealt with these kind of protocols before, as was the case for me, you get
bombarded with all kinds of protocols, protocol layers, and APIs. It took me a while to see
the forest through the trees.

But here's what I ended up with:

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
    For Ethernet, telnet, sockets or VXI-11 are commonly used. Some devices support
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
[Lan eXtensions for Instrumentation](https://www.lxistandard.org/) (LXI) standard specifies
the behavior that is specific for LAN/Ethernet communication, and the
[Virtual Instrumnet Software Architecture](https://en.wikipedia.org/wiki/Virtual_instrument_software_architecture) (VISA)
tries to abstract all these transport methods behind one API.

# Transport Protocol Support of Siglent Oscilloscopes 

Most contemporary measurement devices have 2 physical interfaces: USB and an Ethernet/LAN port.

When a USB is present, the scope will usually present itself as one, or both, of the following devices:

* USB Test and Measurement Class device
* USB Serial Port device

On Siglent scopes, the Ethernet port can be one of the following:

* VXI-11

    This is the most common. As far as I was able to figure out, all Siglent scopes support VXI-11.

* TCP/IP Raw Socket

    Less common. Based on the specification sheets, it's now present on all recent scopes. My
    Siglent SDS2304X does not have it.

* TCP/IP Telnet

    Same thing as the TCP/IP Raw Socket: present only on more recent scopes and not on the Siglent
    SDS2304X.

* Web interface

    Some bleeding edge Siglent scopes run an HTTP web server so you can connect your browser straight
    to the scope and control it through a web GUI.

If Siglent has an overview table that clearly lists which transport is supported by which product, I
couldn't find it. But after going through all the specification sheets of each series, I came
up with the following table:


| Series        | USBTMC | VXI-11 | Raw Sockets | Telnet | HTTP |
|---------------|:------:|:------:|:-----------:|:------:|:----:|
| SDS5000X      |    X   |    X   |      X      |    X   |   X  |
| SDS2000X Plus |    X   |    X   |      X      |    X   |      |
| SDS2000X      |    X   |    X   |             |        |      |
| SDS1000X      |    X   |    X   |             |        |      |
| SDS1000X+     |    X   |    X   |             |        |      |
| SDS1000X-E    |    X   |    X   |      X      |    X   |      |
| SDS1000CFL    |    X   |    X   |      ?      |    ?   |      |
| SDS1000DL+    |    X   |    X   |             |        |      |
| SDS1000CML+   |    X   |    X   |             |        |      |

There is also the Siglent SDS3000X, which is a rebranded version of the LeCroy WaveSurfer 3000. 

# VXI-11

My scope only supports VXI-11 on the Ethernet port, so that's what I focused on first.

VXI-11 dates all the way back to 1995. It is layered on top of the 
[ONC Remote Procedure Call](https://en.wikipedia.org/wiki/Open_Network_Computing_Remote_Procedure_Call) 
(RPC) protocol, which itself is layered on top of TCP/IP. You can find the VXI-11 Specification 
[here](http://www.vxibus.org/specifications.htm).

RPC is synchronous by nature, which means that a request needs to be completed before the next one
can be issued. (This can be a performance bottleneck when there's a sequence of many small calls, which
is why HiSLIP was developed as an alternative.)

One interesting feature of VXI-11 is the ability to discover connected devices on the network: instead of
explicitly specifying the IP address or hostname of your device, devices make themselves know by responding 
to a broadcast transmission.

**While it's supposed to be supported, I have not been able to to make this work with my scope!**

*You don't really need to know what follows, but it took me a long time to figure this all out, so I'm recording it
here for posterity.*

Under the hood, making a connection to a VXI-11 enabled device goes in two phases:

* RPC PortMap call to request TCP/IP communication port - Port 111

    All TCP/IP connections go over ports. There is no standard port assigned for VXI-11 transactions, but
    RPC enabled servers often (always?) run a PortMap service on port 111.

    When a client wants to establish an RPC connection, the client first issues a request to the PortMap
    port to ask which TCP/IP port should be used for a particular RPC service. Each RPC service is
    assigned a so-called program number. The program number of the VXI-11 core channel is 395183 / 0x607af.
    (There's also a VXI-11 Abort Channel and a VXI-11 Interrupt channel, which have program numbers
    395184 and 395185 resp.) (Section B.6 of the VXI-11 spec.)

    The PortMap server will reply with the port number that will be used for the actual VXI-11 RPC transaction.

    In my case, the port number returned by the PortMap call is 9009. This seems to be a number that's
    commonly used by Siglent scopes.

* Actual VXI-11 transactions over the assigned port - Port 9009

    Like all RPC programs, the VXI-11 RPC calls are specified in [RPCL](https://en.wikipedia.org/wiki/RPCGEN)
    (Remote Procedure Call Language), a formal description that can be used for code generators such as RPCGEN
    to automatically create client and server stubs for implementation. (Section C of the VXI-11 spec.)

Wireshark was really useful to dump all the traffic between my PC and the scope, and it has built-in
support for VXI-11 RPC calls!

# Setting Up the IP Address of Your Scope

Since I wasn't able to get the VXI-11 discovery to work, I had to set/figure out the IP address of the scope
manually, as follows:

* Plug in Ethernet cable
* Press [Utility] -> [I/O] *(Page 2/3)* -> [LAN]

When using DHCP:
* Set DHCP to Enable

Otherwise:
* Set DHCP to Disable
* Enter the desired IP address

* Press [Single] to exit the LAN settings page
* Power cycle the scope

    New LAN settings don't take effect until you do this!

* After the power cycle, go again to the LAN settings page and write down the assigned IP address.

    *The IP address of my scope is set to 192.168.1.177. I will use that number in the examples below.*

# Interacting with the Siglent Scope with VXI-11 and PyVISA

[PyVISA](https://pyvisa.readthedocs.io/en/latest/) is probably the easiest way to interact remotely
with a measurement device, and it has the major benefit that the same code will work with all transport
protocols that are supported by your scope.

* Install the `pyvisa` library

   ```
   pip3 install pyvisa pyvisa-py
   ```

* Write the following program: `visa_ident.py`

    ```python
    #! /usr/bin/env python3
    import pyvisa
    
    rm = pyvisa.ResourceManager()
    siglent = rm.open_resource("TCPIP::192.168.1.177::INSTR")
    print(siglent.query('*IDN?'))
    ```
 
    `*IDN?` is the standard SCPI identification command.

    `192.168.1.177` is the IP address that has been assigned to the scope in the previous section.

* Result

    ```
    *IDN SIGLENT,SDS2304X,xxxxxxxxxxxxxx,1.2.2.2 R19
    ```

There you have it! The scope returned the brand name, model name, serial number, and the installed firmware version!

# Interacting with the Siglent Scope with VXI-11 and python-vxi11

PyVISA is easy to use and supports pretty much all interfaces that matter, but it's on the heavy
side in terms of code size. If you're sure that VXI-11 is sufficient for your needs, you can
use the lightweigh [`python-vxi11`](http://alexforencich.com/wiki/en/python-vxi11/start) library.

* Install the `python-vxi11` library

    ```sh
    pip3 install python-vxi11
    ```

* Write the follwoing program: `vxi11_ident.py`

    ```python
    #! /usr/bin/env python3
    import vxi11
    
    instr = vxi11.Instrument("192.168.1.177")
    print(instr.ask("*IDN?"))
    ```

* Result

    ```sh
    > ./vxi11_ident.py 
    *IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
    ```


# Interacting with the Siglent Scope with VXI-11 and liblxi

If you want to talk to the scope from within a C or C++ program, there's
a library called `liblxi` which is part of a larger set of utilities called [lxi-tools](https://lxi-tools.github.io/).

I installed `liblxi` from source code to get the latest version, but most distributions have it as precompiled
package as well. On my Ubuntu 18.04 system, it's as simple as running `sudo apt isntall liblxi-dev lxi-tools`.

*Note: lxi-tools comes with a program called `lxi-gui`. That didn't work for me because `lxi-gui` only supports
connecting to the scope using the discovery mechanism.*
    
Let's first try the `lxi` utility:
```sh
> lxi scpi -a 192.168.1.177 "*IDN?"
*IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
```

Using the library in a C program is straightforward as well:

```c
#include <stdio.h>
#include <string.h>
#include <lxi.h>

int main()
{
     char response[65536];
     int device, length, timeout = 1000;
     char *command = "*IDN?";

     lxi_init();
     device = lxi_connect("192.168.1.177", 0, "inst0", timeout, VXI11);
     lxi_send(device, command, strlen(command), timeout);
     lxi_receive(device, response, sizeof(response), timeout);
     printf("%s\n", response);
     lxi_disconnect(device);
}
```

```sh
> gcc -o lxi_test lxi_test.c -llxi
> ./lxi_test 
*IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
```

# Fetching a Screenshot from your Scope using VXI-11

After this huge detour, let's now do what I wanted to do all along: fetch a screenshot from the scope to the PC.

The easiest way is to just use `lxi-tools`:

```
> lxi screenshot -a 192.168.1.177
Loaded siglent-sds screenshot plugin
Saved screenshot image to screenshot_192.168.1.177_2020-06-06_21:57:53.bmp
```



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

    * Structure:

    * [Discussion about an RPC VXI-11 call with C code](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/Does-VISA-have-VXI-11-Server-implement-to-serve-the-interrupt/td-p/546919?profile.language=en)
    * [VXI11 Ethernet Protocol for Linux](http://optics.eee.nottingham.ac.uk/vxi11/)

        * Code also on GitHub: https://github.com/applied-optics/vxi11
        * Lots of VXI-11 information here, but not about portmap

    * [VXI-11 RPC Programming Guide for the 8065 - An Introduction to RPC Programming](https://www.icselect.com/pdfs/ab80_3.pdf)

    


* HiSLIP

    [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol)

    More modern and faster alternative for VXI-11.

* USBTMC

    [USB Test and Measurement Class](https://sigrok.org/wiki/USBTMC).

    USB device class specification for measurement equipement.

* VISA

    [Virtual Instrument Software Architcture](https://en.wikipedia.org/wiki/Virtual_instrument_software_architecture).

    Generic software API to connect to instruments, using protocols like VXI-11, HiSLIP, USBTMC.

* IEEE 488.1 / GPIB

    Communication standard for T&M equipment that goes all the way back to the late 1960s.

    For a long time, this was *the* interface that could be found on pretty much all equipment, but it has
    since been replaced by USB and Ethernet.

* IEEE 488.2

    Specifies a standard command syntax to test and measurement equipment.

* SCPI ('skippy')

    [Standard Commands for Programmable Instruments](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments).

    A set of standard commands for test and measurement equipment that uses the IEEE 488.2 syntax.

* VICP

    LeCroy Versatile Instrument Control Protocol

    [LAB_WM827 - Understanding VICP and the VICP Passport](https://teledynelecroy.com/doc/understanding-vicp-and-the-vicp-passport)

    Uses TCP/IP port 1861

    Seems to be similar to SCPI, but proprietary.
    
    

So the overall communications stack looks like this:

# Siglent

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


# Github Repo

https://github.com/tomverbeure/siglent_remote

# Connecting with Python using USB

```
pip3 install python-usbtmc
```

(See http://alexforencich.com/wiki/en/python-usbtmc/readme)


Resources:

* [Connection with Python and VXI11](https://siglentna.com/application-note/programming-example-vxi11-python-lan/)
* [VXI-11 Specification](https://www.vxibus.org/specifications.html)
* [Siglent Remote Control Manual](https://siglentna.com/USA_website_2014/Documents/Program_Material/SIGLENT_Digital_Oscilloscopes_Remote%20Control%20Manual.pdf)
* [PyVisa](https://pyvisa.readthedocs.io/en/1.8/index.html)
* [Linux USBTMC Kernel driver 4.19](https://github.com/torvalds/linux/blob/v4.19/drivers/usb/class/usbtmc.c)
* [Linux USBTMC Kernel driver 4.20](https://github.com/torvalds/linux/blob/v4.20/drivers/usb/class/usbtmc.c)
* [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol)



