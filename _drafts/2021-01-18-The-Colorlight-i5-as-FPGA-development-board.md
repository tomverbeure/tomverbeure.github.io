---
layout: post
title: Getting Started with the Colorlight i5 FPGA Development Board
date:  2021-01-8 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

There are hundreds of FPGA development boards out there, and I don't dare to count but I must own a
considerably fraction of them. Most of these were designed deliberately for development purposes, 
but a few were not, and yet they are a good match.

One board that falls in the latter category is the 
[Colorlight i5](https://www.colorlight-led.com/product/colorlight-i5-led-display-receiver-card.html).

![Colorlight i5](/assets/colorlight_i5/colorlight_i5.jpg)

Like other members of the Colorlight family (the [Colorlight 5A-75B](https://github.com/q3k/chubby75) 
comes to mind), these FPGA boards are 'real' products that are designed to be used as controllers for large 
LED video panels. And that's a huge plus, because in FPGA land, high volume means low cost, usually 
much lower than buying individual components on Digikey or Mouser.

The Colorlight i5 is especially attractive because it's a plug-in card, with a reappropriated DDR2 SODIMM 
connector. Even better is that nothing about this module seems to be tailored specifically for LED panels: unlike 
the 5A-75B, there are no unidirectional 3V3 to 5V level shifters. FPGA GPIO pins are routed straight to the 
SODIMM connector and can be used any way you want.

The Colorlight i5 uses a Lattice ECP5U-25, an FPGA that's supported by the Yosys/NextPNR open source
tool flow, an extra bonus.

That said, there's still a hurdle to using it as a hobby FPGA platform: you need a way to power it,
there are no easy usable GPIO connectors (such as PMOD connectors), and while are easily accessible
test JTAG points to program the FPGA, you still need an external JTAG programmer and solder a bunch
of wires to make things work.

Or...

you could use the Colorlight i5 development board that's by [Muse Lab](https://www.muselab-tech.com/) 
on [their AliExpress webstore](https://www.aliexpress.com/item/1005001686186007.html).

![Colorlight i5 Development Board](/assets/colorlight_i5/development_board.jpg)

I bought their Colorlight i5 module + development board combo for $50 and gave it a try. 

# The Colorlight i5 Module 

Let's first go over characterstics of the module itself:

![Colorlight i5 Top Annotated](/assets/colorlight_i5/i5-top-annotated.jpg)

* Low Cost: $30 and up

    I've seem them for $18.50, but with a $25 fee, which makes it only attactive if you're
    buying at least 3. For $35, you can get them with free shipping on AliExpress. That's
    still a fantastic deal for what you get.

* Lattice ECP5 LFE5U-25F FPGA

    Specifications:
    * 24K LUTs
    * 56x sysMEM block RAMs (of 18Kb each), good for up to 126KByte of on-chip RAM
    * 194Kb of distributed RAM
    * 28x 18x18 multipliers
    * 2 PLLs, 2 DLLs
    * 0 SERDES
    * 381 caBGA package

    The -25 version is one of the smaller versions in the ECP5 family, but it's still enough
    for many applications. You can comfortably fit a VexRiscv based Linux SOC in there.

* EtronTech EM638325-6H 2M x 32bit SDRAM, 166MHz

    Non-DDR SDRAM is ancient and slow now, but sufficient for most hobby projects. It's also much 
    easier to use because there's usually no trickery required with complex PLL/DLL configurations.

* 2x Broadcom B50612D 1Gb Ethernet Transceivers

    That's right, not one but two. You could make your own firewall with this thing.

    The PHYs are using an RGMII MAC interface. 

    The module only contains the transceivers, not the Ethernet transformers or 
    RJ45 connectors. The 2x 4 differentials pairs are routed to the DDR SODIMM pins. 

* GD25B16C 16Mbit Quad SPI Serial Flash

    According to the [Lattice ECP5 sysCONFIG Usage Guide](http://www.latticesemi.com/~/media/LatticeSemi/Documents/ApplicationNotes/EH/TN1260.pdf),
    the FPGA has a maximum uncompressed bitstream size of 5.42Mb. That leaves more than 11Mb or ~1.4MByte for
    user applications.

* 25MHz Oscillator

    The Ethernet transceivers require a 25MHz oscillator. It also goes to the FPGA.

* 2 LEDs

    A red LED seems to be connected to power and is always on, but the green LED is controlled
    by the FPGA: a strict requirement to get that blinky going!

* JTAG Interface
    
    4 JTAG test points are not marked as such but they are easy to solder and accessible.

* 3x Mystery CD4051B 8 Channel Analog Multiplexer/Demultiplexer 

    These are only present on V7.0 of the board, not on V6.0. It's functionality hasn't been
    reverse engineered yet, but some of the demultiplexed ports are going to the SODIMM pins.

* DDR2-SODIMM Connector

    * 3V3 to 6V power rail

        There are voltage regulators on the module, but there are no pins back to
        the connector with regulated voltage.

    * 2x 4 differential Ethernet pairs
    * 106x general purpose GPIO pins
    * 2 mystery `RCV_BK1`/`RCV_BK2` pins
    
        These have something to do with receiver backup power. Unknown how they are connected
        on the module.

    * 21 mystery pins

        These seem to be related to the 8 channel analog multiplexers.

* A heat sink

    Not exactly a heavy duty one, but a piece of metal that squeezes against the FPGA and
    the two Ethernet transceivers. Much better than nothing!

    The heat sink is pretty easy to remove without damaging the board.


There's a lot to work with here. What's even better is that there is the potential for future
upgrades: Colorlight has the i6, i9, and i9+ modules with the same pinout as the i5.
same pinout. The i9 board has a Lattice ECP5-45 FPGA, and the i9+ a Xilinx Artix A50T.

For the i5 board, V6.0 and V7.0 are pinout compatible too, with the exception of the mystery pins.

# Features of the Muse Lab Development Board 

As I wrote earlier, the development board can be [bought on AliExpress](https://www.aliexpress.com/item/1005001686186007.html), 
but only as a package deal: $50 for the development board and the i5 module, with free shipping.

It has the following features:

* DDR2-SODIMM socket for the i5 module
* 1x 30-pin connector for Ethernet
    
    This connector has the 2x 4 differential Ethernet pairs. 

* 4x 30-pin connectors for generic GPIOs

    Each connector has 20 GPIOs, ground, 3V3, and 5V pins. The
    pins are smartly organized so that the connector is also compatible
    with 2 side-by-side PMOD connectors. In this case, the number
    of usable GPIOs drops to 16, 8 for each PMOD.

* 1x 30-pin mixed-use connector for generic GPIOs + special functions

    Just like the 4 earlier connectors, there are 20 GPIOs on this connector,
    in the same configuration, but 6 of the GPIOs have been assigned
    a special meaning: UART and SPI.

    These pins are also routed to the microcontroller to be used as
    a potential FPGA debug console, and, presumably to flash the SPI
    flash on the board.

* HDMI connector - video out only

    This one is a surprise, since the FPGA on the module does not support
    high speed SERDES IOs. Instead, the pins are connected to generic
    IOs that can be configured as differential pairs.

    I doubt that these IOs meet the strict electrical requirements that are
    set by the HDMI standard, but meeting these requirements is not necessary
    to drive an image that can be decoded by most monitors.

    Unfortunately, the I2C, HOTPLUG and CEC pins of the HDMI connector
    are not connected. The lack of HOTPLUG makes it impossible to use
    the HDMI connector for video input. 

* USB C Port

    A USB C port is used to power the board, to program the FPGA, and to
    send UART console traffic from and to a host PC.

* STM32F103C8T6 microcontroller (MCU)

    This STM32 MCU is identical to the one used on the dirt cheap and popular 
    [Blue Pill development boards](https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill.html).

    The MCU on this development board is used as programming and debug
    interface only. On one side, it has a USB 2.0 interface to connect to a host
    PC. On the other, it controls JTAG, UART, and SPI pins to the Colorlight
    module. It also controls 2 LEDs.

    The user is not supposed to reflash the MCU with custom firmware, and there
    are no provision to do so. But I still expected there to be test pins
    to factory flash the MCU. It took me quite a while to figure out that 
    there are 4 test pins right underneath the USB C connector!

* USB 5V -> 3.3V voltage regulator

    An AMS1117-3.3V that's used to convert the USB 5V to 3V3 to power the MCU and the
    3v3 pins of the PMOD ports, but NOT the Colorlight module (which uses the 5V from the
    USB.

* 2 LEDs

    Not to be confused with the 2 bright LEDs on the module itself, two tiny and faint LEDs 
    are controlled by the MCU. The red LED flickers when there's USB traffic. A blue
    LED seems to be always on and hidden entirely below the module.

* Power Button 

    When pressed, this button interrupts power to Colorlight module, but not to the MCU.

* JTAG Pogo Pins 

    The i5 module has easy accessible JTAG test points, but they are not connected to the SODIMM
    connector. The development board makes the connection with the test points with 4 pogo pins.
    It's an elegant solution that removes the need for any soldering.

# First Impressions

The package arrived with the i5 module (mine is revision V7.0), the development board, a USB C cable, and 6 30-pin
connectors that you need to solder yourself. 

I'm not well qualified to judge the quality of the PCB, but looks well made to me.

After inserting the 30-pin connectors into the PCB (it's a bit of a hassle that requires
wiggling), I noticed a minor issue: my HDMI cable doesn't fit between the 2 30-pin connectors
that surround the HDMI connector. As a result, the cable can't be plugged in completely.

It still goes in deep enough to make an electrical connector, but it's not ideal.

The box doesn't contain any documentation, not even a leaflet with a URL. You have to make 
do with Google or a link on the AliExpress product page to a GitHub repo.

Without further instructions, I plugged in USB cable into the board and my PC, some LEDs came up
and I heard a little sound: my PC told me that it has seen a new USB drive. So far so good!


# Design Documentation


* Extension board:

    * [schematic](https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/schematic/i5_v6.0-extboard.pdf)

* `./doc` directory contains all datasheets

* borrows a lot from ULX3S board: examples, tools

* Linux dmesg after plugging in USB cable:

```
[2880370.262441] usb 1-11.2: new full-speed USB device number 29 using xhci_hcd
[2880370.381512] usb 1-11.2: New USB device found, idVendor=0d28, idProduct=0204, bcdDevice= 1.00
[2880370.381515] usb 1-11.2: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[2880370.381517] usb 1-11.2: Product: DAPLink CMSIS-DAP
[2880370.381519] usb 1-11.2: Manufacturer: ARM
[2880370.381520] usb 1-11.2: SerialNumber: 070000010670ff495356675287180632a5a5a5a597969908
[2880370.402789] usb-storage 1-11.2:1.0: USB Mass Storage device detected
[2880370.402976] scsi host6: usb-storage 1-11.2:1.0
[2880370.403390] cdc_acm 1-11.2:1.1: ttyACM0: USB ACM device
[2880370.405824] hid-generic 0003:0D28:0204.0008: hiddev0,hidraw4: USB HID v1.00 Device [ARM DAPLink CMSIS-DAP] on usb-0000:00:14.0-11.2/input3
[2880371.411276] scsi 6:0:0:0: Direct-Access     MBED     VFS              0.1  PQ: 0 ANSI: 2
[2880371.411699] sd 6:0:0:0: Attached scsi generic sg1 type 0
[2880371.412601] sd 6:0:0:0: [sdb] 131200 512-byte logical blocks: (67.2 MB/64.1 MiB)
[2880371.412808] sd 6:0:0:0: [sdb] Write Protect is off
[2880371.412810] sd 6:0:0:0: [sdb] Mode Sense: 03 00 00 00
[2880371.413000] sd 6:0:0:0: [sdb] No Caching mode page found
[2880371.413003] sd 6:0:0:0: [sdb] Assuming drive cache: write through
[2880371.440502]  sdb:
[2880371.441769] sd 6:0:0:0: [sdb] Attached SCSI removable disk
```

* DAPLINK drive appears in Ubuntu desktop with the following files:

![DAPLINK folder](/assets/colorlight_i5/DAPLINK_attached_drive.png)

# Getting Started - Examples

* Default bitstream: tried to connect with picocom, but garbage on the output for 115200, 38400, and 9600 bps
* Compile openocd with `--enable-cmsis-dap`: https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/get-start.md
    * `sudo apt-get install libhidapi-dev`
* Info about [CMSIS-DAP](https://arm-software.github.io/CMSIS_5/DAP/html/index.html)
* clone repo
        
```sh
git clone https://github.com/wuxx/Colorlight-FPGA-Projects.git
cd Colorlight-FPGA-Projects
cd tools
. env.sh
cd ../demo/i5
dapprog blink.svf
```


* Litex Demo:

```
tom@thinkcenter:~/projects/Colorlight-FPGA-Projects/demo/i5$ dapprog litex_with_dram.svf 
EXT: svf
TARGET: litex_with_dram.svf
Open On-Chip Debugger 0.10.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
adapter speed: 10000 kHz
Info : CMSIS-DAP: SWD  Supported
Info : CMSIS-DAP: JTAG Supported
Info : CMSIS-DAP: Interface Initialised (JTAG)
Info : CMSIS-DAP: FW Version = 0254
Info : SWCLK/TCK = 1 SWDIO/TMS = 1 TDI = 1 TDO = 1 nTRST = 0 nRESET = 1
Info : CMSIS-DAP: Interface ready
Info : reduce speed request: 10000kHz to 5000kHz maximum
Info : clock speed 10000 kHz
Info : cmsis-dap JTAG TLR_RESET
Info : cmsis-dap JTAG TLR_RESET
Info : JTAG tap: ecp5.tap tap/device found: 0x41111043 (mfg: 0x021 (Lattice Semi.), part: 0x1111, ver: 0x4)
Warn : gdb services need one or more targets defined
   TapName             Enabled  IdCode     Expected   IrLen IrCap IrMask
-- ------------------- -------- ---------- ---------- ----- ----- ------
 0 ecp5.tap               Y     0x41111043 0x41111043     8 0x01  0x03
svf processing file: "litex_with_dram.svf"
70%    Info : cmsis-dap JTAG TLR_RESET
95%    
Time used: 0m29s786ms 
svf file programmed successfully for 741 commands with 0 errors
```

```
tom@thinkcenter:~/projects/Colorlight-FPGA-Projects/demo/i5$ picocom -b 38400 /dev/ttyACM0
picocom v2.2

port is        : /dev/ttyACM0
flowcontrol    : none
baudrate is    : 38400
parity is      : none
databits are   : 8
stopbits are   : 1
escape is      : C-a
local echo is  : no
noinit is      : no
noreset is     : no
nolock is      : no
send_cmd is    : sz -vv
receive_cmd is : rz -vv -E
imap is        : 
omap is        : 
emap is        : crcrlf,delbs,

Type [C-a] [C-h] to see available commands

Terminal ready
<DAPLink:Overflow>
                  Booting from boot.bin...
Copying boot.bin to 0x40000000... 
Network boot failed.
No boot medium found

--============= Console ================--

litex>   
```

```
litex> reboot


        __   _ __      _  __
       / /  (_) /____ | |/_/
      / /__/ / __/ -_)>  <
     /____/_/\__/\__/_/|_|
   Build your hardware, easily!

 (c) Copyright 2012-2020 Enjoy-Digital
 (c) Copyright 2007-2015 M-Labs

 BIOS built on Oct  2 2020 22:57:04
 BIOS CRC passed (5d238c53)

 Migen git sha1: 7bc4eb1
 LiteX git sha1: 8bdf6941

--=============== SoC ==================--
CPU:       VexRiscv @ 198MHz
BUS:       WISHBONE 32-bit @ 4GiB
CSR:       8-bit data
ROM:       32KiB
SRAM:      8KiB
L2:        32KiB
MAIN-RAM:  4096KiB

--========== Initialization ============--
Ethernet init...
Initializing DRAM @0x40000000...
SDRAM now under software control
SDRAM now under hardware control
Memtest at 0x40000000...
[########################################]
[########################################]
Memtest OK
Memspeed at 0x40000000...
Writes: 461 Mbps
Reads:  382 Mbps

--============== Boot ==================--
Booting from serial...
Press Q or ESC to abort boot completely.
sL5DdSMmkekro
             Timeout
Booting from network...
Local IP : 192.168.1.50
Remote IP: 192.168.1.100
Booting from boot.json...
Booting from boot.bin...
Copying boot.bin to 0x40000000... 
Network boot failed.
No boot medium found

--============= Console ================--

litex> 
```

* Programming the flash with a bitstream

```
tom@thinkcenter:~/projects/Colorlight-FPGA-Projects/demo/i5$ dapprog blink_flash.svf
EXT: svf
TARGET: blink_flash.svf
Open On-Chip Debugger 0.10.0
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
adapter speed: 10000 kHz
Info : CMSIS-DAP: SWD  Supported
Info : CMSIS-DAP: JTAG Supported
Info : CMSIS-DAP: Interface Initialised (JTAG)
Info : CMSIS-DAP: FW Version = 0254
Info : SWCLK/TCK = 1 SWDIO/TMS = 1 TDI = 1 TDO = 1 nTRST = 0 nRESET = 1
Info : CMSIS-DAP: Interface ready
Info : reduce speed request: 10000kHz to 5000kHz maximum
Info : clock speed 10000 kHz
Info : cmsis-dap JTAG TLR_RESET
Info : cmsis-dap JTAG TLR_RESET
Info : JTAG tap: ecp5.tap tap/device found: 0x41111043 (mfg: 0x021 (Lattice Semi.), part: 0x1111, ver: 0x4)
Warn : gdb services need one or more targets defined
   TapName             Enabled  IdCode     Expected   IrLen IrCap IrMask
-- ------------------- -------- ---------- ---------- ----- ----- ------
 0 ecp5.tap               Y     0x41111043 0x41111043     8 0x01  0x03
svf processing file: "blink_flash.svf"
5%    Info : cmsis-dap JTAG TLR_RESET
Info : cmsis-dap JTAG TLR_RESET
Info : cmsis-dap JTAG TLR_RESET
Error: tdo check error at line 45
Error:     READ = 0x78ff
Error:     WANT = 0x0ff
Error:     MASK = 0xc100
Error: fail to run command at line 2137
Error: tdo check error at line 45
Error:     READ = 0x78ff
Error:     WANT = 0x0ff
Error:     MASK = 0xc100

Time used: 0m7s504ms 
svf file programmed failed
```
Flash is locked.

* Load bitstream from `colorlight-i5-tips` with Litex
* Connect with terminal at 115200
* `flash_write_protect 0`
* `dapprog blink_flash.svf` -> pass
    * Still works after power cycle

* Loading a bitstream volatile -> ~30s
* Loading a bitstream flash -> ~40

# Create your own design

* Compile Yosys, nextpnr-ecp5, prjtrellis
* 

# References

* [Colorlight i5 Product Page](https://www.colorlight-led.com/product/colorlight-i5-led-display-receiver-card.html)

* [Item on AliExpress](https://www.aliexpress.com/item/1005001686186007.html)

* [Development Board GitHub Repo](https://github.com/wuxx/Colorlight-FPGA-Projects)

* [Colorlight i5 Tips GitHub Repo](https://github.com/kazkojima/colorlight-i5-tips)

* [Colorlight i9 Tweet](https://twitter.com/Claude1079/status/1249983499655950336)
