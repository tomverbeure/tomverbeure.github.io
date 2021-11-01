---
layout: post
title: Correct Timing on a ULPI Interface - Setting the Stage
date:  2021-09-10 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I've been working on getting my own SpinalHDL USB core up and running on an 
[Arrow DECA](/2021/04/23/Arrow-DECA-FPGA-board.html) FPGA board. It's one of 
those half-complete projects that might not ever be finished, so this blog post isn't 
specifically about that. However, I ran into an issue that forced me to learn
some of the finer details of specifying IO timing constraints that I want record for
posterity.

Initially, this was supposed to be just one blog post, but the scope of the whole thing kept on growing.
To keep things manageable, I've split it up into multiple parts.

In this first part, I'll introduce the thing that started it all: the ULPI interface.

# ULPI, a Standard Interface for USB PHYs

Like many other more advanced FPGA boards, the Arrow DECA doesn't have a generic USB
host or device controller[^1], and the MAX10 FPGA itself doesn't have the
IOs to support high-speed 480Mbps USB either:
USB 2.0 requires some specialized digital and analog cells to recover clocks, to support
signalling levels that are radically different between full speed and high speed, to support battery 
charging, to support USB On-The-Go, etc.

[^1]: If you ignore the separate USB device controller that implements a USB Blaster-II.

