
* 0001 - Xilinx clone - 30MHz
    * Device detection not great.
    * bitstream loads successfully

* 0002 - Xilinx clone - 30MHz
    * 142ms loading time
    * Setting time to 60MHz has no effect: still stays at 30MHz
    * Setting time to 24MHz: 
        * Clock is now 15MHz.
        * Loading time: 265ms
        * Readback is fine now.
    * Setting time to 13MHz:
        * Loading time: 388ms
        * Clock is now 10MHz.

* 0003 - Altera FT245+CPLD Clone
    * 6MHz
    * Bitstream loads successfully
    * Loading time 980ms

* 0004 - Altera FT245+CPLD Clone
    * Bursts of 7.20ms with then a pause in between
    * No way to change clock speed

* (no slide) - Altera PIC Clone
    * Load time 1.42s
    * Bitstream loads successfully

* 0005 - Altera PIC Clone
    * Bit clock 12MHz
    * Byte period: 2.16us / 462kHz


( not slide)
* Terasic Altera Clone
    * Exactly the same behavior as CPLD Clone.
    * Load time 980ms.

* 0006 - Altera USB-Blaster II
    lsusb:
    Bus 002 Device 003: ID 0bda:8153 Realtek Semiconductor Corp. 
    Bus 002 Device 002: ID 0bda:0411 Realtek Semiconductor Corp. 
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 001 Device 003: ID 045e:07a5 Microsoft Corp. Wireless Receiver 1461C
    Bus 001 Device 002: ID 8087:0a2b Intel Corp. 
    Bus 001 Device 043: ID 09fb:6010 Altera 
    Bus 001 Device 034: ID 0bda:5411 Realtek Semiconductor Corp. 
    Bus 001 Device 004: ID 046d:c404 Logitech, Inc. TrackMan Wheel
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

    Open On-Chip Debugger 0.10.0+dev-00930-g09eb941 (2019-09-16-21:01)
    Licensed under GNU GPL v2
    For bug reports, read
    	http://openocd.org/doc/doxygen/bugs.html
    Info : only one transport option; autoselect 'jtag'
    xc6s_print_dna
    Info : Altera USB-Blaster II found (Firm. rev. = 1.27)
    Info : This adapter doesn't support configurable speed
    Info : JTAG tap: xc6s.tap tap/device found: 0x44002093 (mfg: 0x049 (Xilinx), part: 0x4002, ver: 0x4)
    Warn : gdb services need one or more targets defined

    
    * Load time 236ms.

* 0007 - Altera USB-Blaster II

    * 24MHz
    * Very clean signal, even if not measured exactly at the pin
    * No way in openocd to change clock speed

* 0008 - Olimex ARM-USB-TINY-H

    Bus 001 Device 044: ID 15ba:002a Olimex Ltd. ARM-USB-TINY-H JTAG interface

    * 143.6ms load time.
    * Bitstream loads fine
    * Reading data back fine.

* 0009 - Olimex ARM-USB-TINY-H

    * 30MHz
    * Not super clean, but good enough.

* (no slide) - ARM-USB-TINY-H

    * 15MHz
    * Behaves identical to Xilinx clone


* (no slide) - Olimex ARM-USB-OCD-H

    * 30MHz
    * Bitstream load fails.
    * Reading data didn't work.

* 0010 - Olimex ARM-USB-OCD-H

    * Changing voltage envelope on TCK

* 0011 - Olimex ARM-USB-OCD-H

    * Changing voltage envelope on TCK.
    * Only starts working around 2kHz.

* 0012 - Segger J-Link PLUS Clone

    Bus 001 Device 049: ID 1366:0101 SEGGER J-Link PLUS

    * 'interface jlink'
    * 3.24s load time (with 2MHz clock setting!)

* 0013 - Segger J-Link PLUS Clone

    * 'interface jlink'
    * 2.04s load time (with 30MHz clock setting)
    * Actual speed is 12MHz

* 0014 - Segger J-Link PLUS Clone

    * huge gaps between maxi-bursts

* 0015 - Segger J-Link PLUS Clone

    * huge gaps between mini-bursts


