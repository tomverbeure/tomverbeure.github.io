

# Architecture

  The AMIQ signal generation board has a CPLD and 2 FPGAs. The information above
  determines which one is used. For whatever reason, R&S decided that it wasn't
  worth having some PC readable configuration register to make that automatic.

1. 

The embedded AMIQ application runs on DOS4GW on top of DR-DOS. The official way to 


XXX When using the official installation way, `B.OUT` got replaced by `NONE.OUT` in
`B.CFG`.


# Configuring the Digital Logic of the Signal Generation PCB

When trying to get the firmware to work, I found it useful to understand how the signal generation PCB
interacts with the motherboard. And for that, you need to know how various FPGAs and CPLDs are
interconnected.

There are 3 programmable logic chips on the PCB:

* Sequencer FPGA

  This Altera EPF10K10 Flex10 FPGA is, found on sheet 7 of the schematics, resonsible for general 
  PCB management. Like all FPGAs, its bitstream is volatile so a new configuration is required after 
  each power-up. 
  Unlike most FPGA boards, there is no bitstream configuration flash on the PCB: the FPGA is set
  to "passive parallel asynchronous: configuration mode and bitstream is loaded by the PC over the 
  ISA bus each time.

* BER FPGA

  Another Altera EPF10K10 Flex10 FPGA, located on sheet 28 of the schematic. This FPGA is primarily
  responsible for controller the bit error rate (BER) external interface. This feature is only
  supported when optoin AMIQ-B1 is enabled, but the FPGA is always there. In fact, even with 
  the BER option disabled, the FPGA is still responsible for driving the JTAG interface to used
  to configure the controller CPLD.

  Like the sequencer FPGA, this one is also configure at bootup over the PC ISA bus.

* controller CPLD

  This chip, Altera EPM7128 CPLD, primarily drives the SDRAM pins, so it's a good guess that the full name
  is SDRAM controller. CPLDs tend to have much less logic resource but back when they were popular, they
  were definitely faster than FPGAs.

  CPLDs will retain their configuration between power on. The controller CPLD is only programmed once
  during the initial device setup. 

  Programming happens over JTAG. The JTAG pins are driven by BER FPGA.

The `AMIQ` directory of the R&S `PREPARE` recovery disk contains all the FPGA and CPLD configuration files:

```
tom@zen:/media/tom/14E4-1358/AMIQ$ ll
total 166
drwxr-xr-x 2 tom tom   512 Apr 29  1999 ./
drwxr-xr-x 5 tom tom  7168 Dec 31  1969 ../
-rwxr-xr-x 1 tom tom 11942 Mar  2  1999 AMIQINIT.EXE*
-rw-r--r-- 1 tom tom  2352 Jun  1  1999 B.LZH
-rw-r--r-- 1 tom tom 15757 Jun  1  1999 CONT_02.LZH
-rw-r--r-- 1 tom tom 15724 Jun  1  1999 CONT_03.LZH
-rw-r--r-- 1 tom tom 16623 Jun  1  1999 CONT_04.LZH
-rwxr-xr-x 1 tom tom 76900 Jan 24  1999 LOADCON.EXE*
-rw-r--r-- 1 tom tom  6886 Oct 25  1999 SEQ_02.LZH
-rw-r--r-- 1 tom tom  6886 Oct 25  1999 SEQ_03.LZH
-rw-r--r-- 1 tom tom  6984 Oct 25  1999 SEQ_04.LZH
```

* `CONT_*.LZH` are the compressed SVF files for the control CPLD. There are 3 AMIQ version, 02,03 and 04, each
  with a unique file. During installation, one of this files is uncompressed into a `CON_*.SVF` file and then
  renamed to `CONTROLS.SVF`. `LOADCON.EXE` is the utility that does the programming. 

