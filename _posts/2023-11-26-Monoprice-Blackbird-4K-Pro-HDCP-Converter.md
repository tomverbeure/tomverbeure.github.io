---
layout: post
title: Analyzing the Monoprice Blackbird HDCP 2.2 to 1.4 Down Converter
date:  2023-11-26 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I got my hands on a 
[Monoprice Blackbird 4K Pro HDCP 2.2 to 1.4 Converter](https://www.monoprice.com/product?p_id=15242).
According to the marketing copy it "is the definitive solution for playback of new 4K HDCP 2.2 encoded 
content on 4K displays with the old HDCP 1.4 standard."

Stuffed after a delicious Thanksgiving meal, I decided to take it apart after the guests had left. It's
a simple single-function device, so I didn't expect much, but maybe there's some things to be learned?

# Some Words about HDCP

If you want a cryptographically secure system, there's nothing worse than creating your own custom protocol
instead of proven one, but that's exactly what happened in the case of 
[High-Bandwidth Digital Content Protection](https://en.wikipedia.org/wiki/High-bandwidth_Digital_Content_Protection) (HDCP).

Version 1 was developed somewhere at the beginning of the century and turned out to be terribly broken.
By 2010, it was completely defeated with the release of the 
[master key](https://github.com/rjw57/hdcp-genkey/blob/master/master-key.txt)[^1] that can be used to 
generate transmit and receive keys at will.

To keep Hollywood happy, a succesor was invented: HDCP 2.0, an entirely new protocol with no similarities 
to revision 1.  This time, the creators decided to use proven cryptography algorithms such as public key
authentication, and 128-bit AES encryption. HDCP 2.1 added the concept of content stream types **to block the 
retransmition of high quality video streams** (e.g. 4K or HDR).

Despite using known-good core algorithms, there was still 
[a major issue](https://blog.cryptographyengineering.com/2012/08/27/reposted-cryptanalysis-of-hdcp-v2/)
in the way certain data was exchanged between transmitter and receiver, necessitating a 2.2 revision
that wasn't backward compatible with versions 2.0 and 2.1. There's an HDCP version 2.3 now, but
it's not reallly clear if there are any real-world consequences...

Today, all new TVs support both HDCP 2 and HDCP 1 so that legacy HDCP 1-only sources such as DVD players 
are still supported. Similarly, most HDCP 2 sources will fall back to HDCP 1 when dealing with older
TVs that don't have HDCP 2 support.

There's a major issue however: remember how HDCP 2.1 added content stream types? There are currently only 2 of
them: type 0 and type 1, where type 1 is considered high value. It's up to a content provider to decide 
whether a video stream gets tagged as such. In the case of Netflix, UHD (4K) or HDR content is classified as 
type 1 while traditional HD content (720p and 1080p non-HDR) is type 0. On Amazon Prime, 1080p HDR content
is classified as type 0 content, but UHD, with our without HDR, is classified as type 1.

So if you have a 4K display that only supports HDCP 1, you're out of luck: Netflix and Amazon will only serve
1080p streams. The issue can't be solved with repeaters such as home theater video receivers, because 
the HDCP specification prohibits retransmision of type 1 content. 

And yet, the Monoprice Blackbird claims to do HDPC 2 to HDCP 1 downconversion just fine. Maybe it only supports 
type 0 content, making it technically HDCP 2 compliant even if it doesn't supports only a fraction of the available 
content? 

# Inside the Monoprice Blackbird 4K Pro

The outside of the Blackbird is forgettable, with the kind of black metal case that's used by most
protocol conversion boxes.

![Top view](/assets/hdcp_converter/top_view.jpg)

![Bottom view](/assets/hdcp_converter/bottom_view.jpg)

After removing the top cover, you're greeted with the following:

[![Inside view - annotated](/assets/hdcp_converter/inside_view annotated.jpg)](/assets/hdcp_converter/inside_view annotated.jpg)
*(Click to enlarge)*

The design is straightforward: a main conversion IC, an SPI flash memory, a microcontroller, 
and a bunch of jellybean components to create power rails.

Let's look at the main actors:

* Silicon Image Sil9679CNUC 

    Google has quite a bit of hits for this product, but they're all articles from way back when HDCP 2.2
    capable TV silicon was rare. Apparently, this chip was the very first one that allowed televsion 
    manufacturers to add support for HDCP 2.2 to their 4K TVs. It only supports the YUV 4:2:0 color format,
    but that's sufficient for most TV content.

    A few years ago, Silicon Image was acquired by Lattice Semiconductor, so the Sil9679 is now listed on the Lattice 
    [TV HDMI / MHL Receivers product page](https://www.latticesemi.com/en/Products/ASSPs/TVHDMIMHLReceivers):

    [![Lattice Product Page](/assets/hdcp_converter/lattice_product_page.png)](/assets/hdcp_converter/lattice_product_page.png)
    *(Click to enlarge)*

    But there's no datasheet to be found.

    BTW, notice how the table above lists HDMI 2.0 support. Most people associate HDMI 2.0 with full quality 4K 60Hz
    support, which requires a cable bandwidth above the limit of HDMI 1.4. 4K 60Hz in  YUV 4:2:0 mode, however,
    fits nicely within the capabilities of HDMI 1.4. It's a mystery why the table claims HDMI 2.0 capabilities...[^2]

    A Google search for "Sil9679 datasheet" turns up a 
    [datasheet for the Sil9678](https://datasheet.lcsc.com/lcsc/1912111437_Lattice-SiI9678CNUC_C369587.pdf) 
    on LCSC. It's a different product that does exactly the opposite: convert from HDCP 1.4 to HDCP 2.2, but
    it has the same packages and after close examination of the PCB, the pinout seems identical at well.

    Chances are high that the Sil9678 and Sil9679 use the same silicon with different functions 
    fused off...

* STMicroelectronics STM8S005K6T6C Microcontroller

    No secrets here: the [datasheet](/assets/hdcp_converter/stm8s005c6.pdf) is readily available.

    This member of the [STM8 series](https://en.wikipedia.org/wiki/STM8) has an 8-bit CPU, 32KB of flash memory, 
    2KB of RAM, and the usual assortment of timers, UART, I2C, and SPI interfaces. It's just what you need for 
    some simple configuration and control of another chip.

* Console Connector J1

    You can visually trace the PCB traces from connector J1 to the STM8 controller: 2 pins are connected
    to its UART interface. We're definitely going to have a closer look at that.

* Debug Connector J2

    The second pin of connector J2 is connected to the SWIM pin of the STM8. SWIM is short for
    [Single Wire Interface Module](http://kuku.eu.org/?projects/stm8spi/stm8spi#mcb_toc_head1). 
    It's a single-pin alternative of the more common JTAG interface.

# The Test

To test whether or not the HDCP converter works, I did a couple of experiments.

The equipment:

* an Amazon Fire TV Stick 4K
* a 15 year old Samsung TV, 1080p, no HDR, HDCP1 only
* a 5 year old Monoprice 4K 32" monitor, HDR support (terrible quality),  HDCP1 only
* the Monoprice HDCP 2 to HDCP 1 converter

For content, I picked a random Amazon Prime show with UHD/4K and HDR10+ support: 
*Z, the Beginning of Everything*.

**Samsung 1080p TV, Fire TV Stick, no converter**

The first test counts as a base line. With the Fire TV plugged in straight into the 
old TV, I wanted to see whether or not there'd be a visual indication that the Fire TV was
playing lower quality content.

![Player HD 1080p](/assets/hdcp_converter/player_hd1080p.jpg)

This was indeed the case. While the content browing screen indicated support for UHD
and HDR10+, pressing pause during playing showed "HD 1080p". 

**MonoPrice 4K monitor, Fire TV Stick, no converter**

For the next step, I plugged the Fire TV directly into my 4K monitor. Since the monitor
doesn't support HDCP 2, I expected lower quality playback than 4K/HDR, and that's what I got.
This time, the player showed "HD 1080p HDR".

![Player HD 1080p HDR](/assets/hdcp_converter/player_hd1080p_hdr.jpg)

**MonoPrice 4K monitor, Fire TV Stick, with HDCP converter**

The final test puts the HDCP converter between the Fire TV and the monitor. If the converter
does its job, I should be seeing 4K with HDR enabled.

![Player UHD HDR](/assets/hdcp_converter/player_uhd_hdr.jpg)

And it does! The player now shows "Ultra HD HDR".

As an intermediate conclusion, we can agree that the HDCP converter is definitely doing
something that makes the Fire TV believe that it's dealing with something better than an 
old HDCP1 enabled display.

But what is it doing exactly? 

# Digging Deeper: UART Transactions

Let's dig deeper. The obvious second step is to wire up the UART pins of the
microcontroller and see if there's anything interesting to see there.

![UART connected](/assets/hdcp_converter/uart_connected.jpg)

I used a USB to serial converter to capture UART traffic with a 115200 bit rate.

The TX port of the UART is chatty whenever there is some major event: booting up,
plugging an HDMI cable in or out, or going to sleep. I typed a bunch of commands back
to the device, but was not able to get a response of out it.

**Booting Up**

The message after plugging in the power cable:

```
        Copyright Silicon Image Inc, 2013
        Build Time: Aug 31 2015-14:50:30

        Host Software Version: 01.02.02
        Adapter Driver Version: 01.00.11
        Require FW version: 02.02.xx

Waiting Boot Done  ....
Booting is done successfully.

Chip ID: 0x9679
Firmware Version: 01.02.06
***Error: Chip FW Version not match.
```

**Plugging in the sink**

When I plug in the output HDMI cable to connect the monitor
to the converter, it sends out this:

```
Downstream Connect Status Changed:
   Link Type is: HDMI/DVI

Tx HDCP  Version:
   HDCP version is: 1.x

Tx HDCP Status Changed:
   Tx HDCP Authentication Off.

Rx HDCP  Version:
   HDCP version not support

Rx HDCP Status Changed:
   Rx HDCP Authentication Off.


Edid Status: Avaliable
Edid Block 0 Data:
00 ff ff ff ff ff ff 00 24 62 00 32 01 01 01 01 
10 1c 01 03 80 47 28 78 3e 64 35 a5 54 4f 9e 27 
12 50 54 bf ef 80 d1 c0 b3 00 a9 c0 95 00 90 40 
81 80 81 40 81 c0 40 d0 00 a0 f0 70 3e 80 30 20 
35 00 54 4f 21 00 00 1a b4 66 00 a0 f0 70 1f 80 
30 20 35 00 80 88 42 00 00 1a 00 00 00 fc 00 48 
44 4d 49 32 0a 20 20 20 20 20 20 20 00 00 00 fd 
00 18 90 0f de 3c 00 0a 20 20 20 20 20 20 01 30 
Edid Block 1 Data:
02 03 4f f2 5e 04 05 10 13 14 1f 20 21 22 27 48 
49 4a 4b 4c 5d 5e 5f 60 61 62 63 64 65 66 67 68 
69 6a 6b e2 00 c0 e3 05 c0 00 23 09 7f 07 83 01 
00 00 e5 0f 00 00 0c 00 67 03 0c 00 10 00 38 78 
67 d8 5d c4 01 78 88 01 e6 06 05 01 69 69 4f 02 
3a 80 18 71 38 2d 40 58 2c 25 00 55 50 21 00 00 
1e 69 5e 00 a0 a0 a0 29 50 30 20 35 00 00 b0 31 
00 00 1e 00 00 00 00 00 00 00 00 00 00 00 00 df 
```

We can see how it doesn't go through HDCP authentication yet, but it waits
for the source on the input HDMI port.

The EDID data contains all the information about the connected monitor: supported
resolutions and refresh rates, colometry information, audio modes and so forth. 
After removing the "Edid Block 1 Data", you can paste these hex values straight into 
[an online EDID parser](http://www.edidreader.com) to extract all the 
EDID information in a readable format.

![EDID parser screenshot](/assets/hdcp_converter/EDID_parser.png)

The converter needs this EDID data so that it can pass it on to the upstream
source device on its input port.

**Plugging in the source**

Most important is what happens when plugging in the source:

```
Upstream Connect Status Changed:
   Link Type is: HDMI/DVI


Sync Detect: ON

Clock Detect: ON


Rx HDCP  Version:
   HDCP version is: 2.2

Rx HDCP Status Changed:
   Rx HDCP Authenticating...

AV Mute Status Changed:
   AV Mute ON

Tx HDCP  Version:
   HDCP version is: 1.x

Tx HDCP Status Changed:
   Tx HDCP Authenticating...

Rx HDCP  Version:
   HDCP version is: 2.2

Rx HDCP Status Changed:
   Rx HDCP Authenticating...


AV Mute Status Changed:
   AV Mute OFF

Tx HDCP  Version:
   HDCP version is: 1.x

Tx HDCP Status Changed:
   Tx HDCP Authentication Done.

Rx HDCP  Version:
   HDCP version is: 2.2

Rx HDCP Status Changed:
   Rx HDCP Authenticating...


Rx HDCP  Version:
   HDCP version is: 2.2

Rx HDCP Status Changed:
   Rx HDCP Authentication Done.
```

We can see how the input/RX and the output/TX port go through
an HDCP2 and HDCP1 authentication respectively.

Unfortunately, the console log still doesn't tell us whether or not the HDCP2
authentcation is for type 0 or type 1 content.

# Decoding HDCP I2C Transactions

To really know what's going on, we need to observe the control traffic that runs
over the [Display Data Channel (DDC)](https://en.wikipedia.org/wiki/Display_Data_Channel) of
the HDMI cable. DDC uses the standard [I2C protocol](https://en.wikipedia.org/wiki/I²C) that
can be decoded by any self-respecting logic analyzer or oscilloscope.

The SCL and SDA signals of the DDC channel are present on pins 15 and 16 of the HDMI connector. 

![SDA and SCL pins on the PCB](/assets/hdcp_converter/inside_view_ddc.jpg)

It takes a bit of patience, a steady hand, and, in my case, a microscope to solder two
tiny wires to those pins, but it's totally doable with a fine tipped soldering iron. Once in 
place, you can capture the I2C transactions with a logic analyzer such as a Saleae or DSLogic
for further analysis:

![I2C Capture](/assets/hdcp_converter/i2c_capture.png)

There are multiple I2C devices on the DDC bus:

* EDID: address 0x50 

    This contains the EDID information that we saw earlier on the console log. On many older
    monitors there's literally an I2C PROM soldered onto the wire. Newer monitors handle EDID
    I2C requests with an I2C device controller in the scaler chip.

* SCDC: address 0x54

    The Status and Control Data Channel was introduced for HDMI 2.0. For earlier versions, 
    data transmission over the high-speed HDMI links was a pure one-way fire-and-forget
    affair. HDMI 2.0 added status registers to observe link quality and control registers to 
    control clock to data ratio, enable or disable scrambling operation and so forth.

    The HDMI converter only supports HDMI 1.4, so you can expect to source requests to
    address 0x54 to result in an I2C NAK (not-acknowledged) response.

* HDCP: 0x3A

    This address is used for read and write access to various HDCP registers that are used
    to exchange authentication and status information.

**I2C Transactions**

Let's walk through the key I2C transactions of the recorded trace.

Initially, nothing is connected, and the sink, the HDCP converter in this case, doesn't respond:

```
// HDCP... Nothing connected
write to 0x3A nak
...
write to 0x3A nak
```

Next, the source reads the EDID information:

```
// Read EDID Page 0
write to 0x50 ack data: 0x00 
read to 0x50 ack data: 0x00 0xFF 0xFF 0xFF 0xFF 0xFF 0xFF 0x00 ...
// Read EDID Page 1
write to 0x50 ack data: 0x80 
read to 0x50 ack data: 0x02 0x03 0x4F 0xF2 0x5E 0x04 0x05 0x10 ...
```

The source then checks if it's dealing with an HDMI 2.0 sink. It is not,
so the access results in a NAK:

```
// SCDC
write to 0x54 nak
```

The source is now ready to enable HDCP protection. HDCP documents can be found
on the [HDCP Specifications](https://www.digital-cp.com/hdcp-specifications) page
of the Digital Content Protection consortium.

There are specifications that describe the general principles, such as the
*HDCP Specification Rev. 2.2 Interface Independent Adaptation*, as well as
specifications with interface specific implementation details, such as the
*HDCP 2.3 on HDMI Specification*. We can use the latter to decode the
meaning of the I2C transactions. Section 2.14 *HDCP Port* shows all the
supported I2C registers.

First, the source checks the HDCP2Version register. Bit 2 of register 0x50 indicates
that HDCP2 is supported.

```
// HDCP HDCP2Version 
write to 0x3A ack data: 0x50 
// Supports HDCP2.2 or higher
read to 0x3A ack data: 0x04
```

This is then followed by the actual cryptographic exchange sequence.

The source indicates that it wants an HDCP2 authentication:

```
// HDCP Write_Message: msg_id=0x02 AKE_Init, Data len=11
// Last 3 bytes: 0x02 0x00 0x00 -> HDCP transmitter version = 0x02
write to 0x3A ack data: 0x60 0x02 0xBB 0xDA 0x14 0x6B 0x44 0xFB 0x1A 0x0C 0x02 0x00 0x00 
```

This results in the sink returning a message that is 534 bytes long. It contains the
monitor's authentication certificate, a public key, but also whether or not the sink is
a final terminal or a repeater:

```
// HDCP RxStatus
write to 0x3A ack data: 0x70 
// Message length 0x216/534
read to 0x3A ack data: 0x16 0x02

// HDCP Read_Message
write to 0x3A ack data: 0x80 
// Read 534 bytes: msg_id=0x03 AKE_Send_Cert
// Last 3 bytes: 0x02 0x00 0x00 -> RxCaps: receiver version 0x02, REPEATER=0 (!)
read to 0x3A ack data: 0x03 0xF1 0x60 0xD1 0x6B ...  0x02 0x00 0x00
```

The sink indicates that it is NOT a repeater. This is the information I was looking for: repeaters have 
strict rules about how to deal different types of content and are NOT allowed to forward 
type 1 content. 

![StreamID Table](/assets/hdcp_converter/streamID_table.png)

The HDCP converter simply announces itself as a final video endpoint... yet still repeats the
content to its output port. Without a very expensive HDMI protocol analyzer, we can't
check if the source is tagging the content as type 0 or type 1, but there is no reason now
to think that it's not type 1.

The rest of the I2C trace follows the HDCP specification authentication playbook, but doesn't
provide any more clues about the content type.

The trace ends with the source polling the sink at regular interval to make sure the HDCP link is still active:

```
// HDCP RxStatus
write to 0x3A ack data: 0x70 
read to 0x3A ack data: 0x00 0x00

write to 0x3A ack data: 0x70 
read to 0x3A ack data: 0x00 0x00
...
```

# The Legality of It All

All of this made me question the legality of all this.  Monoprice sells cheap products, but it's not a 
shady bottom feeder. After a bit of Googling around, I found
[the following article](https://torrentfreak.com/4k-content-protection-stripper-beats-warner-bros-in-court-1605xx/).

There has been a lawsuit about this kind of down-converter, but the case was settled. Here's the money 
quote:

> In its reply, LegendSky explained that their devices do not “strip” any HDCP copy protection. 
> Instead, the contested HDFury device merely downgrades the higher HDCP protection to a lower 
> version, which is permitted as an exception under the DMCA.

And that's the end of the story: the converters work, they're passing through type 1 contents, and
there's nothing the movie studios can do about it. It's all good.

# References

* [HDCP Specifications](https://www.digital-cp.com/hdcp-specifications)
* [A Cryptanalysis of the High-bandwidth Digital Content Protection System](https://cypherpunks.ca/~iang/pubs/hdcp-drm01.pdf)
* [A cryptanalysis of HDCP v2.1](https://blog.cryptographyengineering.com/2012/08/27/reposted-cryptanalysis-of-hdcp-v2/)
* [hdcp-genkey](https://github.com/rjw57/hdcp-genkey)

# Footnotes

[^1]: It wasn't necessary for someone in-the-know to leak the master key: the protocol was so flawed
      that the master key can be derived using the technique described in 
      "A Cryptanalysis of the High-bandwidth Digital Content Protection System" by Crosby, et al.

[^2]: You can the bandwidth requirements with my [video timings calculator](https://tomverbeure.github.io/video_timings_calculator).
      Just chose 4K/60 in the predefined mode selection box, and toggle between the RGB 4:4:4 or YUV 4:2:0 color formats.
      You'll see how RGB 4:4:4 requires HDMI 2.0 while YUV 4:2:0 works with HDMI 1.4.

      ![Video Timings Calculator](/assets/hdcp_converter/video_timings_calculator.png)
