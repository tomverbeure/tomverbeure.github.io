---
layout: post
title: Minisplit Repair
date:   2024-10-07 00:00:00 -1000
categories:
---


# References

Unit: MSZ-GL12NA-U1

* [Service manual](https://www.mitsubishitechinfo.ca/sites/default/files/SH_MS%28Y%29%28Z%29-GL09_24NA_OBH732D.pdf)
* [Parts list](https://www.mitsubishitechinfo.ca/sites/default/files/Parts_MS%28Y%29%28Z%29-GL06_24NA_OBB732E.pdf)



* First checked voltage on external unit
* Checked voltage on internal S1/S2/S3 connector: 120V between each of the 3 and ground.
* There's an external power switch: useful. Ugly, but required by local code.
* section 5: wiring diagram

    * There are different diagrams for U1 and U2 version.
    * in diagram, CN211 is drawn upside down to reality! Wire order top to bottom is
      blk, blu, ylw, ... red instead of the opposite!

* section 9-7 test point diagram and voltage

    * measure fuse
    * CN211 pin 1 is connected to right side of ZD111
    * CN211 pin 3 (high voltage GND) is also accessible as the stripped wire JP3 to the right of the big capacitor
      It is NOT available on JP6, the GND wire!
    * 0V on the 5V line
    * 32V on pin 1 (instead of 300V)
    * R111 can be measured between top of diode D101 and top of diode D121. Should be 4 Ohm. MAKE SURE POWER IS OFF !!!

* section 9-3: follow flow-chart. In my case: 

  * indoor unit does not receive signal from remote controller
  * indoor unit does not operate when emergency operation switch is pressed.
  * indoor/outoodr connecting wire has power
  * go to section 9-6 section C: check of indoor PC board and indoor fan motor


* section 10-1: disassembly
    