* Like the control CPLD, there are 3 bitstreams `SEQ_*.LZH` for the sequencer FPGA. One of the files gets
  uncompressed and renamed to `S.OUT`. There is only 1 bitstream version of the BER FPGA:
  `B.LZH`. It gets decompressed and renamed to `B.OUT. `AMIQINIT.EXE` is used to send the `S.OUT` and
  `B.OUT` bitstreams to the FPGAs.

You may see this error on your AMIQ-connected VGA monitor:

```Error: 243, “AMIQ variant check failed;Board-ID 155: Bit:24/24 Version:05/06”```

This is guaranteed to be a case of using the wrong SEQ bitstream or CONTROL configuration file.

If you have an AMIQ for which the HD has been installed the official way, you'll find
a `S.OUT`, `B.OUT` and `CONTROL.SVF` file in the `C:\AMIQ` directory. The `SEQ_*.LZH` files
will be there as well, but the `CONT_*.LZH` won't be. The `PREPARE` installation should
has all versions of them though.


# Recapping Tools

25 year old PC motherboards already used complex multi-layer PCBs, so they're not the best 
practice ground for beginners like me, but Santa had given me a desoldering station and
I was eager to try it out.

![Workbench with recapping tools and motherboard](/assets/amiq/restauration/recapping_items.jpg)

Here are the tools that I used:

* Yihua 948 desoldering station

  It has a hollow iron and electrical air pump. Great to remove the solder from
  through-hole contact with thicker leads, but not very useful for smaller caps.

* Pinecil soldering iron

  I used this more than the desoldering station. 

* Engineer Solder Sucker

  This thing is amazing. More expensive than cheaper solder suckers, but the silicone
  tip makes all the difference.

* Fake Amtech flux with a syringe plunger
* Solder wick braid
* Solder wire
* Ceramic tweezers
* Isopropyl alcohol
* Medical swab sticks

# Desoldering Techniques Learned Along the Way

Recapping is a pretty common process and you can find plenty of videos on YouTube about it.

Here are some random notes about techniques that I learned along the way:

* Temperature >350C

  I used a temperature of 350C and higher. A PC motherboard has a lot of copper layers that
  channeling away the heat of a soldering iron. Some capacitors were easy to
  remove and to replace. Others were a total pain: they just didn't want to come loose. I 
  think the difference is primarily due to the amount of copper closeby.

* Opening up the through-hole completely is rare

  In an ideal world, you are able to suck enough solder out of the through-hole so that the
  hole opens up and you can simply insert a replacement cap back and and solder it. 
  In practice, that rarely happened.
  Larger caps such as the 1000uF and 1500uF ones have thicker leads and a larger through-hole
  diameter. For those, there is a decent chances that at least one of the hole will free up,
  but I never had a case where both holes were open.

* The hollow tip of the desoldering pump

  One of the nice benefits of the heated desoldering pump was that the tip is hollow so it will
  immediately warm up the solder around the whole lead, instead of heating it up at one side
  only.

  It helps to wiggle around the hot tip in circles to loosen up the solder all around.

* Desoldered all the old caps intact vs cutting them off

  If you want to remove a cap without destroying it, you need to alternate between the 2
  leads and gradually extract the cap a millimeter or 2 at a time while applying an alternating
  force. When doing so, you run the risk of stripping away the copper lining of through-hole.

  I removed all caps intact, but in hindsight that was a mistake. The alternative is to just
  cut the old cap off the motherboard with micro wire cutter and then desolder the 2 leads
  one by one. This isn't always the best solution, e.g. when then cap is located in a small
  space between connectors, having the cap in place where desoldering it gives you something
  to grip on.

* Adding solder before removing it

  Adding fresh solder to a joint before removing it can do wonders. The extra solder can
  increase the contact surface between the solder and the soldering iron tip and make the solder
  heat up much easier. I didn't use it, but you can buy special solder with a low melting
  temperature to make desoldering even easier.

* Making use of gravity

  For small capacitors with small lead spacing such as the 10uF and 100uF caps, the desoldering
  pump wasn't very useful. I had best results by adding enough new solder so that it bridged both
  leads. After heating it up the single blog, the cap would often just fall out. Gravity for the win!

* Immediately replacing a removed capacitor with a new one

  Instead of first removing all capacitors and then adding the new ones, I immediately replaced
  an old one with the new one. This makes it much harder to make a mistake.

# Installing New Caps

When you can't unclog a solder hole, inserting a new cap isn't as easy. Here are some techniques that
I used.

I shorten the leads first and make one lead around 2mm shorter than the other. The longest lead is
obviously the one I want to put in place first. When there are no nearby obstacles that limit my
ability to maneuver the cap, I make the longest lead around 5mm and the shorter one around 3mm. Shorter
leads reduce that chance that they will buckle when you're putting a bit of pressure on them to get them
through the hole.

If there are nearby connectors or other components, I makes the leads as long as they need to be so that
the cap rises above its surroudings before it's inside the hole. The chance to buckle a lead is higher
now, but at least your fingers will have something to grip on.

You'll be holding 3 things at the same time: the soldering iron on one side of the PCB, the PCB itslef and
the new cap on the other side, which is a little bit of a challenge with only 2 hands.

Since you'll be looking on the side of the soldering iron, you don't have the luxury to monitor the placement
of the cap. For this reason, you need to make sure that the residual solder after removing the old cap doesn't
bulge but is slightly sunken into the hold. This way, when you place the longer lead of the cap on the PCB,
it will stay there and not glide off. Use soldering wick on the component side of the PCB to remove excess
solder if the solder is bulging out of the hole.

Here's an example of that: the holes of the left cap have already been wicked and are indented. Those of the
right cap have solder bulging out.

With the longer lead positions inside the indented hole, it's time to heat up that hole from the other side.
An indented hole usually means that there's not a lot of solder in the full at all, so I use a fine tipped
soldering iron and poke it perpendicalar into the hole to reach the solder. Soon the lead will shoot
through the hole. This is the point where I'll add more solder to this hole so that it's easier to
heat up the solder.

You now need to get the second lead in. If the distance between the 2 holes is small enough, you can heat
the solder of both holes at the same time but squeezing your iron between the 2 holes, just like you could
when using the gravity method to remove small caps.

If that's not possible, you'll have to alternate between the two leads and gradually work the capacitor
into its position.


# Disassembly

* Remove 4 back feet
* Slide case away
* Cut zip ties
* Unplug 2 flat cables
* Unplug power cable
* Unscrew 4 screws of CPU fan
    * 12V neolec. Screw holes: 33x33mm
* Unplug memory stick: 8x 48LC8M8A2 8MByte per chip -> 64MByte total
* Loosen 4 screws for the motherboard back holding bracket and slide it back
* Unplug speaker cable
* Remove 3 motherboard holding screws
* Remove 6 hex screws for the parallel port, RS232 and X13 connector
    * The motherboard is now loose.
    * It's an [MSI MS5179](https://groups.io/g/Rohde-and-Schwarz/topic/r_s_amiq_generator_need/52310294)
    * [The Retro Web](https://theretroweb.com/motherboards/s/msi-ms-5169-al9)
    * size: 300x
* Lift the motherboard from the left
* Unplug the 2 flat cables on the right
* Unplug right cable with blue and red wires
* Remove heat sink from CPU: push down on the metal clip close to the DRAM slots
    * Remove CPU
* Remove ISA extension slot

Removing HD:
* Remove power cable attachment screw
* Remove 2 screws on aluminum HDD holding plate
* Disconnect cables
* Remove 2 HD attachment screws
* Slide out HD
* Backup HD:
* `sudo apt install gddrescue`
* `ddrescue /dev/<src device> amiq-backup.img`

* Take motherboard out
* Plug in PCI card -> boot screen
* Replace CR2032

* Disk image through http://www.ko4bb.com/getsimple/index.php?id=manuals
* Compact Flash

```
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ sudo ddrescue -f amiq_hdd.img /dev/sda log
GNU ddrescue 1.23
Press Ctrl-C to interrupt
     ipos:    3253 MB, non-trimmed:        0 B,  current rate:   1003 MB/s
     opos:    3253 MB, non-scraped:        0 B,  average rate:   1084 MB/s
