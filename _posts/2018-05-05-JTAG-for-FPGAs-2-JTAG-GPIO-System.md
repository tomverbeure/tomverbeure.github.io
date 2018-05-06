---
layout: post
title:  "JTAG for FPGAs - Part 2: JTAG_GPIO in a System"
date:   2018-05-05 22:00:00 -0700
categories: JTAG
---

# Introduction 

In part 1 of this series, we looked at the details of the JTAG\_GPIO block, a block that makes it possible to
control and observe signals in a digital (FPGA) design.

In this part, we're looking at integrating this block in an actual design.

All code of this project can be found in [this](https://github.com/tomverbeure/jtag_gpios) GitHub repo.

# The Example Design

In our example design, we're doing the most boring thing possible: use the GPIO outputs to control LEDs and the GPIO inputs to
check that status of a button. Yeah...

The hierarchy of the design is as follows:

```
   top
        jtag_top
            jtag_tap_generic
            jtag_gpios
            <some JTAG related glue logic>
        <some very minor glue logic>

```

The `jtag_tap_generic` block has been derived from that JTAG TAP controller from the OpenRisc project. 

The `jtag_gpios` block takes in already decoded JTAG TAP states, as well as decoded instructions. This makes the
JTAG side of its interface very generic: it can be connected to a regular JTAG TAP (as we do here), but we can
also connect it something difference.

For example, in `jtag_top`, you'll see that two kinds of TAP are instantiated: the generic one, as well as an
Altera Virtual JTAG TAP. (Altera chip already have a JTAG port and TAP. Their virtual JTAG architecture make it
possible for third party designers, like us, to make use of that. This will be discussed in some later article.)

The glue logic in the `jtag_top` block does some custom decoding to link the TAP to the JTAG\_GPIO block. It decodes
the instructions register, it also provides a bypass register to cover the case where an undefined instruction
has been scanned in.

Finally, the top links the GPIO pins to the LEDs and button.
