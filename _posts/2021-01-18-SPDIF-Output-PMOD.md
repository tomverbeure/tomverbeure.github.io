---
layout: post
title: Optical S/PDIF Output PMOD
date:  2021-01-18 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Analog design isn't my strength, so when I do audio experiments with an FPGA, I prefer to
send out the audio signal in digital format. One pretty common format
is [S/PDIF](https://en.wikipedia.org/wiki/S/PDIF). The format supports coaxial cable and
optical fiber as transport medium. I'm using optical because of the coolness factor
(and because it once again doesn't require any analog consideration.)

S/PDIF to analog converters can be found on Amazon for ~$10. 

Optical S/PDIF works fine with pretty much any regular LED on a development board. You don't even 
need a special interface: [@ultraembedded](https://twitter.com/ultraembedded) showed how you
can do this by [holding the optical cable right above the LED](https://twitter.com/ultraembedded/status/1297597288433549313)!

S/PDIF is a pretty simple format and I was able to quickly reproduce that
experiment:

<iframe src="https://player.vimeo.com/video/501886212" width="640" height="360" frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>

But that's obviously not a long term solution.

My [PDM-to-PCM microphone series of blog posts](/2020/12/20/Design-of-a-Multi-Stage-PDM-to-PCM-Decimation-Pipeline.html) 
has moved to the implementation stage, and that means I need something to check the results. I hadn't design 
a PCB in a while, so I sat down one evening to crank out an optical S/PDIF output PMOD.

All PCB and RTL files can be found in [this GitHub repo](https://github.com/tomverbeure/spdif_pmod).

# S/PDIF Optical Output PMOD

This is the result:

![S/PDIF Populatd PCB](/assets/spdif_pmod/spdif_populated_pcb.jpg)

I handsoldered it and it looks terrible, but it works... (Next time, I'll just spinkle around some solder
paste and use a heat gun.)

Plugging in a TOSLINK optical cable is much easier than holding it above an LED!

![S/PDIF System](/assets/spdif_pmod/spdif_system.jpg)

The PMOD has an S/PDIF optical output (TOSLINK) and 4 GPIOs. I've given the GPIO pins the
names of an I2S interface, but since they go straight to the PMOD connector, you can use
them for anything.

The total cost is around ~$30:

* PCB (JLCPCB): $2 + $14 shipping (for 5 PCBs)
* TOSLink connecter: $10
* All the rest: ~$4

# SPDIF Board

The board was designed with [KiCAD](https://kicad.org/).

**Schematic**

![S/PDIF PMOD Schematic](/assets/spdif_pmod/spdif_pmod_schematic.png)

[Schematic in PDF format](https://github.com/tomverbeure/spdif_pmod/tree/main/pcb/pmod_spdif/pmod_spdif.pdf)

**PCB**

![S/PDIF PMOD PCB](/assets/spdif_pmod/spdif_pmod_pcb_front.png)

![S/PDIF PMOD PCB](/assets/spdif_pmod/spdif_pmod_pcb_back.png)

![S/PDIF PMOD PCB 3D](/assets/spdif_pmod/spdif_pmod_3d.png)


**Component list**

![S/PDIF PMOD Components](/assets/spdif_pmod/spdif_pmod_component_list.png)

# Example RTL Design

The PMOD was tested on an [Intel Max10 development board](https://www.intel.com/content/www/us/en/programmable/products/boards_and_kits/dev-kits/altera/max-10-fpga-development-kit.html), 
but it should be trivial to make it work on any FPGA board that has a PMOD connector.

The [RTL](blob/main/fpga/spinal/src/main/scala/spdif/SpdifOut.scala) is written in 
[SpinalHDL](https://spinalhdl.github.io/SpinalDoc-RTD/), which gets converted into Verilog.

There's also a small [testbench](tree/main/fpga/tb/spdif) that uses 
[CXXRTL](https://tomverbeure.github.io/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html) 
to simulate the whole thing. The testbench is not self-checking. You'll need to eyeball the waveforms to verify
that things are working...

The Max10 design uses a PLL to create a 6.144MHz clock out of the 50MHz oscillator clock.

If you don't want to generate the Verilog files yourself, you can find `SpdifTop.v` (the Max10 FPGA
design) and `SpdifOut.v` (the block level module for simulation) [here](https://github.com/tomverbeure/spdif_pmod/blob/main/fpga/spinal/).

# Future Improvements

I rushed this board from intial idea to to gerber-out in a couple of hours, instead of thinking
things through a bit more. 

Two obvious improvements come to mind:

* Add S/PDIF input(s)

    This would allow me to apply audio effects on an input source and send it back out.

* PDM microphone input(s)

    Duh.

That will be for the next iteration.

