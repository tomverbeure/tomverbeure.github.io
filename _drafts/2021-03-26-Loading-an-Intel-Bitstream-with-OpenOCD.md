---
layout: post
title: Loading an Intel Bitstream with OpenOCD
date:  2021-03-26 00:00:00 -1000
categories:
---

*Executive summary: loading a volatile bitstream with OpenOCD into the FPGA works fine. But on my Cyclone II FPGA,
programming the flash, only worked when the flash was empty.*

* TOC
{:toc}

# Introduction

The 2 most common operations when dealing with FPGA bitstreams are: 

* loading the bitstream straight into the FPGA, without programming the FPGA flash

    This is voltatile operation: after a power cycle, the FPGA contents are lost. This is a
    common operation during debugging.

* programming a bitstream into the FPGA-connected flash

    This is obviously a non-volatile operation. After an FPGA power cycle, the FPGA will
    load the bitstream from the connected flash and start operating as it should.

When using Intel FPGA, the tool of choice is Quartus Programmer. 

Quartus Programmer expects an Intel JTAG dongle: a piece of hardware that sits between your PC and the FPGA, with
a JTAG interface on the FPGA side. 

Many development boards have USB Blaster logic on the board itself, so all you need is a USB cable. But for those
that don't, Intel has the USB Blaster and USB Blaster 2, the EthernetBlaster and EthernetBlaster 2. 

Because these things are unreasonably expensive, there's a whole industry of USB Blaster clones. The cheapest ones
can be found for next to nothing on AliExpress, I got mine for $3, but the 
[quality is terrible](/2018/04/18/Terasic-vs-Cheap-Clone-USB-Blaster.html). A high quality one from Terasic is $50, 
and good no-name clones go for around $25.

