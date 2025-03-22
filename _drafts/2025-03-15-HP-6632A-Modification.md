---
layout: post
title: HP 6632A Modification
date:   2025-03-15 00:00:00 -1000
categories:
---

* TOC
{:toc}

* Works fine, but loose wires for the fan
* Fan control circuit: page 93 of 117, page 6-3, figure 6-1
* According to the schematic, the middle pin of XT1P5 should be 12V. 
  * I measure 14.4V.
  * voltage across zener is also 14.4V
  * Why is there no 1.4V drop between B and E?

* Fan: AD0612HB-A72GL
  * 3 wires: 12V, 0V, locked
  * locked has an open drain transistor that pulls the pin low when
    the fan isn't rotating.
  * mounted with label towards the heatsink so that air is pushed
    from inside the case to the back

* Replacements:

  * Darlington transistor Q119
    * 15V UNREG is actually 24V 
    * 12V drop across transistor
    * brushless fan is 0.23A
    * 2.76W consumed in Q119
    * Digikey has the max power of listed sometimes for
      heatsink (Tc) and sometimes without (Ta). When using
      Tc, it's almost always more than 50W. For Ta it's
      usually 2W or less.
    * [TIP121]](https://www.digikey.com/en/products/detail/stmicroelectronics/TIP121/603562) seems
      like a decent choice.
  * Alternative: 3.3V Zener diode in series?
    * 0.76W
    * [1N5333BG](https://www.digikey.com/en/products/detail/onsemi/1N5333BG/1474069)

* Fan connector
  * Header [Molex 0022272031](https://www.digikey.com/en/products/detail/molex/0022272031/1130578)
    * HP number: 1252-0063
  * Matching connector [Molex 0022013037](https://www.digikey.com/en/products/detail/molex/0022013037/26433)
  * Matching connector with cable [Molex 2177961031](https://www.digikey.com/en/products/detail/molex/2177961031/14637927)

* Fan itself:
  * 60x60
  * >23 CFM (because that's what the existing replacement fan had)
  * [CFM-6025V-145-270](https://www.digikey.com/en/products/detail/same-sky-formerly-cui-devices/CFM-6025V-145-270/7605498)
    * 12VDC - range: 4.5V to 13.8V
    * 23CFM
    * 1.05W
    * 27.0 dB/A (instead of 32.3 dB/A)

* Speed regulator
  * [TL431CLP](https://www.digikey.com/en/products/detail/texas-instruments/TL431CLP/276230)

# References

* [HP 6633A System DC Power Supply Repair - No.1130](https://www.youtube.com/watch?v=CSk07ToKTdA)

    Capacitor replacement, power switch fix, replacing some fuses.

* [HP 6633A System DC Power Supply Upgrades - No.1136 ](https://www.youtube.com/watch?v=7BTqajU44pY)

    Installs front terminals, fan temperature control

* [EEVblog forum - HPAK 6632A / 6633A / 6634A 100W System PSU - Teardown & MODs](https://www.eevblog.com/forum/testgear/hpak-6632a-6633a-6634a-teardown-mods/)

    Source for all the mods that were done in the video above.

* [AliExpress - binding posts that were used in the YouTube mod](https://www.aliexpress.us/item/3256803763737026.html)

    Original HP part: 1510-0091 

* [Repair of a Hewlett-Packard 6632A, output voltage in error and drifts, display v](https://www.eevblog.com/forum/testgear/repair-of-a-hewlett-packard-6632a-output-voltage-in-error-and-drifts-display-v/)

  Fixes a leaking capacitor. But in the comments, somebody mentions using
  an [AliExpress control board](https://www.aliexpress.us/item/3256803003660496.html) 
  to regulate the fan speed. But it's not clear if this requires the fan to have a PWM
  input signal?


