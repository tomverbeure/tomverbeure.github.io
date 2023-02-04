---
layout: post
title: Remote Control and Acquisition of Siglent Oscilloscopes
date:  2023-02-03 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my earlier post](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html), 
I gave a general overview about the different protocols that exist to remote
control instrumentation equipment.

My initial goal was to figure out how to download screenshots of my Siglent SDS2304X straight
from the scope to my PC, thus avoiding juggling around a USB stick and having to deal with
non-descriptive screenshot names.

However, after reading up on all of this, I became a bit more ambitious: why download
a screenshot when could just as well download the actualy data for further processing?

# Transport Protocol Support of Siglent Oscilloscopes 

One of the first hurdles in getting to talk to my scope was figuring out which protocol to use.

Siglent scopes support up to 5 different protocols: USBTMC, VXI-11, TCP/IP raw sockets,
TCP/IP telnet, and a web server with HTML-based GUI.

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

I think the general rule is: newer models support more protocols. Mine only supports USBTMC and VXI-11.

*There is also the Siglent SDS3000X, which is a rebranded version of the LeCroy WaveSurfer 3000.*

# Remote Control Information on the Siglent Website

Even if incomplete and not very well organized, the Siglent website has helped me getting 
everything together.

Here's a non-exhaustive list of useful information:

