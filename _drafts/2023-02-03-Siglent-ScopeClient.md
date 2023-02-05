---
layout: post
title: LAN/Ethernet Remote Control of Siglent Oscilloscopes
date:  2023-02-03 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

A few years ago, I wrote about the [protocols](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html)
that are used to remote control test and measurement equipment.

The blog post started out as a quest to figure out how to download screenshots of my 
Siglent SDS2304X oscilloscope to my PC, thus avoiding juggling around a USB stick and having to deal with
non-descriptive screenshot names, but things got a bit out of control... 

![Siglent SDS2304X oscilloscope](/assets/siglent/SDS2000Xa.png)

In this blog post, I'm first returning back to the original goal, downloading 
screenshots, after which I'll expand to extracting actual measurement data for further processing.

# Transport Protocols Supported by Siglent Oscilloscopes 

One of the first hurdles in getting to talk to my scope was figuring out which protocol to use.
Siglent offers up to 5 different ways to remote control their scope through either USB
or Ethernet.

USB:

* USBTMC over USB

Ethernet:

* [VXI-11](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html)
* [TCP/IP raw sockets](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html)
* [TCP/IP telnet](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html)
* web server with HTML-based GUI.

However, not all scopes support this full set, and if Siglent has an overview table that 
clearly lists which transport is supported by which product line, I wasn't able to find it. 
After going through the specification sheets of each series, I came up with the 
following table:

