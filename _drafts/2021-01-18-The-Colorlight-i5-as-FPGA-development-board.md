---
layout: post
title: The Colorlight i5 as Lattice ECP5 FPGA Development Board
date:  2021-01-8 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

* version V7.0 (see PCB)

* Extension board:

    * [schematic](https://github.com/wuxx/Colorlight-FPGA-Projects/blob/master/schematic/i5_v6.0-extboard.pdf)
    * DDR2-SODIMM
    * 6 30-pin connectors
        * P1: 2x 4 Ethernet differential pairs
        * P2,P3,P4,P6: generic GPIO
            * compatible with 2x PMOD
            * intermediate pins have extra GPIO pins and 5V pin 
        * P5: generic GPIO + special functions
            * SPI,
            * UART
    * HDMI connector
        * video out
        * I2C, HOTPLUG, CEC not connected. :-(
    * STM32F103C8T6 microcontroller
        * identical to the one used in the Blue Pill
    * USB 5V -> 3.3V power
        * AMS1117-3.3V
            * powers the PMOD ports and the MCU
            * does NOT power the Colorlight module  
    * 2 LEDs
        * driven by MCU
        * red: LED_RUN
            * always one
        * green: LED_CON
            * on shortly after plugging in USB cable
    * power switch 
        * when pressed, interrupts power to Colorlight module, but not to the MCU
        * USB drive only disconnects after releasing button, not after pressing it
    * pogo pins connect MCU on extension board to JTAG pins of Colorlight module

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

# References

* [Colorlight i5 Product Page](https://www.colorlight-led.com/product/colorlight-i5-led-display-receiver-card.html)

* [Item on AliExpress](https://www.aliexpress.com/item/1005001686186007.html)

* [Development Board GitHub Repo](https://github.com/wuxx/Colorlight-FPGA-Projects)

* [Colorlight i5 Tips GitHub Repo](https://github.com/kazkojima/colorlight-i5-tips)