non-tried:        0 B,  bad-sector:        0 B,    error rate:       0 B/s
  rescued:    3253 MB,   bad areas:        0,        run time:          2s
pct rescued:  100.00%, read errors:        0,  remaining time:         n/a
                              time since last successful read:         n/a
Finished                                     
```

Took around 8 minutes even if 'Finished' showed up immediately.

# Booting up

* Plug in VGA GPU
    * ATI Rage XL 8MB PCI
    * $20.72 on eBay
* [PCI riser card](https://www.mini-box.com/s.nl/it.A/id.289/.f?sc=8&category=1549)
    * $3

* RAM test first
* Use keyboard with PS/2
* DEL key due RAM test to enter BIOS setup screen

# WinIQSim

* Start software
* ARB -> Select Target ARB ... -> AMIQ03
* ARB -> AMIQ -> AMIQ Interface and Transmission Options -> RS 232 -> Default baud rate: 115200
* ARB -> AMIQ -> Remote Control and BERT..

  This will try to access remote. See remote control window.

  * Test and Adjustment
  * Selftest
  * Send command: doesn't work

* quit WinIQSinm
* Putty
  * serial, com3, 115200
  * Terminal: 
    * Local echo: force on
  * Open
  * `*IDN?` -> ...
  
```
*RST
CLOCK 100MHz
ARM
TRIG
SClock EXTFAst   <- switches to external clock input
```

* Calibration of level and offset for I and Q

```
*RST
CAL:ALL?
```

Takes about 30s. Should return 0 if no error.

* Won't work when PCI VGA is not plugged in

  * This is because Primary Display is set to VGA/EGA in "Advanced CMOD Setup"
  * Set to "Absent"
  * After this, VGA card will still work when plugged in, but only in PCI slot
    that is closest to the CPU

* After bootup: "Error: 243, "AMIQ variant check failed;Board-ID 155: Bit:24/24 Vers 05/06"

# EEPROM

```
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ ./eeprom.py EEPROM_AMIQ02.BIN 
XOR result of all bytes in the file 'EEPROM_AMIQ02.BIN': 0xa5
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ ./eeprom.py EEPROM_AMIQ04.BIN 
XOR result of all bytes in the file 'EEPROM_AMIQ04.BIN': 0xa5
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ ./eeprom.py EEPROM_AMIQ04b.BIN 
XOR result of all bytes in the file 'EEPROM_AMIQ04b.BIN': 0xa5
```

```
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ xxd EEPROM_AMIQ02.BIN 
00000000: c200 0300 cc00 3832 3932 3933 2f30 3334  ......829293/034
00000010: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 0000 0000 0000 f03f  ...............?
00000030: a508 0008 5708 7e08 e907 3708 3c08 6408  ....W.~...7.<.d.
00000040: ce07 1c08 4007 4607 4c07 5107 5507 5807  ....@.F.L.Q.U.X.
00000050: 5c07 5e07 6007 6007 6107 6007 6007 5e07  \.^.`.`.a.`.`.^.
00000060: 5b07 5807 5507 5007 4c07 4607 4007 9109  [.X.U.P.L.F.@...
00000070: 7a09 7009 af08 440f 6608 1408 c007 e400  z.p...D.f.......
00000080: a207 b107 b407 c707 b607 c407 c807 da07  ................
00000090: fe06 0507 0b07 1007 1407 1807 1c07 1e07  ................
000000a0: 2007 2007 2107 2007 1f07 1d07 1a07 1707   . .!. .........
000000b0: 1407 0f07 0a07 0407 fd06 7209 5809 5109  ..........r.X.Q.
000000c0: 8e08 420f 6c08 1a08 c807 ec00            ..B.l.......
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ xxd EEPROM_AMIQ04.BIN 
00000000: 8f00 0300 cc00 3833 3832 3636 2f30 3234  ......838266/024
00000010: 0000 0000 0100 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 7e42 2c51 ac09 f03f  ........~B,Q...?
00000030: d705 0008 5d08 8508 7308 0008 6208 7f08  ....]...s...b...
00000040: 7608 0008 8206 8606 8a06 8e06 9106 9306  v...............
00000050: 9506 9606 9806 9806 9806 9806 9606 9506  ................
00000060: 9406 9206 8f06 8c06 8806 8406 8006 a609  ................
00000070: 9e09 8609 0008 8a0f 6c08 1608 c007 a000  ........l.......
00000080: 8708 1009 6508 0008 5208 d208 3208 0008  ....e...R...2...
00000090: 5606 5706 5806 5906 5a06 5a06 5b06 5b06  V.W.X.Y.Z.Z.[.[.
000000a0: 5c06 5c06 5c06 5b06 5c06 5a06 5a06 5a06  \.\.\.[.\.Z.Z.Z.
000000b0: 5a06 5906 5806 5806 5706 d409 cc09 b409  Z.Y.X.X.W.......
000000c0: 0008 880f 6808 1208 bc07 9e00            ....h.......
tom@zen:~/projects/tomverbeure.github.io/assets/amiq$ xxd EEPROM_AMIQ04b.BIN 
00000000: 3100 0300 cc00 3833 3832 3636 2f30 3234  1.....838266/024
00000010: 0000 0000 0100 0000 0000 0000 0000 0000  ................
00000020: 0000 0000 0000 0000 7e42 2c51 ac09 f03f  ........~B,Q...?
00000030: d705 0008 5d08 8508 7308 0008 6208 8008  ....]...s...b...
00000040: 7808 0008 7c06 8106 8606 8806 8c06 8e06  x...|...........
00000050: 9006 9206 9306 9406 9406 9306 9206 9006  ................
00000060: 8f06 8c06 8a06 8806 8406 8006 7c06 a609  ............|...
00000070: 9f09 8609 0008 8a0f 6a08 1408 be07 9f00  ........j.......
00000080: 8508 1109 6408 0008 5208 d308 3008 0008  ....d...R...0...
00000090: 5606 5606 5806 5806 5806 5a06 5a06 5a06  V.V.X.X.X.Z.Z.Z.
000000a0: 5a06 5a06 5a06 5a06 5a06 5906 5806 5806  Z.Z.Z.Z.Z.Y.X.X.
000000b0: 5806 5606 5606 5606 5406 d409 cb09 b409  X.V.V.V.T.......
000000c0: 0008 880f 6808 1208 bc07 9e00            ....h.......
```

# Extacting data from the SATA/IDE drive

The USB to SATA/IDE adapter is optional if you don't care about extracting the old HD data, 
but I don't think I'd have been able to complete the installation without 
this $8 [USB-to-CompactFlash adapter](https://www.amazon.com/dp/B08P517NW5?th=1) that I already
had laying around after my [Symmetricom S200](/2024/07/14/Symmetricom-S200-NTP-Server-Setup.html)
adventures.

![USB-to-CompactFlash adapter](/assets/s200/flash_card_reader.jpg)

I use `ddrescue` on Ubuntu Linux to create and write full disk images. 

To install it:

```sh
sudo apt install gddrescue`
```

To make a backup of a drive:

```sh
ddrescue /dev/<src device> amiq-backup.img
```

In my case, `<src device>` is `sda`. Use `df` to figure out the name of the drive that's connected
to your USB adapter.

To restore an image to a drive:

```sh
sudo ddrescue -f amiq_hdd.img /dev/sda log
```

```
GNU ddrescue 1.23
Press Ctrl-C to interrupt
     ipos:    3253 MB, non-trimmed:        0 B,  current rate:   1003 MB/s
     opos:    3253 MB, non-scraped:        0 B,  average rate:   1084 MB/s
non-tried:        0 B,  bad-sector:        0 B,    error rate:       0 B/s
  rescued:    3253 MB,   bad areas:        0,        run time:          2s
pct rescued:  100.00%, read errors:        0,  remaining time:         n/a
                              time since last successful read:         n/a
Finished                                     
```

Be careful: when restoring an image to a drive, `Finished` will show up immediately
even if the data is still being transfered to the drive.

# References

**Rohde & Schwarz documents**

* [R&S AMIQ Operating Manual](/assets/amiq/AMIQ_OperatingManual_en_08.pdf)
* [R&S AMIQ Service Manual with schematic](/assets/amiq/Rohde_Schwarz_AMIQ_Service_Manual_with_schematics.pdf)
* [R&S AMIQ Overview](/assets/amiq/AMIQ_overview.PDF)
* [R&S AMIQ Datasheet](/assets/amiq/Rohde-Schwarz-AMIQ04-Datasheet.pdf)

* [R&S Floppy Disk Control of the I/Q Modulation Generator AMIQ](/assets/amiq/amiq_floppy_disc_control.pdf)
* [R&S Software WinIQSIM for Calculating I/Q Signals for Modulation Generator R&S AMIQ](/assets/amiq/Software Manual WinIQSIM - ES Documentation.pdf)
* [R&S Creating Test Signals for Bluetooth with AMIQ / WinIQSIM and SMIQ](/assets/amiq/R&S - Creating Test Signals for Bluetooth with AMIQ.pdf)
* [R&S WCDMA Signal Generator Solutions](/assets/amiq/R&S - WCDMA Signal Generator Solutions.pdf)
* [R&S Golden devices: ideal path or detour?](/assets/amiq/R&S Golden devices - ideal path or detour.pdf)
* [R&S Demonstration of BER Test with AMIQ controlled by WinIQSIM](/assets/amiq/R&S - Demonstration of BER Test with AMIQ controlled by WinIQSIM.pdf)

**Other AMIQ content on the web**

* [Lost Manual - Rohde & Schwarz](https://www.lost-manuals.com/en/manufacturer/rohde-schwarz)
* [R&S Groups.io AMIQ repair thread](https://groups.io/g/Rohde-and-Schwarz/topic/r_s_amiq_generator_need/52310294)
* [EEVBlog repair discussion](https://www.eevblog.com/forum/testgear/harddisk-image-for-rs-amiq-generator/)
* [EEVBlog AMIQ license key comment](https://www.eevblog.com/forum/testgear/enabling-options-for-rs-test-equipment/msg3468382/#msg3468382)
* [EEVBlog AMIQ license key comment](https://www.eevblog.com/forum/testgear/enabling-options-for-rs-test-equipment/msg4626139/#msg4626139)
* [EEVBlog AMIQ + SFQ as vector signal generator](https://www.eevblog.com/forum/testgear/rs-smiq-as-a-replacement-for-a-general-signal-generator/msg5400308/#msg5400308)
* [How to get error out of AMIQ?](https://forums.ni.com/t5/UVLabVIEW/How-to-get-errors-form-R-amp-S-AMIQ/td-p/3639064)

* [zw-ix has a blog - Getting an Rohde Schwarz AMIQ up and running](https://zw-ix.nl/blog/2021/02/09/getting-an-rohde-schwarz-amiq-up-and-running/)
* [zw-ix has a blog - Connecting a Rohde Schwarz AMIQ to a SMIQ04](https://zw-ix.nl/blog/2021/02/09/494/)

* [Bosco tweets](https://x.com/BoscoMac/status/1860000781128380629)

** DDS Clock Synthesis**

* [MT-085 Tutorial: Fundamentals of Direct Digital Synthesis (DDS)](https://www.analog.com/media/en/training-seminars/tutorials/MT-085.pdf)
* [How to Predict the Frequency and Magnitude of the Primary Phase Truncation Spur in the Output Spectrum of a Direct Digital Synthesizer (DDS)](https://www.analog.com/media/en/technical-documentation/app-notes/an-1396.pdf)

**Recapping**

* [Choosing Capacitors to Recap Old Electronics](https://www.youtube.com/watch?app=desktop&v=6PKaj9-1xIs&t=0s)
* [Six Common Mistakes Made When Recapping Vintage Electronics](https://www.youtube.com/watch?v=BeDKwi-GJRI)

**Related content**

* [The Signal Path - Teardown, Repair & Analysis of a Rohde & Schwarz AFQ100A I/Q (ARB) Modulation Generator](https://www.youtube.com/watch?v=6aRZGOcdGUE)
* [Analog Devices - Optimization of EVM Performance in IQ Modulators](https://www.analog.com/en/resources/technical-articles/optimization-of-evm-performance-in-iq-modulators.html)

    Uses an AMIQ in the test setup


# HD repair

* [Head Stack Replacement: Questions and Answers](https://hddguru.com/articles/2006.02.17-Changing-headstack-Q-and-A/)
* [HDDSurgery: HDDS HGST 2.5” Ramp Set](https://hddsurgery.com/data-recovery-tools/hdds-hgst-2-5-inch-ramp-set)
* [DonorDrives](https://www.donordrives.com/)
* [Clicking Noise? Causes and solutions?](https://forum.hddguru.com/viewtopic.php?f=16&t=7457)

# Footnotes