Just like Ethernet defines a [MAC](https://en.wikipedia.org/wiki/Medium_access_control), 
a [PHY](https://en.wikipedia.org/wiki/PHY), 
and a [media-independent Interface (MII)](https://en.wikipedia.org/wiki/Media-independent_interface) 
between them, the USB consortium created a well-defined cut between a PHY that takes care of the low 
level protocol concerns, and the higher level functionality of device and host controllers. The lower level 
PHY is called the USB 2.0 Transceiver Macrocell (UTM), and the interface between a controller and a UTM is
defined by the [UTMI specification][UTMI-specification].

A UTM PHY can be located on the same silicon die as a controller (chances are high that your cell phone
has one or more UTM cells on its main SOC), but there are also separate chips that just contain a UTM. 
However, instead of using the ~35 IO pins that are required by the UTMI specification, they use the
[UTMI+ Low Pin Interface (ULPI)][ULPI-specification] which requires only 12 IO pins.

The overall system block diagram of such a configuration, which matches the one of the Arrow DECA
board, looks like this:

![System Diagram of USB with UTM interface](/assets/io_timings/io_timings-usb_system_with_ulpi.svg)

The FPGA core logic contains a host or device controller that talks to the external UTM PHY over
standard digital IOs.

A UTM PHY contains a bunch of digital logic that converts between a parallel data stream 
and the serialized USB traffic, as well as PLLs, analog transceivers, voltage regulators, as shown 
in the block diagram of the [TUSB1210 UTM PHY][TUSB1210-product-page] that is used on the Arrow DECA:

![TUSB1210 Block Diagram](/assets/io_timings/tusb1210_block_diagram.png)

The 12 pins of the ULPI interface are at the bottom left of this diagram.

In this series, I won't talk about the high level functionality of USB controllers or the internal logic of
the PHY chip, but about how to ensure reliable communication over the digital ULPI interface.

# ULPI Signals

It's not strictly needed to understand how ULPI communication works, but here's a very short overview
of the different kind of transactions that exist in ULPI land.

The interface has 12 signals that run between the link (the USB controller) and the PHY:

* `ulpi_data[7:0]`: a bidirectional parallel bus to exchange packet data, status information, and 
   register address and data.
* `ulpi_dir`: driven by the PHY, this signal determines who drives the `ulpi_data` bus.
* `ulpi_stp`: driven by the link, this signal signals the end of a transaction by the link.
* `ulpi_nxt`: driven by the PHY, this signals is used to pace data on `ulpi_data` in both directions.

ULPI is a bidirectional interface on which both the link or the PHY can initiate
a transaction. When the interface is idle, the link owns the bus, and always actively drives the 
bidirectional `ulpi_data` bus.

# ULPI TX Commands 

The link has for 4 types of transactions, call "TX Commands". Commands are indicated by the value
of bits `[7:6]` of `ulpi_data`:

* No-op
* Packet transmit
* Register write
* Register read 

**NOOP**

No operation. The link is idle. 

Bits [7:6] of `ulpi_data` are equal to 2'b00.

**Transmit Packet**

The link transmits data bytes to the PHY. 

A transmit is started when bits [7:6] of `ulpi_data` are equal to 2'b01.

![ULPI TXCMD Transmit Waveform](/assets/io_timings/ulpi_txcmd_transmit.png)


**RegWrite**

The link writes an 8-bit value to a register inside the PHY.

A RegWrite is started when bits [7:6] of `ulpi_data` are equal to 2'b10.

![ULPI TXCMD RegWrite Waveform](/assets/io_timings/ulpi_txcmd_regwrite.png)

**RegRead**

The link reads an 8-bit value from a register inside the PHY.

A RegRead is started when bits [7:6] of `ulpi_data` are equal to 2'b11.

![ULPI TXCMD RegRead Waveform](/assets/io_timings/ulpi_txcmd_regread.png)

# ULPI RX Commands and Received Data Bytes

When the PHY wants to send changes in line status information or data bytes from
received packets, it asks for a change in bus direction by asserting `ulpi_dir` and
then sends back mix of status bytes ("RXCMD") or data bytes:

![ULPI RXCMD Data Receive Waveform](/assets/io_timings/ulpi_rxcmd_receive.png)

When there are no more status or data bytes to send, the PHY drops `ulpi_dir`, and the link
gets back ownership of the `ulpi_data`.

While seemingly simple, there are a number of corner cases that need to be dealt with:
how to flag error conditions, how to abort a RegWrite command when the PHY urgently needs to
communicate a change in status, and so forth.

These things are way past the scope of this blog post. You'll just have to read the specification
for the details.

# A Low Level Look at a ULPI Transaction

*I'll be using a register read as an example, but everything discussed here applies to all ULPI transactions.*

A ULPI RegRead transaction has 5 steps:

![ULPI Register Read Specification](/assets/io_timings/ulpi_register_read_specification.png)

1. The link issues a RegRead command on the data bus. It does this by setting
   bits [7:6] of the data bus to 2'b11, and assigning the register address to bits [5:0].
1. The PHY sees the RegRead command, and asserts `nxt` to inform the link.
1. The PHY asserts `dir` to turn around the direction of the data bus and take control of it. However,
   the PHY doesn't drive the data bus yet. Whenever there is a change in direction of the bus, there is an
   idle cycle to give the link time to stop driving the bus. This is called a **bus turn around** cycle.
1. The PHY drives the data value of the requested register on the bus.
1. The PHY deasserts `dir` return control of the data bus to the link, and stops driving
   the data bus. Another bus turn around cycle.


The specification is not explicit about whether or not the PHY can immediately assert `nxt` during step 1.
All it says, in section 3.8.3.1, is the following:

> For a register read, as shown in Figure 22, the Link sends a register read command and waits
> for **nxt** to assert.

However, one could reasonable expect a PHY to assert `nxt` *at the earliest* during the second cycle. If not, 
you'd end up with pretty impressive critical path: 

databus output FF of the link -> databus output IO path of the FPGA -> data bus input IO path of the PHY 
-> a combinatorial path inside the PHY -> `nxt` output IO path of PHY -> `nxt` input IO path of the link
-> FF inside the link.
 
That's just not going to happen at 60 MHz, especially not for an interface that was released 17 years
ago.

# Conceptual Schematic of a Link and PHY Implementation

Taking all of the above into account, here's a conceptual diagram that shows how the IO signals between the Link and PHY 
are almost certainly wired up:

![Overall Setup Without Added Delays](/assets/io_timings/io_timings-overall_setup_no_delays.svg)

Things of note:

* The PHY creates the clock and sends it to the link. This is called ULPI *Output Clock* mode.
  Most PHYs also support the optional *Input Clock* mode, where the link sends a clock to the PHY, 
  but the Arrow DECA board is configured in output clock mode.
* Output signals of either chip, whether it's the link or the PHY, are driven by a flip-flop
  right before going to the IO pin. There is no other logic in between.
* Input signals, on the other hand, typically need to go through some combinatorial cloud
  of logic before they hit a register.
* The `ulpi_dir` signal coming from the PHY directly controls the output enable of the 
  `ulpi_data` IO pins of the link: when `ulpi_dir` is high, the link stops driving `ulpi_data` through
  a combinatorial path.

# Utmi to Ulpi Protocol Adapter 

Most USB controllers have a UTMI interface, so you need a UTMI to ULPI protocol conversion
block that sits between the controller and the IO pins. 
That's my [Utmi2Ulpi](https://github.com/tomverbeure/usb_system/blob/main/spinal/src/main/scala/usb/Utmi2Ulpi.scala)
block.

To test the very basics, I wrote a testbench that implements a behavioral model of a ULPI PHY with the diagram 
above in mind, and ran a simulation of a register read. The signal behavior matches the one of the ULPI specification:

![ULPI Register Read Simulation](/assets/io_timings/ulpi_register_read_simulation_correct.png)

So far so good!

While the other ULPI transactions have been implemented as well, there's no controller logic yet
that exercises those parts, but that's OK: the goal of these blog posts is not the higher
level workings of a USB solution, but practical introduction of getting low level timing
constraints right. And for that, the RTL that's needed for a register read operation already
has all the necessary components to reach the desired complexity:

* an external clock entering the FPGA
* uni-directional control signals going in and out of the chip
* a bi-directional bus
* tri-state buffers for which the output enable is an external input signal

Altogether, this is non-trivial example that will offer plenty of opportunities to learn!

# References

* [USB 2.0 Transceiver Macrocell Interface (UTMI) Specification 1.05][UTMI-specification]
* [UTMI+ Specification Revision 1.0](https://www.nxp.com/docs/en/brochure/UTMI-PLUS-SPECIFICATION.pdf)
* [ULPI Specification][ULPI-specification]
* [Texas Instruments TUSB1210 Product Page][TUSB1210-product-page]

[UTMI-specification]: https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/usb2-transceiver-macrocell-interface-specification.pdf
[ULPI-Specification]: https://www.sparkfun.com/datasheets/Components/SMD/ULPI_v1_1.pdf
[TUSB1210-product-page]: https://www.ti.com/product/TUSB1210