* [Digital Oscilloscopes Programming Guide](https://siglentna.com/wp-content/uploads/2020/04/ProgrammingGuide_PG01-E02C.pdf)

    This document can be found in the 
    [Siglent Digital Oscilloscopes Document Downloads](https://siglentna.com/resources/documents/digital-oscilloscopes)
    section.

    It describes how to connect to your scope, provides a list of all the SCPI commands, 
    and gives a number of programming example. 
    
    All examples are based for Windows and the commercial NI-VISA driver, but the PyVISA examples
    can be used straight on Linux as well.

    The PyVISA examples show you how to download a waveform and plot it on a graph, and
    how to download a screendump.

    The programming guide is not scope specific: it simply assumes that all scopes have support for
    all protocols.

The following articles are all published on the 
[Siglent Application Notes for Digital Oscilloscopes](https://siglentna.com/application-notes/digital-oscilloscopes/):

* [Programming Example: SDS Oscilloscope save a copy of a screen image via Python/PyVISA](https://siglentna.com/application-note/programming-example-sds-oscilloscope-save-a-copy-of-a-screen-image-via-python-pyvisa/)

* [Programming Example: SDS Oscilloscope screen image capture using Python over LAN](https://siglentna.com/application-note/programming-example-sds-oscilloscope-screen-capture-python/)

    Uses straight TCP/IP sockets.

* [Programming Example: Using VXI11 (LXI) and Python for LAN control without sockets](https://siglentna.com/application-note/programming-example-vxi11-python-lan/)

    Uses Python VXI-11 library instead of PyVISA.

* [Programming Example: List connected VISA compatible resources using PyVISA](https://siglentna.com/application-note/programming-example-list-connected-visa-compatible-resources-using-pyvisa/)

* [Programming Example: Retrieve data from an XE series Oscilloscope using Kotlin](https://siglentna.com/application-note/x-e-kotlin-example/)

* [Quick remote computer control using LXI Tools](https://siglentna.com/application-note/lxi-tools/)

* [Verification of a LAN connection using Telnet](https://siglentna.com/application-note/verification-lan-connection-using-telnet/)

* [Verification of a working remote communications connection using NI – MAX](https://siglentna.com/application-note/verification-working-remote-communications-connection-using-ni-max/)

# LXI-Tools

One of the easiest ways to get started with remote controlling VXI-11 compatible equipment is
through [LXI-tools](https://lxi-tools.github.io/).

On my Ubuntu 18.04 system, installing it was as simple as doing:

```
sudo apt install lxi-tools
```

# VXI-11 Device Discovery

VXI-11 has a discovery protocol that allows a device to announce itself to potential clients on the 
Ethernet network. With lxi-tools, that goes as follows:

```
lxi discover
```

If all goes well, this will result in a list of all network connected VXI-11 devices with the IP address,
their name, serial number etc. You can see how that's supposed to go in 
[this video](https://www.youtube.com/watch?v=--gfZcrQ0N8&feature=youtu.be&t=64).

Unfortunately, I never got this to work with my scope: everything is on the same ethernet switch,
the IP subnets between my PC and the scope are the same as well, but no luck.

This is not necessarily a blocking issue when it comes to remote controlling your scope: you just need to
figure out the IP address yourself. But some tools, like `lxi-gui`, the GUI that comes with lxi-tools, 
*only* supports discovery, and no way to specify the IP address manually.

# Setting Up the IP Address of a Siglent Scope

Since I wasn't able to get the VXI-11 discovery to work, I had to set/figure out the IP address of the scope
manually, as follows:

* Connect the scope to your Ethernet network
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

# VXI-11 and PyVISA

[PyVISA](https://pyvisa.readthedocs.io/en/latest/) is probably the easiest way to programmatically remote
control a measurement device, and it has the major benefit that the same code will work with all transport
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

There you have it! The scope returned the brand name, model name, serial number, and the installed firmware version.

# VXI-11 and python-vxi11

PyVISA is easy to use and supports pretty much all interfaces that matter, but it's on the heavy
side in terms of code size. If you're sure that VXI-11 is sufficient for your needs, you can
use the lightweigh [`python-vxi11`](http://alexforencich.com/wiki/en/python-vxi11/start) library.

* Install the `python-vxi11` library

    ```sh
pip3 install python-vxi11
    ```

* Write the following program: `vxi11_ident.py`

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


# VXI-11 and liblxi

If you want to talk to the scope from within a C or C++ program, there's
a library called `liblxi`, the library part of [lxi-tools](https://lxi-tools.github.io/).

I installed `liblxi` from source code to get the latest version, but most distributions have it as a precompiled
package as well: `sudo apt install liblxi-dev`.

Let's first try the `lxi` utility from lxi-tools:
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

# Fetching a Screenshot using VXI-11

Let's now do what I wanted to do all along: fetch a screenshot from the scope to the PC.

The easiest way is to just use `lxi-tools`:

```
> lxi screenshot -a 192.168.1.177
Loaded siglent-sds screenshot plugin
Saved screenshot image to screenshot_192.168.1.177_2020-06-06_21:57:53.bmp
```

# Fetching and Decoding Waveforms

Here's the general procedure to fetch raw waveform data from a Siglent oscilloscope:

* `C1:WF? DESC` / `C1:WAVEFORM? DESC`  

    This query returns the waveform descripter,  a binary data structure of 346 bytes 
    that contains all the parameters that were used to record and encode the data for 
    the latest captured waveform, in this case for channel 1.

    How to you know the format of this data structure?

    Easy! The `TEMPLATE?` query returns 
    an [extensive text file](/assets/siglent/wavedesc_template.txt) 
    describes all bytes in detail. 

    Note how the template started with the following text:

    ```
/00
    000000              WAVEACE:  TEMPLATE
                    8 66 111
;
; Explanation of the formats of waveforms and their descriptors on the^M
; LeCroy Digital Oscilloscopes,
    ```

    LeCroy? 

    Yes! Teledyne LeCroy is rebadging some Siglent products and selling
    it as their own product. Apparently, their cooperation also worked the other
    way around in that Siglent copied some data structures from LeCroy.

* `WFSU` / `WAVEFORM_SETUP` 


    On my SDS2304X, waveforms can be up to 140M sample points. That's way too much to
    transfer in 1 remote control request: some part in the communications stack
    will eventually time out.

    On my scope, the `liblxi` library times out after 25s, which happens when 
    you request a waveform that exceeds 2.8M sample points. But other scopes may
    have slower transfer times and reach the time-out for a lower number of
    sample points.

    The `WAVEFORM_SETUP` makes it possible to retrieve waveform data in multiple
    smaller sections so that the time-out can be avoided.

    Depending on the scope model, `WFSU` has 4 parameters:
    
    * `SP`: sparse point. When set to a value higher than 1, the scope will return ever so
      many points. 
    * `NP`: number of points. The number of points that should be returned.
    * `FP`: first point. The first point to return of a waveform.
    * `SN`: sequence number. XXX needs to be described.

    Let's say you have a waveform with 2M samples. You can fetch this in multiple sections of
    500K samples as follows: 

    ```
WFSU SP,0,NP,500000,FP,0
WF? DAT2
WFSU SP,0,NP,500000,FP,500000
WF? DAT2
WFSU SP,0,NP,500000,FP,1000000
WF? DAT2
WFSU SP,0,NP,500000,FP,1500000
WF? DAT2
    ```

* `C1:WF? DAT2`

    This fetches that actual data.

    After an initial header, each sample is encoded as either an 8-bit signed byte or
    a 16-bit signed word.

    The conversion from this value to the recorded voltage is:

    `voltage = value / 25 * vdiv - ofst`

    `vdiv` and `ofst` can be retrieved either with indivual SCPI queries, or from the waveform descriptor.

* `C1:WF? ALL`

    This combines `WF? DESC` and `WF? DAT2` into one query.
    

# Siglent Issues and Bugs

* Waveform download speed
* Waveform size limitation
* WAVEDESC length bug
* VOLT_DIV bug
* USBTMC hang with older Linux kernels
* 

# Github Repo

https://github.com/tomverbeure/siglent_remote

* [Siglent Remote Control Manual](https://siglentna.com/USA_website_2014/Documents/Program_Material/SIGLENT_Digital_Oscilloscopes_Remote%20Control%20Manual.pdf)
* [PyVisa](https://pyvisa.readthedocs.io/en/1.8/index.html)



