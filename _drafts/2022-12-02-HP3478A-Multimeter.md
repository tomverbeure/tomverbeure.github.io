---
layout: post
title: HP 3478A Multimeter Capacitor and Battery Replacement
date:  2022-12-02 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Calibration Data Backup over GPIB

* [EEVblog forum: HP 3478A: How to read/write cal SRAM](https://www.eevblog.com/forum/repair/hp-3478a-how-to-readwrite-cal-sram/)
* [hp3478a_utils](https://github.com/fenugrec/hp3478a_utils)
    * [Format of calibration parameters](https://www.eevblog.com/forum/repair/hp-3478a-how-to-readwrite-cal-sram/msg1966463/#msg1966463)
* [HP3478Ctrl](https://github.com/pigrew/HP3478Ctrl)
* [hp3478a-calibration](https://github.com/steve1515/hp3478a-calibration)
* [HP3478A instrument control software](https://mesterhome.com/gpibsw/hp3478a/index.html)

![schematic of calibration RAM logic](/assets/hp3478a/calibration_ram.png)

![schematic of battery circuit](/assets/hp3478a/battery_circuit.png)

For my unit, this script returns the following values:

```
0000: 40 40 40 40 43 40 48 42 4f 44 44 40 4d 4b 40 40  @@@@C@HBODD@MK@@
0010: 40 40 43 43 42 4f 45 43 40 4e 40 40 40 40 40 40  @@CCBOEC@N@@@@@@
0020: 43 42 4f 44 40 40 4e 47 49 49 49 49 49 47 42 40  CBOD@@NGIIIIIGB@
0030: 4f 43 4c 4a 4b 49 49 49 49 49 49 42 40 4e 4f 4e  OCLJKIIIIIIB@NON
0040: 49 4c 40 40 40 40 40 40 40 40 40 40 40 4f 4f 49  IL@@@@@@@@@@@OOI
0050: 49 48 46 40 49 42 4e 4e 40 4c 4a 4c 49 49 49 49  IHF@IBNN@LJLIIII
0060: 49 45 41 4c 40 45 4e 4a 4d 49 49 49 49 49 48 41  IEAL@ENJMIIIIIHA
0070: 4c 41 4f 41 4a 4c 40 40 40 40 40 40 41 4c 4f 43  LAOAJL@@@@@@ALOC
0080: 40 4e 40 49 49 49 49 49 49 41 4c 4d 42 4e 49 4f  @N@IIIIIIALMBNIO
0090: 49 49 49 49 49 49 41 4c 4d 44 42 4a 49 49 49 49  IIIIIIALMDBJIIII
00a0: 49 49 49 41 4c 4e 4c 4d 49 45 49 49 49 49 49 49  IIIALNLMIEIIIIII
00b0: 41 4c 42 41 4f 4a 4a 40 40 40 40 44 42 43 40 40  ALBAOJJ@@@@DBC@@
00c0: 43 4c 4e 47 40 40 40 40 40 44 43 40 41 4c 43 4e  CLNG@@@@@DC@ALCN
00d0: 48 40 40 40 40 40 40 40 40 40 40 40 4f 4f 49 49  H@@@@@@@@@@@OOII
00e0: 48 46 40 49 43 4e 43 41 41 4c 40 40 40 40 40 40  HF@ICNCAAL@@@@@@
00f0: 40 40 40 40 40 40 4f 4f 40 40 40 40 40 40 40 40  @@@@@@OO@@@@@@@@
```
 

# Various

* Works by charging a capacitor and measuring time (according to EEVblog video)

# References

* [EEVblog teardown](https://www.youtube.com/watch?v=9v6OksEFqpA) 
* [HP 3478A Multimeter Repair and Test](https://www.youtube.com/watch?v=e-itiJSftzs)
* [Tony Albus HP 3478A Multimeter Teardown](https://www.youtube.com/watch?v=q6JhWIUwEt4)
* [Datasheet](https://accusrc.com/uploads/datasheets/agilent_hp_3478a.pdf)
* [HP Journal](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1983-02.pdf)

    Contains technical description.

* [Discussion on EEVblog](https://www.eevblog.com/forum/beginners/is-190$-a-bargain-for-a-hp-2378a-bench-multimeter/)

    "3478 are not bad but they are virtually unrepairable if they break. Especially the display is unobtainium..."

* [Service Manual](http://www.arimi.it/wp-content/Strumenti/HP/Multimetri/hp-3478a-Service.pdf)
* [Battery replacement article](http://mrmodemhead.com/blog/hp-3468a-battery-replacement/)

* [Boat Anchor Manual Archive](https://bama.edebris.com)