| Series        | USBTMC | VXI-11 | Raw Sockets | Telnet | HTTP |
|---------------|:------:|:------:|:-----------:|:------:|:----:|
| [SDS6000A](https://siglentna.com/digital-oscilloscopes/sds6000a-digital-storage-oscilloscope/)                  |    X   |    X   |      X      |    X   |   X  |
| [SDS6000L](https://siglentna.com/digital-oscilloscopes/sds6000l-low-profile-digital-storage-oscilloscope/)      |    X   |    X   |      X      |    X   |   X  |
| [SDS5000X](https://siglentna.com/digital-oscilloscopes/sds5000x/)                                               |    X   |    X   |      X      |    X   |   X  |
| [SDS2000X HD](https://siglentna.com/digital-oscilloscopes/sds2000x-hd-digital-storage-oscilloscope/)            |    X   |    X   |      X      |    X   |   X  |
| [SDS2000X Plus](https://siglentna.com/digital-oscilloscopes/sds2000xp/)                                         |    X   |    X   |      X      |    X   |   X  |
| [SDS2000X-E](https://siglentna.com/digital-oscilloscopes/sds2000x-e/)                                           |    X   |    X   |      X      |    X   |   X  |
| [SDS2000X](https://siglentna.com/digital-oscilloscopes/sds2000x/)                                               |    X   |    X   |             |        |      |
| [SDS1000X/X+](https://siglentna.com/digital-oscilloscopes/sds1000xx-series-super-phosphor-oscilloscopes/)       |    X   |    X   |             |        |      |
| [SDS1000X-E](https://siglentna.com/digital-oscilloscopes/sds1000x-e-series-super-phosphor-oscilloscopes/)       |    X   |    X   |      X      |    X   |   X[^1]  |
| [SDS1000X-U](https://siglentna.com/digital-oscilloscopes/sds1000x-u/)                                           |    X   |    X   |             |        |      |
| [SDS1000CFL](https://siglentna.com/digital-oscilloscopes/sds1000cfl-series-digital-storage-oscilloscopes/)      |    X   |    X   |      ?      |    ?   |      |
| [SDS1000CML+](https://siglentna.com/digital-oscilloscopes/sds1000cml-series-digital-storage-oscilloscopes/)     |    X   |    X   |             |        |      |
| [SDS1000DL+](https://siglentna.com/digital-oscilloscopes/sds1000dl-series-digital-storage-oscilloscopes/)       |    X   |    X   |             |        |      |

[^1]:Only models with 4 channels

The general rule is: newer models support more protocols. Mine only supports USBTMC and VXI-11.

*There is also the Siglent SDS3000X, which is a rebranded version of the LeCroy WaveSurfer 3000.*

The common denominator over Ethernet is support for VXI-11. It's also the only
LAN mode that's supported by my SDS2304X, so everything going forward will deal with that. But
keep in mind that VXI-11 is a synchronous protocol that doesn't allow queuing up multiple requests 
and thus the slowest one.

# Remote Control Information on the Siglent Website

Even if incomplete and not very well organized, the Siglent website has helped me getting 
everything together.

Here's a non-exhaustive list of useful information:

**Manuals**

* [Siglent Digital Oscilloscopes Document Downloads](https://siglentna.com/resources/documents/digital-oscilloscopes)

    This section is your best bet if you're looking for a variety of documents, or if some of the links in this blog
    post have gone stale: Siglent has the annoying behavior of deleting the older version of documents that have been
    updated.

* [SDS Series Digital Oscilloscope Programming Guide](https://siglentna.com/wp-content/uploads/dlm_uploads/2022/07/SDS_ProgrammingGuide_EN11C-2.pdf)

    This link is to one of the latest versions, and it covers most of their latest product lines.
    The programming guide for my SDS2304X is [here](https://siglentna.com/wp-content/uploads/dlm_uploads/2021/01/SDS1000-SeriesSDS2000XSDS2000X-E_ProgrammingGuide_PG01-E02D.pdf).

    The programming guides describes how to connect to your scope, provides a list of all the 
    [SCPI commands](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html#scpi---the-universal-command-language) 
    and gives a number of programming example. All examples are based for Windows and the 
    commercial NI-VISA driver, but the PyVISA examples can be used straight on Linux as well.

    The PyVISA examples show you how to download a waveform and plot it on a graph, and
    how to download a screendump.


**Articles and Application Notes**

The following articles are all published on the 
[Siglent Application Notes for Digital Oscilloscopes](https://siglentna.com/application-notes/digital-oscilloscopes/):

* [Programming Example: SDS Oscilloscope save a copy of a screen image via Python/PyVISA](https://siglentna.com/application-note/programming-example-sds-oscilloscope-save-a-copy-of-a-screen-image-via-python-pyvisa/)

    An example that should work for most Siglent oscilloscope (and other devices too.) It connects
    to the scope with VISA, sends the `SCDP` command, reads the data and stores it to a `.bmp` image
    file.

* [Programming Example: SDS Oscilloscope screen image capture using Python over LAN](https://siglentna.com/application-note/programming-example-sds-oscilloscope-screen-capture-python/)

    This example uses uses straight TCP/IP sockets and will *not* work on oscilloscopes that only
    have VXI-11 support.

* [Programming Example: Using VXI-11 (LXI) and Python for LAN control without sockets](https://siglentna.com/application-note/programming-example-vxi11-python-lan/)

    An example on how to use talk to the oscillscope without PyVISA, but using a straight VXI-11 Python
    library instead. I have a similar example further down.

* [Programming Example: List connected VISA compatible resources using PyVISA](https://siglentna.com/application-note/programming-example-list-connected-visa-compatible-resources-using-pyvisa/)

    Trivial example to shows how to enumerate all the connected instruments using PyVisa. It fails
    to list my oscilloscope when connected through Ethernet though. See below...

* [Programming Example: Retrieve data from an XE series Oscilloscope using Kotlin](https://siglentna.com/application-note/x-e-kotlin-example/)

    This Kotlin example uses raw sockets instead of VXI-11.

* [Quick remote computer control using LXI Tools](https://siglentna.com/application-note/lxi-tools/)

    A pretty extensive overview of what you can do with LXI tools. I cover some of the same
    material furhter down.

* [Verification of a LAN connection using Telnet](https://siglentna.com/application-note/verification-lan-connection-using-telnet/)

    Shows how you can send commands to the scope using telnet. This only works on later Siglent
    oscilloscopes.

* [Verification of a working remote communications connection using NI – MAX](https://siglentna.com/application-note/verification-working-remote-communications-connection-using-ni-max/)

    Only useful if you're on Windows and using National Instruments NI-MAX tool.

# LXI-Tools

One of the easiest ways to get started with remote controlling VXI-11 compatible equipment is
through [LXI-tools](https://lxi-tools.github.io/).

Installing lxi-tools is as simple as doing:

```
sudo apt install lxi-tools
```

lxi-tools comes with `lxi` and `lxi-gui`, a command line and a GUI utility that can send commands to 
and grab screenshots from your instrument. It also has a LUA scripting option that I haven't
explored.

# VXI-11 Device Discovery

VXI-11 has a discovery protocol that allows a device to announce itself to potential clients on the 
Ethernet network. With lxi-tools, that goes as follows:

```
lxi discover
```

If all goes well, this will result in a list of all network-connected VXI-11 devices with the IP address,
their name, serial number etc. You can see how that's supposed to work in 
[this video](https://www.youtube.com/watch?v=--gfZcrQ0N8&feature=youtu.be&t=64).

Unfortunately, I never got this to work with my scope: everything is on the same ethernet switch,
the IP subnets between my PC and the scope are the same as well, but no luck.

This is not a blocking issue when it comes to remote controlling your scope: you just need to
figure out the IP address yourself. But `lxi-gui` *only* supports discovery with no way to specify the 
IP address manually.

# Setting Up the IP Address of a Siglent Scope

Since I wasn't able to get the VXI-11 discovery to work, I had to set/figure out the IP address of the scope
manually, as follows:

* Connect the scope to your LAN with an Ethernet cable
* Press [Utility] -> [I/O] *(Page 2/3)* -> [LAN]

![LAN setup](/assets/siglent/lan_setup.png)

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

# Grabbing Screenshots with lxi-tools

If all you ever need are screenshots, then `lxi screenshot -a <IP address>` is
the way to go:

```sh
tom@zen$ lxi screenshot -a 192.168.1.177
Loaded siglent-sds screenshot plugin
Saved screenshot image to screenshot_192.168.1.177_2023-02-04_15:36:43.bmp
```
![Screenshot with 1kHz waveform](/assets/siglent/screenshot_1kHz.png)

Note the `Loaded siglent-sds screenshot plugin` message: lxi-tools supports
only a [limited number of instruments](https://github.com/lxi-tools/lxi-tools#5-tested-instruments). 
Since Siglent oscilloscopes share the same core SCPI commands across the full
product line, you'd think that screenshots would be supported for all, but
a quick look at the 
[source code](https://github.com/lxi-tools/lxi-tools/blob/37eda6c12f00e94582f4a9271d93f5372ca2c7f3/src/plugins/screenshot_siglent-sds.c#L94)
shows that the tool only supports scopes with an ID that match the following regular expression: 

```c
// Screenshot plugin configuration
struct screenshot_plugin siglent_sds =
{
    .name = "siglent-sds",
    .description = "Siglent SDS 1000X/2000X series oscilloscope",
    .regex = "SIGLENT TECHNOLOGIES Siglent Technologies SDS[12]...",    <<<<
    .screenshot = siglent_sds_screenshot
};
```

# Sending SCPI Commands with lxi-tools

The same `lxi` command can be used to send commands to the scope:

```sh
$ lxi scpi -a 192.168.1.177 "*IDN?"
*IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
```

`*IDN?` is *the* standard command to request identification data from an instrument. It predates
the SCPI standard by a decade or two and will work on pretty much all remote controllable instruments
in existence.

With the Siglent programming manual in hand, you can now set or get configuration
parameters, kick off a single measurement and so forth. 

For example, `ASET` is the same pressing the Auto Setup button:

```sh
$ lxi scpi -a 192.168.1.177 "ASET"
```

And `BWL?` will tell you wether or not BW Limit option has been enabled for each of the
4 channels:

```sh
$ lxi scpi -a 192.168.1.177 "BWL?"
BWL C1,OFF,C2,OFF,C3,ON,C4,ON
```

# Controlling the Oscilloscope with Code

Using lxi-tools is good enough when you want to throw together a bunch of commands in a bash script, 
but you may want to integrate scope commands in a larger script or program that sets up a
configuration, triggers a data acquistions, and fetches the data for post processing.



# VXI-11 and PyVISA

[PyVISA](https://pyvisa.readthedocs.io/en/latest/) is probably the easiest way to programmatically remote
control a measurement device, and it has the major benefit that the same code will work with all transport
protocols that are supported by your scope. I already wrote who to install and use
it [here](http://localhost:4000/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html#visa---one-api-that-rules-them-all).

The following program, `visa_ident.py`, prints out the identification
number of the scope:

```python
#! /usr/bin/env python3
import sys
import pyvisa

rm = pyvisa.ResourceManager()
siglent = rm.open_resource(f"TCPIP::{sys.argv[1]}")
print(siglent.query('*IDN?'))
```

```sh
./visa_ident.py 192.168.1.177
*IDN SIGLENT,SDS2304X,xxxxxxxxxxxxxx,1.2.2.2 R19
```

# VXI-11 and python-vxi11

PyVISA is easy to use and supports pretty much all interfaces that matter, but it's on the heavy
side in terms of code size. If you're sure that VXI-11 is sufficient for your needs, you can
use the lightweight [`python-vxi11`](http://alexforencich.com/wiki/en/python-vxi11/start) library.

Install the `python-vxi11` library:

```sh
pip3 install python-vxi11
```

Write the following program: `vxi11_ident.py`

```python
#! /usr/bin/env python3
import sys
import vxi11

instr = vxi11.Instrument(sys.argv[1])
print(instr.ask("*IDN?"))
```

```sh
$ ./vxi11_ident.py 192.168.1.177
*IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
```

# VXI-11 and C code with liblxi

If you want to talk to the scope from within a C or C++ program, there's
a library called `liblxi`, the library part of [lxi-tools](https://lxi-tools.github.io/).

I installed `liblxi` from source code to get the latest version, but most distributions have it as a precompiled
package as well: 

`sudo apt install liblxi-dev`.

Using the library in a C program is straightforward as well:

```c
#include <stdio.h>
#include <string.h>
#include <lxi.h>

int main(int argc, char **argv)
{
     char response[65536];
     int device, length, timeout = 1000;
     char *command = "*IDN?";

     lxi_init();
     device = lxi_connect(argv[1], 0, "inst0", timeout, VXI11);
     lxi_send(device, command, strlen(command), timeout);
     lxi_receive(device, response, sizeof(response), timeout);
     printf("%s\n", response);
     lxi_disconnect(device);
}
```

```sh
$ gcc -o lxi_idn lxi_idn.c -llxi
$ ./lxi_idn 192.168.1.177 
*IDN SIGLENT,SDS2304X,SDS2XJBD1R2754,1.2.2.2 R19
```

# Fetching and Decoding Waveforms

Here's the general procedure to fetch raw waveform data from a Siglent oscilloscope:

* `C1:WF? DESC` / `C1:WAVEFORM? DESC`  

    This query returns the waveform descriptor,  a binary data structure of 346 bytes 
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


# Footnotes
