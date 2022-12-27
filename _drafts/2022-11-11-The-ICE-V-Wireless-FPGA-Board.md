---
layout: post
title: An In-Depth Look at the ICE-V Wireless FPGA Development Board
date:  2022-11-11 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

It's been more than 7 years now since the first public release of 
[Project IceStorm](http://bygone.clairexen.net/icestorm/).  Its goal was to reverse engineer to the internals
of Lattice ICE40 FPGAs, and create full open source toolchain to go from RTL all the way
to place-and-routed bitstream.  Project IceStorm was a huge success and a small revolution in the 
world of hobby electronics. While it had been possible to design for FPGAs before,
it required multi-GB behemoth software installations, and there weren't a lot of cheap development
boards.

Project IceStorm kicked off industry of small scale makers who created their own development boards, each
with a distinct set of features. One crowd favorite has been the 
[TinyFPGA BX](https://www.crowdsupply.com/tinyfpga/tinyfpga-ax-bx), which is still available for
$38, one of the lowest prices to get your hands dirty with an FPGA that has a capacity that will
exceed the needs of most users.

The BX board is very bare bones: it's BYOP, Bring Your Own Peripherals, and there's not even a PMOD 
connector for quick experimentation with external modules. That's great if you're working on a custom 
build with physical size constraints, but often you want to have something with a bit more features.

The ICE-V Wireless is a relatively new entrant in this market. Developed by 
[Querty Embedded Design](http://www.qwertyembedded.com/), it's available at 
[GroupGets.com](https://store.groupgets.com/products/ice-v-wireless) for $99. I ran into 
its creator at the 2022 Hackaday Supercon, and he gave me a board for review.

![ICV-V Wireless board - front view](/assets/icev/ice-v_front.jpg)
*(Photo from ICE-V Wireless github page)*

Let's check it out!

# The ICE-V Wireless FPGA Board

The [ICE-V Wireless GitHub project](https://github.com/ICE-V-Wireless/ICE-V-Wireless) has schematics
and PCB layout available both in their KiCAD 6.0 format. There's also a
[PDF version of the schematic](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/docs/esp32c3_fpga_schematic.pdf)
which is always convenient.

Let's check out the different components:

* ESP32-C3-MINI-1 module ([datasheet](/assets/icev/esp32-c3-mini-1_datasheet_en.pdf))

    An excellent member of the well-known Espressif portfolio. It includes:

    * support for 2.4 Wifi (802.11 b/g/n) and Bluetooth 5
    * a RISC-V CPU
    * 4MB embedded flash
    * on-board PCB antenna

* ICE5LP4K-SG48 from the [Lattice iCE40 Ultra family](https://www.latticesemi.com/Products/FPGAandCPLD/iCE40Ultra)

    This FPGA is less commonly used and slightly smaller than the ICE40-UP5K FPGA, but still has a respectable 
    number of features:

    * 3520 LUTs
    * 80 kbits of block RAM
    * 4 DSPs
    * 2 I2C and SPI cores

    One of the most attractive features of iCE40 Ultra family is their ultra-low static power: just 71 uA
    for this version. This makes the FPGA particularly well-suited for battery operated use cases.

    One feature lacking from this FPGA compared to the more popular iCE40UP5K is the lack of a large slab
    of SRAM. But fear not, because the board also has:

* LY68L6400, a SPI/QPI serial pseudo-SRAM (PSRAM) with a whopping 64M bits of RAM ([datasheet](/assets/icev/LY68L6400-0.4.pdf))

    The RAM is connected directly to the FPGA. It has a clock rate of 100MHz. In QPI mode, with 4 data lines working
    in parallel, a peak transfer rate of 4MB/s should be sufficient for many applications. 

* 3 PMOD ports

    These are your standard double-row configuation PMOD connectors with 8 GPIOs per port, all of which are
    controlled by the FPGA. Unusual is that the power of each PMOD can be individually selected to be
    either the 3v3 rail from the on-board power regulator, or the 4V/5V rail coming from USB (5V, when plugged in)
    or LiPo battery (4V, when present.)

    A nice touch is that the PCB silk screen shows the FPGA pin number of each PMOD IO pin, as well as the
    polarity of differential FPGA IO pairs.

    ![PMOD FPGA pin numbering](/assets/icev/pmod_fpga_pin_numbers.jpg)

* Auxiliary GPIO connector

    The 8 remaining GPIOs of the FPGA and the ESP32 are routed to a 12-pin connector that can optionally
    be populated with a pin header. Reset, power and ground are also avaiable.

    ![GPIO pin numbering](/assets/icev/gpio_connector_pin_numbers.jpg)

* Standard LiPo battery JST connector with charging logic

    It's always nice to have a charge management controller on board. This one uses a 
    [Microchip MCP73831 ](https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf).

    Here's such a battery, [sold by Adafruit](https://www.adafruit.com/product/3898). 

    ![LiPo battery with JST connector](/assets/icev/lipo_battery_with_jst.jpg)

    If there were any doubts left about the IoT/mobile intensions of this board, the inclusion of the charging logic 
    and battery connector should put these to rest.

* XC6222B331MR-G 3v3 LDO Power Regulator ([datasheet](https://www.digikey.com/en/products/detail/torex-semiconductor-ltd/XC6222B331MR-G/2138187))

    This jelly bean component normally doesn't deserve special mention, but since it also
    drives the PMOD power pins, it's worth pointing out that it has a maximum output current of 700mA.

* USB-C Device Port

    The USD-C port can be used to power the whole board. It also connects to the USB port of othe ESP32 module,
    where it can either act as serial port or a JTAG controller.

* Various smaller components 

    * reset and boot buttons. The boot button can be used as general purpose button for the ESP32.
    * RGB LED connected to the FPGA.
    * various status LEDs
    * 12MHz oscillator

# Preloading the PSRAM with User Data

FPGA boards with just an FPGA are usually pretty simple affairs: there's usually a flash SPI PROM
on the board from which the FPGA sucks in the bitstream automatically after power up. Sometimes,
there's also JTAG interface to directly load a new bitstream into the FPGA, but that's not something
a the Lattice ICE40 family supports.

In addition to storing the bitstream, the SPI flash PROM often also contains user data that can
fetched by the FPGA as needed. A common use case is one where the FPGA has a soft-CPU core with the
firmware of the CPU residing in the SPI flash.

During the bitstream loading process, the FPGA is configured in *active serial mode*: the FPGA
is the controller of the SPI bus. And after the bitstream is loaded, the FPGA is controller
of the SPI bus as well, if it needs access to SPI user data.

![Traditional FPGA configuration](/assets/icev/ICEV_drawings-traditional_configuration.png)

Things are more complicated when there's an SOC like the ESP32C3 on the board. 

![ICE-V configuration](/assets/icev/ICEV_drawings-ICEV_configuration.png)

Since the SOC module already contains embedded flash, which has its own 
[SPIFFS filesystem](https://docs.espressif.com/projects/esp-idf/en/v5.0/esp32c3/api-reference/storage/spiffs.html).

It'd be a waste to add an additional SPI bitstream flash just for the FPGA. Instead, the 
FPGA boots up in *passive serial mode*: during bitstream loading, the SPI port on the FPGA 
side is configured as a device and the ESP32C3 is the controller that loads the bitstream from
the embedded flash into the FPGA.

A negative of this approach, however, is that there isn't a place anymore where the
FPGA can fetch user data! The ICE-V Wireless board solves this by adding a
(Q)SPI Pseudo RAM to the system.

This PSRAM can of course be used by the FPGA as a pure RAM, but if the PSRAM can be
pre-loaded with user data, part of it can just as well be used a pseudo flash PROM.
The pseudo SRAM is a psuedo SPI PROM if you will.

The only question that remains then is how to get the user data into the PSRAM before the
FPGA starts executing the main user bitstream? 

It's a multi-stage process:

0. The ESP32C3 first check if the PSRAM needed to be preloaded with user data. It does this
   by [checking if there exists a non-empty `psram.bin` file on its embedded flash file system](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L85).

   If there isn't a `psram.bin` file, it jumps to step 3 and just loads the user FPGA bitstream.

1. the ESP32C3 fetches a bitstream called [`spi_pass.bin`](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L23)
   from the embedded flash and [loads it into the FPGA](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L90).

    This bitstream is completely trivial (you can check the code 
    [here](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Gateware/spi_pass/spi_pass.v)).
    All it does is connect the ESP32C3 SPI interface to the PSRAM SPI interface.

2. the ESP32C3 now fetches a binary file called 
    [`psram.bin`](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L24)
    from embedded flash and [programs it straight into the PSRAM](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L114-L133), 
    with the FPGA as SPI signal conduit.

3. the ESP32C3 now fetches the user bitstream called [`bitstream.bin`](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L22)
   from the embedded flash and [loads it into the FPGA](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/main.c#L154).

4. with the FPGA configured with the user bitstream, it is now free to let the FPGA whatever the user
   has programmed it to do.

    If there is a need for communication between the ESP32C and the FPGA, it can do so through the
    same SPI interface. Similarly, if the FPGA needs user data, it can fetch that from the
    PSRAM.

![ICE-V PSRAM usage](/assets/icev/ICEV_drawings-ICEV_PSRAM_usage.png)

The default ICE-V Wireless ESP32C3 firmware has all of this implemented. The GitHub repo
also has the necessary support tools to complete the flow. It's great! However, it's only after
disecting the firmware source code that I was able to piece the puzzle together. 

# The Overall Boot Process

With the details of PSRAM preloading out of the way, let's zoom out a bit more and look at the
overall boot process.

* As is already clear, the ESP32C3 is the orchestrator of the whole process.
* after powering up, the ESP32C3 follows the boot procedure that is described in the 
  [ESP32C Boot Mode Selection documentation](https://docs.espressif.com/projects/esptool/en/latest/esp32c3/advanced-topics/boot-mode-selection.html):

    GPIO9 is the bootloader select pin. On the ICE-V board, it's connected to the BOOT button.

    * When GPIO9 is low (BOOT button pressed while releasing reset), the ESP32C3 boots from a
      ROM inside the ESP32C3 chip that sets up a bootloader over the USB serial port. 

      No matter how much you screw up your custom firmware, you will always be able to reflash new firmware,
      such as the default ICE-V firmware, by pressing the BOOT button and releasing RESET.

    * When GPIO9 is high (BOOT button not pressed), the ESP32C3 goes in *Normal execution mode*. 

      It will first perform a bunch of internal boot housekeeping after which it loads
      firmware that is stored in its embedded SPI flash and execute it.

      This is the normal operation. Expect to use this mode a lot, especially when you primarily use
      the ICE-V board as a FPGA board that just happens to have an ESP32 module as well.

# UART Console

In what's become a common theme: it's not mentioned in any of the manual pages, but the board schematic
shows how GPIO21 of the ESP32C3 has boot logging:

![ESP32C console UART](/assets/icev/ESP32C3_console_UART.png)

This is a standard ESP32C3 feature. I wired up a USB serial port dongle to GPIO21 pin
and connected to with with `picocom -b 115200 /dev/ttyUSB0`.

In boot loader mode (BOOT button pressed when releasing RST), it shows the following:

```
ESP-ROM:esp32c3-api1-20210207
Build:Feb  7 2021
rst:0x1 (POWERON),boot:0x7 (DOWNLOAD(USB/UART0/1))
waiting for download
```

And here's what it prints out during normal boot:

```
ESP-ROM:esp32c3-api1-20210207
Build:Feb  7 2021
rst:0x1 (POWERON),boot:0xf (SPI_FAST_FLASH_BOOT)
SPIWP:0xee
mode:DIO, clock div:1
load:0x3fcd6100,len:0x16b4
load:0x403ce000,len:0x91c
load:0x403d0000,len:0x2d00
entry 0x403ce000
I (30) boot: ESP-IDF v4.4.2 2nd stage bootloader
I (30) boot: compile time 13:14:59
I (30) boot: chip revision: 3
I (32) boot.esp32c3: SPI Speed      : 80MHz
I (37) boot.esp32c3: SPI Mode       : DIO
I (41) boot.esp32c3: SPI Flash Size : 4MB
I (46) boot: Enabling RNG early entropy source...
I (51) boot: Partition Table:
I (55) boot: ## Label            Usage          Type ST Offset   Length
I (62) boot:  0 nvs              WiFi data        01 02 00009000 00006000
I (70) boot:  1 phy_init         RF data          01 01 0000f000 00001000
I (77) boot:  2 factory          factory app      00 00 00010000 00100000
I (85) boot:  3 storage          Unknown data     01 82 00110000 00100000
I (92) boot: End of partition table
I (96) esp_image: segment 0: paddr=00010020 vaddr=3c090020 size=16958h ( 92504) map
I (119) esp_image: segment 1: paddr=00026980 vaddr=3fc90600 size=02bb8h ( 11192) load
I (122) esp_image: segment 2: paddr=00029540 vaddr=40380000 size=06ad8h ( 27352) load
I (130) esp_image: segment 3: paddr=00030020 vaddr=42000020 size=8c434h (574516) map
I (223) esp_image: segment 4: paddr=000bc45c vaddr=40386ad8 size=09ae8h ( 39656) load
I (231) esp_image: segment 5: paddr=000c5f4c vaddr=50000010 size=00010h (    16) load
I (236) boot: Loaded app from partition at offset 0x10000
I (236) boot: Disabling RNG early entropy source...
I (241) cpu_start: Pro cpu up.
I (256) cpu_start: Pro cpu start user code
I (256) cpu_start: cpu freq: 160000000
I (256) cpu_start: Application information:
I (259) cpu_start: Project name:     ICE-V_Wireless
I (264) cpu_start: App version:      1048184
I (269) cpu_start: Compile time:     Dec 25 2022 13:15:04
I (275) cpu_start: ELF file SHA256:  0ed39813b88c943b...
I (281) cpu_start: ESP-IDF:          v4.4.2
I (286) heap_init: Initializing. RAM available for dynamic allocation:
I (293) heap_init: At 3FC97940 len 000286C0 (161 KiB): DRAM
I (300) heap_init: At 3FCC0000 len 0001F060 (124 KiB): STACK/DRAM
I (306) heap_init: At 50000020 len 00001FE0 (7 KiB): RTCRAM
```

Once you start changing the ESP32C3 firmware for your own applications, this kind of
UART console can be worth its weight in gold.

# Getting Started with the ICE-V Wireless Board for Real

When you first plug in the ICE-V Wireless board, it should immediately come up with a bunch of LEDs doing their thing:

* a red LED indicates that the board has power.
* a yellow LED will be blinking at high frequency to indicate that a LiPo battery is not connected.
* a slowly blinking green LED indicates that the ESP32C3 is not connected to a wireless network.
* a big tri-color LED will be cycling smoothly through the colors of the rainbow.

At the time of writing this review, the GitHub repo has a 
The [Getting Started page](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Getting-Started.md) 
GitHub repo will get you, well, started... eventually, but the documentation is generally lacking for a 
beginner. Some of the information is there, but it's more written in the style of a reference guide. 

What it needs is a tutorial with a clear, unambiguous path to go for unpacking to getting familiarized 
with the board.

Let's try to correct that.

**Main Repo Installation**

You always start with getting a copy of the main GitHub repo:

```sh
git clone https://github.com/ICE-V-Wireless/ICE-V-Wireless.git
```

Among others, the repo contains `Firmware`, `Gateware`, `Hardware` and `python` directories. 

Initially, the `python` directory is the most important one: it contains the tools to estabilish 
communication between the default ESP32C3 firmware and your PC, and allows you to perform
a variety of maintenance and configuration operations.

**The Default ICE-V Wireless Firmware**

The default ICE-V Wireless firmware is the one that can be found in the `./Firmware`
directory. This firmware uses the ESP32C3 RISV-C CPU only as a support CPU for FPGA
bitstream bootup, the procedure that I describe earlier.

* It sets up a USB serial port (on `/dev/ttyACM0` on my Ubuntu 20.04 system) for
  PC to board communication.
* After additional configuration over USB, it also sets up a Wifi connection for  
  PC to board communication.
* Using these communication channels, it allows you to configure the FPGA after
  booting up.
* Read and write files with data to the PSRAM on the board.
* It returns information about battery status and IP address of the Wifi connection.

When you want to run your own custom firwmare, you should try to jumpstart your development
from the original firmware and keep some of the existing functionality. This will allow
you to keep on using the provided tools to reflash the FPGA bitstream.

**Basic Sanity Testing and Maintenance Functions**

There are 3 tools in the `python` directory:

* `send_c3usb.py`

    Talks to the standard ESP32C3 firmware over USB. You'll be using this to check
    the battery level, check firmware version, and write files to the SPIFFS
    file system that resides on the ESP32C32 4MB embedded SPI NOR flash.

    The SPIFFS file system contains, among other things, the bitstream that gets loaded
    into the FPGA at bootup.

    You also use this tool to configure a Wifi network and password to which the ESP32C3
    can connect to.

* `send_c3sock.py`

    This tool has largely the same functionatily as `send_c3usb.py`, but it does its
    magic over a TCP/IP socket using Wifi. That's great, because it means that you can
    change the FPGA bitstream over Wifi, and thus while your ICE-V board is embedded deep
    into whichever application you want to use it for.

    Of course, you can only start using this tool once you have the configured a Wifi
    network to connect to with `send_c3usb.py`.

* `icevwprog.py`

    Something something something about loading a bitstream to the FPGA, but 
    completely undocument... 

So let's play around a bit:

```sh
cd ./ICE-V-Wireless/python
tom@zen:~/projects/ICE-V-Wireless/python$ ./send_c3usb.py --info
Version 0.3 , IP Addr unavailable
tom@zen:~/projects/ICE-V-Wireless/python$ ./send_c3usb.py --battery
Vbat = 4052 mV
```

The board is responding. Good!

I didn't have a battery installed, but in that case, 4.052V measured is the voltage
that's driven by the LiPo charger: 

![Battery voltage path](/assets/icev/battery_voltage.png)

**Configure Wifi**

Here's the help page of `./send_c3usb.py`:

```sh
tom@zen:~/projects/ICE-V-Wireless/python$ ./send_c3usb.py -h
./send_c3usb.py  [options] [<file>] | [DATA] | [LEN] communicate with ESP32C3 FPGA
  -h, --help              : this message
  -p, --port=<tty>        : usb tty of ESP32C3 (default /dev/ttyACM0)
  -b, --battery           : report battery voltage (in millivolts)
  -f, --flash=<file>      : write <file> to SPIFFS flash
  -i, --info              : get info (version, IP addr)
  -l, --load=<cfg#>       : load config from SPIFFS (0=default, 1=spi_pass
  -r, --read=REG          : register to read
  -w, --write=REG DATA    : register to write and data to write
      --ps_rd=ADDR LEN    : read PSRAM at ADDR for LEN to stdout
      --ps_wr=ADDR <file> : write PSRAM at ADDR with data in <file>
      --ps_in=ADDR <file> : write PSRAM init at ADDR with data in <file>
  -s, --ssid <SSID>       : set WiFi SSID
  -o, --password <pwd>    : set WiFi Password
```

I tried to configure the Wifi connection as follows:

```sh
./send_c3usb.py -s MyWifi -o VerySecretPassword
```

**This didn't work!**

It turns that the tool can process only one command line option at the time. The right 
procedure is as follows:

```sh
./send_c3usb.py -s MyWifi 
./send_c3usb.py -o VerySecretPassword
```

After this, you need to reset the board with the RST botton. If all goes well, the green LED will
start blinking vigorously at 5Hz to indicate that the ESP32C3 has successfully make a connection 
with your wifi network.

You can now use `send_c3sock.py` instead of `send_c3usb.py` to control the board. Like this:

```sh
tom@zen:~/projects/ICE-V-Wireless/python$ ./send_c3sock.py --info
Version = 0.3 , IP Addr = 192.168.1.178
```

Success!

I've played a little bit with ESP Wifi modules in the past. One of the things that I found
annoying was the hassle of finding the right IP address, something that can change after
each reset on a DHCP configured local network.

I'm pleasantly suprised about the frictionless process of the ICE-V Wireless board. The
default firmware declares the board with a default
[`ICE-V.local`](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Firmware/main/wifi.c#L310)
hostname, which is also the hostname that `send_c3sock.py` looks for. You'll probably have
to change this when you have multiple active ICE-V boards, but it just worked in
my case.

# Reinstalling or Modifying the ESP32C3 Firmware 

If you want to flash the ICE-V board with new or the original ESP32C3 firmware,
you'll need an Espressif design environment. Installation on my machine was surprisingly
straight forward.

* Download [release v4.4.2 of the Espressif IDF](https://github.com/espressif/esp-idf/releases/tag/v4.4.2)
    
    ```sh
cd ~/tools
git clone -b v4.4.2 --recursive https://github.com/espressif/esp-idf.git esp-idf-v4.4.2
    ```

    Keep an eye on the [ICE-V Firmware README](https://github.com/ICE-V-Wireless/ICE-V-Wireless/tree/main/Firmware)
    if you want to do this yourself: it's always possible that they'll require a later version for
    later firmware versions.

* Install the ESP32C3 version

    ```sh
cd ~/tools/esp-idf-v4.4.2
./install.sh esp32c3
    ```

    This will download and install a whole bunch of files in a `~/.espressif` directory.

* Set up your `$PATH` to include the Espressif tools

    ```sh
cd ~/tools/esp-idf-v4.4.2
. ./export.sh
    ```

    You might want to add that last line to your `~/.profile` file, but I prefer to just run it in that one
    terminal window where I plan to do development.

* Compile ICE-V Wireless firmware

    ```
cd ~/projects/ICE-V-Wireless/Firmware
idf.py build
    ```

    This will kick off a bunch of compilations. If all goes well, you'll be greated by this meassage:

    ```
Project build complete. To flash, run this command:
/home/tom/.espressif/python_env/idf4.4_py3.8_env/bin/python ../../../tools/esp-idf-v4.4.2/components/esptool_py/esptool/esptool.py -p (PORT) -b 460800 --before default_reset --after hard_reset --chip esp32c3 --no-stub write_flash --flash_mode dio --flash_size detect --flash_freq 80m 0x0 build/bootloader/bootloader.bin 0x8000 build/partition_table/partition-table.bin 0x10000 build/ICE-V_Wireless.bin 0x110000 build/storage.bin
or run 'idf.py -p (PORT) flash'
    ```

* Flash the firmware

    ```sh
idf.py -p /dev/ttyACM0 flash
    ```

    That's really it!

    I expected that I'd have to press the BOOT button and do a RST before I'd be able to flash the
    firmware, but that was not needed.


It would go too far to get into all the details of developing for the ESP32C3.
Luckily, Espressif provides a ton of [development documentation](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/index.html)
about just that.

# The Example FPGA Design

The visual effect of the example bitstream is trivial, the LED just cycles through
all colors, but the design behind it is elaborate. 

It's a small SOC that contains:

* a [picorv32](https://github.com/YosysHQ/picorv32) RISC-V soft-CPU
* a UART
* an SPI device that goes to a number of registers and a mailbox FIFO.

    This allows the ESP32C3 to interact with the soft-CPU.

* 2 SPI controllers

    The UP5K FPGA has 2 hard-macro `SB_SPI` controllers. I don't think I've ever seen
    them being used in the past, but this SOC 
    [instantiates both of them](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/38e0798b7f3acd68918e2c34cd632a507d861276/Gateware/riscv/src/wb_bus.v#L54-L320), 
    and even has [a SW driver](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Gateware/riscv/c/spi.c).

    The PSRAM is connected to the one of these SPI controllers. There's [a driver](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Gateware/riscv/c/psram.c)
    for that too.

* an I2C controller

    Like the SPI controllers, the UP5K also has a hard-macro `SB_I2C` controller.
    It's [instaniated in the example design](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/38e0798b7f3acd68918e2c34cd632a507d861276/Gateware/riscv/src/wb_bus.v#L323-L406),
    again with [a driver](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Gateware/riscv/c/i2c.c).

* a PWM controller for the LEDs

The directory structure is a bit confusing, but the toplevel file of the design is 
[here](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/main/Gateware/src/bitstream.v).

While it's nice to have a relatively complex design example to show off the possibilities,
I feel that's also a bit overwhelming, especially since nothing about the design is documented.
It'd be easier for a new user to have multiple examples of increasing complexity.

I think the following stand-alone examples would have been useful:

* a simple LED blinky
* a small design that demonstrates communication between the ESP32C3 and the FPGA
* the FPGA reading some data from the PSRAM

# Compiling the Example FPGA Design

Since there aren't any basic examples, let's just go ahead and go through the motions to compile
the whole thing.

* Open FPGA toolchain installation

    The Yosys Open Source CAD suite contains all the tools needed to build an FPGA bitstream.
    It used to be a lengthly compilation process, but these days you can just download a release that
    contains everything.

    The commands below install the tools exactly where the ICE-V Gateware development environment
    expects it. If you want to install it somewhere else, you'll need to 
    [modify the Makefile to point to the right location](https://github.com/ICE-V-Wireless/ICE-V-Wireless/blob/104818448c758a6e8a5270a8c9ae80c04ac047d2/Gateware/icestorm/Makefile#L26),
    or set the way-to-generic `TOOLS` environment variable with the right value.

    ```sh
cd ~/Downloads
wget https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2022-12-26/oss-cad-suite-linux-x64-20221226.tgz
sudo mkdir -p /opt/openfpga/
cd /opt/openfpga
sudo tar xfvz ~/Download/oss-cad-suite-linux-x64-20221226.tgz
sudo mv oss-cad-suite/ fpga-toolchain
    ```

* Install a (another) RISC-V toolchain

    The [ICE-V Gateware directory](https://github.com/ICE-V-Wireless/ICE-V-Wireless/tree/main/Gateware)
    contains 2 designs: `riscv` and `spi_pass`.

    The `spi_pass` design is the trivial SPI pass-through firmware that is loaded when the
    ESP32C3 wants to preload the PSRAM. (See earlier.)

    The `riscv` compiles into the default bitstream when you initially receive the board. It makes the LED cycle
    through all the colors of the rainbow. This design is quite complex. It even includes a RISC-V soft CPU.
    The build flow needs a RISC-V GCC compiler to generate the firmware for this example design.

    In theory, you should be able to reuse the RISC-V compile that's used to compile the ESP32C3 firmware, but
    that's not what's done here. The Gateware instructions suggest to use the 
    [pre-compiled August 2019 RISC-V toolchain from SiFive](https://github.com/sifive/freedom-tools/releases/tag/v2019.08.0):

    ```sh
cd ~/Downloads
wget https://static.dev.sifive.com/dev-tools/riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-linux-ubuntu14.tar.gz
sudo mkdir -p /opt/riscv-gcc
cd /opt/riscv-gcc
sudo tar xfvz ~/Downloads/riscv64-unknown-elf-gcc-8.3.0-2019.08.0-x86_64-linux-ubuntu14.tar.gz
    ```

* Build the RISC-V example

    ```sh
cd ~/projects/ICE-V-Wireless/Gateware/icestorm   
make
    ```

    You should see this after a minute or so:

    ```
Info: Program finished normally.
make -C ../riscv/c/ main.hex
make[1]: Entering directory '/home/tom/projects/ICE-V-Wireless/Gateware/riscv/c'
make[1]: 'main.hex' is up to date.
make[1]: Leaving directory '/home/tom/projects/ICE-V-Wireless/Gateware/riscv/c'
cp ../riscv/c/main.hex ./code.hex
/opt/openfpga/fpga-toolchain/bin/icebram rom.hex code.hex < bitstream.asc > temp.asc
/opt/openfpga/fpga-toolchain/bin/icepack temp.asc bitstream.bin
    ```

    A new `bitstream.bin` is waiting!

* Program the new bitstream into the ESP32C3 embedded flash

    ```sh
cd ~/projects/ICE-V-Wireless/Gateware/icestorm   
../../python/send_c3usb.py -f bitstream.bin
    ```

    Programming should only take a few seconds.

* Reset the board

    If all goes well, you should the newly flashed bitstream in action.

    To revert back to the default bitstream, you can do this:

    ```sh
cd ~/projects/ICE-V-Wireless/Firmware/spiffs   
../python/send_c3usb.py --flash bitstream.bin
    ```



# Conclusion

TBD

# References

* [ICE-V Wireless Zephyr Support](https://docs.zephyrproject.org/latest/boards/riscv/icev_wireless/doc/index.html)

# Footnotes

# XXX Scraps that must be deleted or embedded somewhere in the text

* All my instructions apply to an Ubuntu 20.04 installation.
* `/dev/ttyACM0` shows up right after plugging in.
* From the documentation:

    > Clone this repository or download the scripts and follow the documentation to get your board running on 
    > your WiFi network and begin communicating with it.

    There should be a link to "the documentation".

* Announces itself to the PC as follows:

    ```
Bus 001 Device 009: ID 0d8c:0103 C-Media Electronics, Inc. CM102-A+/102S+ Audio Controller
Bus 001 Device 021: ID 046d:c404 Logitech, Inc. TrackMan Wheel
Bus 001 Device 006: ID 0bda:5411 Realtek Semiconductor Corp. 4-Port USB 2.0 Hub
Bus 001 Device 029: ID 303a:1001                <<<<<<<<<<
Bus 001 Device 007: ID 0957:0718 Agilent Technologies, Inc. 
Bus 001 Device 005: ID 05e3:0610 Genesys Logic, Inc. 4-port hub
Bus 001 Device 004: ID 0b05:1939 ASUSTek Computer, Inc. AURA LED Controller
    ```

    You can only figure this out by plugging in and out, and checking the difference.
    Isn't it possible to give this a name? 

* Is it necessary to create a /etc/udev/rules.d file? Not clear...
* Boot button: 

    > Hold down while pressing the Reset button to put the ESP32C3 into bootloader mode. Can also be used without the Reset 
    > button for other firmware purposes.

    This should be in the Getting Started instructions, not in a "What's on the board" features list.

    Also, what does "put the ESP32C3 into bootloader mode" mean? Do I need to do that when I'm running the
    `send_c3usb.py` scripts?
* `--help` for `send_c3usb.py` says `--flash=<file>` but that doesn't work. It should be `--flash <file>` which
  goes against the standard getopt conventions.
* Directory structure inconsistent:  

    ./Gateware has ./icestorm directory to build ./riscv. But to build ./spi_pass, you need to go
      into ./spi_pass. Why is ./icestorm not under ./riscv?

