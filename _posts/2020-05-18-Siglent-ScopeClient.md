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
bombarded with all kinds of protocols, protocol layers, and APIs. It took me a little bit to see
the forest through the trees.

But here's what I ended up with:

![Instrument Control Protocols]({{ "/assets/siglent/Instrument_Control_Layers.svg" | absolute_url }})

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
    
If this sounds all simply enough, don't worry: it's not as clear-cut as I'm making it out to be.
For example, USBTMC has a messaging system that has been borrowed almost entirely from GPIB/IEEE-488.2

To make things even more fun, the fact that these standards are well defined doesn't mean that
equipment follows them. Rigol oscilloscopes are known to use a different TCP/IP port number than those
mandated by the standard. USBTMC has seen very buggy implementations. Some Siglent oscilloscopes
support raw TCP/IP sockets as transport layer while others only support VXI-11.

When tying all of this together in an automation setup, there's a lot of complexity to manage.
But fear not: other standards were created to bring some uniformity to the whole deal. The 
[Lan eXtensions for Instrumentation](https://www.lxistandard.org/) (LXI) is a standard to specifies
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
    assigned a so-called program number, the program number of VXI-11 core channel is 395183 / 0x607af.
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
manually.

* Plug in Ethernet cable
* Press [Utility] -> [I/O] *(Page 2/3)* -> [LAN]

When using DHCP:
* Set DHCP to Enable

Otherwise:
* Set DHCP to Disable
* Enter the desired IP address

* Press [Single] to exist the LAN settings page
* Power cycle the scope

    New LAN settings don't take effect until you do this!

* After the power cycle, go again to the LAN settings page and write down the assigned IP address.

# Interacting with the Siglent Scope with VXI-11 and PyVISA

[PyVISA](https://pyvisa.readthedocs.io/en/latest/) is probably the easiest way to interact remotely
with a measurement device. 

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

# Interacting with the Siglent Scope with VXI-11 and liblxi

If you want to talk to the scope from within a C or C++ program, you can't use `PyVISA`, but there's
a library called `liblxi` that part of a larger set of utilities called [lxi-tools](https://lxi-tools.github.io/).

I installed `liblxi` from source code to get the latest version, but most distributions have it as precompiled
package as well. On my Ubuntu 18.04 system, it's as simple as running `sudo apt isntall liblxi-dev lxi-tools`.

*Note: lxi-tools comes with a program called `lxi-gui`. That didn't work for me because `lxi-gui` only supports
connecting to the scope using the discovery mechanism.*
    
Let's first try the `lxi` utility:
```sh
> lxi scpi -a 192.168.1.177 "*IDN?"
*IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
```

Using the library in a C program isn't much more difficult:

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

# USBTMC

In the USB world, there are base USB speficiations, which detail everything from the mechanical properties
of connectors to overall protocol used to exchange data. And then there are numerous additional class
specifications that describe how devices of a certain class are supposed to exchange data with a host.

The [USB Test and Measurment Class Specification](xxx) is one of those device classes.

It defines a number of endpoints (virtual data channels) that must be used to transmit and receive data, 
message types, packet headers, and how data needs to be encapsulated inside those packets.

There is also a subclass that specifies the communication of  IEEE-488 traffic over USB.

Almost all modern test and measurement equipment today has a USBTMC compatible USB port.

# Linux and USBTMC

There are plenty of Windows tools that allow one to control USBTMC devices, but Linux is a different story.
It took a lot of googling around before I had a clear picture. Here's what I found. 

In general, there are 2 major ways to implement a specific USB class driver under Linux:

* a dedicated class driver that's part of the Linux kernel

    There is a usbtmc driver for the Linux kernel. Or better, there are a bunch of them: 
    a very old one that's not compatible with anything recent, one that was the official one
    until sometime 2018 which didn't have an API version, but let's call it version 1. And
    Version 2, backwards compatible with version 1, that can be found in kernels 4.20 and later.

* a user mode driver that uses generic USB device driver

    User mode drivers are typically implemented by using the `libusb` library.

    A major disadvantage of user mode drivers is that they are specific to a particular application.
    Sigrok is a good example of an application that has [its own USBTMC user mode driver](https://sigrok.org/gitweb/?p=libsigrok.git;a=blob;f=src/scpi/scpi_usbtmc_libusb.c).

A library like PyVISA, which hides the details of all kinds of interfaces, can use either the kernel driver
or a [user mode driver](https://github.com/pyvisa/pyvisa-py/blob/master/pyvisa-py/protocols/usbtmc.py).

# The Linux USBTMC Kernel Drivers

When you google for USBTMC kernel drivers, you can find articles and source code, but very often things
will just not work.

A good example is the ["USBTMC Kernel Driver Documentation"](https://www.keysight.com/upload/cmc_upload/All/usbtmc.htm?&cc=US&lc=eng) 
article on the Keysight website. It's the number one result for a "linux usbtmc" search on Google, yet
the information in it is almost completely obsolete. 
The most basic example works, but the moment IOCTL calls or usbtmc specific struct come into play, the code 
doesn't compile. It turns out that this article is about a kernel driver that was never part of the Linux 
kernel, but one that was[^2] downloadable from the Agilent (now Keysight) website. 

[^2]: "... *was* downloadable ..." because that the link to that code is dead.

There are 2 USBTMC drivers that are officially part of the Linux kernel: version 1 (all kernels before 4.20),
and version 2 (everything 4.20 and later). Version 2 is backwards compatible with version 1.

The most important differences:

* Version 1 has a fixed 5s timeout. Version 2 defaults to 5s, but the timeout is programmable.

    This is important for my Siglent scope because request for waveforms larger than 2.8M samples
    require a larger than 5s preparation time.

* Internal buffer of 2048 vs 4096 bytes

    Large USB bulk read requests get split up into smaller request with a size of this buffer.
    In theory, this is something that's entirely hidden from the user (who can issue read request
    for pretty much any size), but it turns out that bugs in the Siglent USBTMC USB device driver 
    result complete hang of this driver when reads are issued that are almost the size of this
    internal buffer size.
* More efficient read transfers
* Support for USBTMC-USB488 features
* Expanded support for the IVI library 
* A way to query the kernel API version 

    The original driver didn't support a way to detect the driver version.

# Linux, USBTMC, and the Siglent SDS2304X

Once I figured out that my Siglent oscilloscope only supports VXI-11 and not TCP/IP sockets or telnet,
controlling via Ethernet was relatively painless.

Getting it to work using USBTMC was a different story.

I first tested it on Windows 10, with the [National Instruments NI-VISA driver](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210)
and Siglent's [EasyScopeX](https://siglentna.com/service-and-support/firmware-software/digital-oscilloscopes/), and
it worked fine.

However, I ran into issues with both using the usbtmc kernel driver (version 1) directly and with
PyVisa.

Eventually, I had to turn to Wireshark to observe exactly what was going on.

Let's first look at my test program:

```c
/* usbtmc_trivial.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

// The scope has a maximum waveform capture size of 140M.
int buffer_size = 150000000;
char *buffer;

int query(int file, char *cmd)
{
    printf("Cmd: %s\n", cmd);
    write(file,cmd,strlen(cmd));

    int bytes_fetched=read(file,buffer,buffer_size);
    printf("Size: %d\n",bytes_fetched);
    buffer[bytes_fetched]=0;
    printf("Response:\n%s\n",buffer);

    return bytes_fetched;
}

int main(int argc, char **argv)
{
    buffer = (char *)malloc(buffer_size);

    int tmc_file=open("/dev/usbtmc0",O_RDWR);
    if(tmc_file>0)
    {
        query(tmc_file, "*IDN?");
        query(tmc_file, "C1:WF? DESC");
    }
}
```

When you run this, everything is great:
```
tom@thinkcenter:~/projects/siglent_remote/usbtmc$ sudo ./usbtmc_trivial 
Cmd: *IDN?
Size: 49
Response:
*IDN SIGLENT,SDS2304X,SDS2Xxxxxxxxxx,1.2.2.2 R19

Cmd: C1:WF? DESC
Size: 369
Response:
C1:WF DESC,#9000000346WAVEDESC
```

The `WF? DESC` comment returns a struct with all information about the waveform that was captured,
but not the waveform itself.

To do that, we need to add the following line to the case:

```c
        ...
        query(tmc_file, "C1:WF? DESC");
        query(tmc_file, "C1:WF? DAT2");             // Fetch actual waveform data
        ...
```

Run this, and here's the result:
```
tom@thinkcenter:~/projects/siglent_remote/usbtmc$ sudo ./usbtmc_trivial_hang 
Cmd: *IDN?
Size: 49
Response:
*IDN SIGLENT,SDS2304X,SDS2Xxxxxxxxxx,1.2.2.2 R19

Cmd: C1:WF? DESC
Size: 369
Response:
C1:WF DESC,#9000000346WAVEDESC

Cmd: C1:WF? DAT2
Size: -1
Response:
```

The `WF? DAT2` request timed out. But it gets better: if you now issue any USBTMC query to the scope, every single
request time out as well. And it will stay that way until your power cycle the scope! 

I checked out the behavior with [Wireshark](https://www.wireshark.org/) and found the Linux USBTMC driver splits
up the data request into request with a maximum size of 2048 (in line with 2048 buffer that gets allocated
in the USBTMC driver), and that USBTMC driver inserts messages for each additonal chunk. Windows doesn't have
that behavior.

I found 2 ways around that:

* Split up the waveform into chunks of less than 2048 bytes by using the `WFSU` command.

    This requires 2 SCPI calls per fetch of ~2000 bytes, which adds a considerable amount 
    of overhead.

* Issue consecutive reads to the TMC driver where each read request 2032 bytes or less.

    Why 2032 and not 2048? Beats me! Requesting 2033 is sufficient to trigger then denial
    of service behavior mentioned earlier!

```
XXX screenshot.
```

Here's the version that issues a bunch of reads with a size of 2032:

```c
void query(int file, char *cmd)
{
    printf("Cmd: %s\n", cmd);
    write(file,cmd,strlen(cmd));

    int max_bytes_per_req = 2032;
    int i = 0;
    int bytes_fetched, bytes_requested;
    do{
        bytes_requested = MIN(max_bytes_per_req, buffer_size-i);
        bytes_fetched = read(file, buffer+i, bytes_requested);
        printf("Size: %d\n",bytes_fetched);
        i += bytes_fetched;
    } while(bytes_fetched == bytes_requested);

    buffer[i]=0;
    printf("Response:\n%s\n",buffer);
}
```

```
tom@thinkcenter:~/projects/siglent_remote/usbtmc$ sudo ./usbtmc_multiple_reads 
Cmd: *IDN?
Size: 49
Response:
*IDN SIGLENT,SDS2304X,SDS2Xxxxxxxxxx,1.2.2.2 R19

Cmd: C1:WF? DESC
Size: 369
Response:
C1:WF DESC,#9000000346WAVEDESC
Cmd: C1:WF? DAT2
Size: 2032
Size: 2032
Size: 2032
Size: 2032
Size: 2032
Size: 2032
Size: 1832
Response:
C1:WF DAT2,#9000014000�
```

# Siglent udev rules

This is the rule that made it work for me. Change "tom" to your own user name...

```
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="f4ec", ATTRS{idProduct}=="ee3a", OWNER="tom", MODE="0660"
```

# Update Ubuntu 18.04 to newer kernel

* upgrade to later kernel: https://ubuntu.com/kernel/lifecycle

```
# This is the recommend way to upgrade. But after this, mouse and keyboard didn't work
# anymore
sudo apt-get install --install-recommends linux-generic-hwe-18.04 xserver-xorg-hwe-18.04 
# This solved the mouse and keyboard issue...
sudo apt-get install xserver-xorg-input-all
```

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

Resources:

* [Connection with Python and VXI11](https://siglentna.com/application-note/programming-example-vxi11-python-lan/)
* [VXI-11 Specification](https://www.vxibus.org/specifications.html)
* [Siglent Remote Control Manual](https://siglentna.com/USA_website_2014/Documents/Program_Material/SIGLENT_Digital_Oscilloscopes_Remote%20Control%20Manual.pdf)
* [PyVisa](https://pyvisa.readthedocs.io/en/1.8/index.html)
* [Linux USBTMC Kernel driver 4.19](https://github.com/torvalds/linux/blob/v4.19/drivers/usb/class/usbtmc.c)
* [Linux USBTMC Kernel driver 4.20](https://github.com/torvalds/linux/blob/v4.20/drivers/usb/class/usbtmc.c)
* [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol)