But what if you already have a JTAG dongle. Maybe you have a Digilent JTAG SMT2 programming cable (or clone) for 
your Xilinx boards? Or you created a JTAG programming cable yourself by flashing an STM32-based Blue Pill with 
[Versaloon firmware](https://github.com/zoobab/versaloon)?

For those cases, it's possible to load the bitstream directly into the FPGA by using OpenOCD. Programming the 
FPGA flash, however, didn't universally work.

# Serial Vector Format (SVF), a Standard JTAG File Protocol

The method describe in [Loading a Xilinx Spartan 6 bitstream with OpenOCD](/2019/09/15/Loading-a-Spartan-6-bitstream-with-openocd.html), 
doesn't quite work for Intel FPGAs because OpenOCD doesn't have direct support for the native Intel bitstream format, but 
OpenOCD has generic support for SVF files.

An SVF file contains commands that describe how JTAG pins must be toggled, and, what kind of return data is expected 
on the TDO pin. It's a pretty primitive text based format that executes linearly start to finish, but that's good enough 
for our needs.

You don't have to understand the contents of an SVF file, but here's an example of what an SVF file looks like:

```
FREQUENCY 6.00E+06 HZ;

TRST ABSENT;
ENDDR IDLE;
ENDIR IRPAUSE;
STATE IDLE;
SIR 10 TDI (002);
RUNTEST IDLE 6000 TCK ENDSTATE IDLE;
SDR 1265648 TDI (0100AE14...) TDO(045CCEFA...) 
SIR 10 TDI (003);
RUNTEST 30 TCK;
RUNTEST 512 TCK;
SIR 10 TDI (3FF);
RUNTEST 6000 TCK;
STATE IDLE;
```

The cool thing is that Quartus Programmer supports exporting all the operations to program a bitstream as an
SVF file!

So with just the right mouse clicks and keyboard taps, you can load the bitstream of your Intel FPGA without
needing an Intel compatible JTAG dongle.

# Connecting to Your FPGA with OpenOCD

The first step is to get OpenOCD to talk to your FPGA. 

* Connect the JTAG pins of your JTAG dongle to the FPGA
* Plug in the JTAG dongle in your PC
* Use the instructions from [the Xilinx blog post](/2019/09/15/Loading-a-Spartan-6-bitstream-with-openocd.html)
  to find the right OpenOCD driver, and detect the FPGA JTAG port

Going a bit against the whole spirit of using something else than a USB Blaster, I used a USB Blaster to connect 
OpenOCD to the FPGA...

My recipe was as follows:

```sh
sudo /opt/openocd/bin/openocd \ 
    -f /opt/openocd/share/openocd/scripts/interface/altera-usb-blaster.cfg 
    -c "adapter_khz 6000" 
```

This is the result:

```
Open On-Chip Debugger 0.10.0+dev-00930-g09eb941 (2019-09-16-21:01)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : only one transport option; autoselect 'jtag'
adapter speed: 6000 kHz

Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : usb blaster interface using libftdi
Info : This adapter doesn't support configurable speed
Warn : There are no enabled taps.  AUTO PROBING MIGHT NOT WORK!!
Info : JTAG tap: auto0.tap tap/device found: 0x020b10dd (mfg: 0x06e (Altera), part: 0x20b1, ver: 0x0)
Warn : AUTO auto0.tap - use "jtag newtap auto0 tap -irlen 2 -expected-id 0x020b10dd"
Error: IR capture error at bit 2, saw 0x3FFFFFFFFFFFFD55 not 0x...3
Warn : Bypassing JTAG setup events due to errors
Warn : gdb services need one or more targets defined
```

The most important line is this:
```
Info : JTAG tap: auto0.tap tap/device found: 0x020b10dd (mfg: 0x06e (Altera), part: 0x20b1, ver: 0x0)
```

OpenOCD doesn't have an extensive list of Intel FPGAs, but it was able to detect a JTAG enabled device with JTAG standard 32-bit ID 
code of 0x020b10dd. That's the code of the Cyclone II EP2C5 FPGA that I'm using.

We can make things more well behaved by declaring the FPGA explicitly:

```sh
sudo /opt/openocd/bin/openocd \ 
    -f /opt/openocd/share/openocd/scripts/interface/altera-usb-blaster.cfg 
    -c "adapter_khz 6000" 
    -c "jtag newtap ep2c5 tap -expected-id 0x020b10dd -irlen 10"
```

This is the result:

```
Open On-Chip Debugger 0.10.0+dev-00930-g09eb941 (2019-09-16-21:01)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : only one transport option; autoselect 'jtag'
adapter speed: 6000 kHz

Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : usb blaster interface using libftdi
Info : This adapter doesn't support configurable speed
Info : JTAG tap: ep2c5.tap tap/device found: 0x020b10dd (mfg: 0x06e (Altera), part: 0x20b1, ver: 0x0)
Warn : gdb services need one or more targets defined
```

Much better!

# Generating the SVF File for Directly Loading into the FPGA

You should have a design that has successfully gone through all the stages of a Quartus 
compilation cycle, which means that there should be a `<project_name>.sof` and a `<project_name>.pof` file. These are 
normally located in the `./output_files` subdirectory.

The name of my test project is `blink` so that's what I'll be using going forward.

* Open Quartus Programmer. From the main Quartus window: [Tools] -> [Programmer]
* Use [Add File] to insert the SOF file to the JTAG chain, if it wasn't done automatically

    ![Quartus Programmer with SOF file added](/assets/intel_svf/quartus_programmer_add_sof.png)

* Use [File] -> [Create JAB, JBC, SVF or ISC File...] and fill in the form as follows:

    ![Quartus Programmer Create SVF File Form](/assets/intel_svf/quartus_programmer_create_svf_file.png)

    * Filename: `blink.svf`
    * File format: Serial Vector Format (.svf)
    * Operation: Program
    * Programming options: None
    * TCK frequency: 6 MHz

        The clock speed needs to be filled in correctly, with the peak clock rate. This is because certain programming
        operations might be timing specific. For example, if the FPGA must be reset for 1ms before a bitstream can be
        loaded, setting a 6MHz clock will result in a wait of 6000 clock cycles.

        **If you don't know the peak clock speed of your JTAG dongle, it's better to fill in a number that's too high
        than too low.** However, in that case the programming operation might take longer than needed, because the SVF might contain
        a wait of 12000 instead of 6000 clock cycles, if you fill in 12MHz isntead of the actual 6 MHz.

        Official USB Blasters run at a fixed 6MHz clock rate. An official USB Blaster II has a programmable clock rate 
        that can go up to 24MHz.

    * Supply voltage: 3.3 volts

        This is the JTAG IO voltage. 


Doing this with the GUI gets tiresome if you need to do a lot of interations. You can do it with the command line
like this:

```sh
quartus_cpf -c -q 6MHz -g 3.3 -n p output_files/blink.sof output_files/blink.svf
```

I often bypass the GUI whole Quartus compilation flow and kick off everything from a Makefile.

# Loading the SVF file into the FPGA

All that remains now is for openOCD to read the SVF file and apply it to the FPGA.

```
sudo /opt/openocd/bin/openocd \ 
    -f /opt/openocd/share/openocd/scripts/interface/altera-usb-blaster.cfg 
    -c "adapter_khz 6000" 
    -c "jtag newtap ep2c5 tap -expected-id 0x020b10dd -irlen 10"
    -c "init; svf -tap ep2c5.tap blink.svf; exit"
```

# Generating the SVF File to Program the FPGA Flash

**IMPORTANT: on my Cyclone II device, I was only ever able to program the flash when the flash was empty!!!
Since I couldn't find a way to erase the flash with an SVF file, this made programming the flash a one-time operation!!!**

Unfortunately, this step can vary a bit depending on which exact FPGA or flash memory you're using, but it may help
those who are looking for general pointers.

The key thing to remember is that most Intel FPGAs can program a flash that's connected to an FPGA with
a Serial Flash Loader (SFL). Under the hood, this works as follows:

* Load an Intel-provided bitstream with the Serial Flash Loader into the FPGA.

    The SFL contains logic that bridges the FPGA's JTAG port to the FPGA's flash port.

* Send the data that must be programmed into the flash through the JTAG port through the
  SFL into the flash.

    That data that can be programmed into the flash can be anything. It doesn't have to be a bitstream!
    But a bitstream is obviously something that will almost always be part of it, and that's what we'll do here.

We will be using the Quartus Converter tool for that.

**Create a .jic File with Quartus Convert Programming Files**

* From the main Quartus window (not Quartus Programmer!): [File] -> [Convert Programming Files...]
* Change the following fields:

    * Programming file type: JTAG Indirect Configuration File (.jic)
    * Configuration Device: EPCS4, Mode: Active Serial

        This depends on the FPGA board that you're using!

    * File name: `output_files/blink.jic`
* Select the correct serial flash loader:
    * [Flash Loader] -> [Add Device...]
    * Select the right device family and device name
* Select the bitstream
    * [SOF Data] -> [Add File...]
    * Select `blink.sof`
* Set extra SOF properties:
    * [blink.sof] -> [Properties]
    * Enable compression

        This is optional, but when your design doesn't have RAMs preinitialized or when it doesn't fill
        the whole FPGA, it will reduce the flash programming time and startup time of the FPGA.

        Modern FPGA can have a more advanced properties, such as bitstream encryption.

When you're done, things will look like this:

![Quartus Converter Form](/assets/intel_svf/quartus_converter.png)

You could use [Save Conversion Setup] to store all the settings.

**Convert the .jic File to an SVF File with Quartus Programmer**

Converting the .jic file to an .svf file is the same as for an .sof file.

* Load the .jic file into Quartus Programmer

    ![Quartus Programmer with JIC file added](/assets/intel_svf/quartus_programmer_add_jic.png)

* Use [Create JAB, JBC, SVF or ISC File...] to covert to SVF

I created a `blink_prog.svf` file.

