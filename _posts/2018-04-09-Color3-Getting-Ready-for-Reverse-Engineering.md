---
layout: post
title:  "eeColor Color3: Getting Ready for Reverse Engineering"
date:   2018-04-09 00:00:00 -1000
categories: 
---

Today was all about getting set up for reverse engineering the board connections.

The SDRAM, LEDs, buttons, and FTDI chip connections have already been figured out in the past by 
[Taylor Killian](http://www.taylorkillian.com/2013/04/using-fpga-of-eecolor-color3.html) but the Silicon Image 
chips have not. And those chip are really what makes this board so interesting.

The SI chips are using a TQFP package, which makes it easier to figure out the connections from those chips to the FPGA.

Here's one way of doing it: 

* create an FPGA design with a large input bus
* let Quartus assign all those signals at random. (Known IOs are already assigned to their correct position)
* connect these input pins to a SignalTap
* run SignalTap in continuous trigger mode
* touch the pins of the TQFP packages with a wire that's connected to VDD or GND through a resistor.
* check on SignalTap if some of the wires are wiggling. If they do, you've found your next connection!
* update the pin assignment table in Quartus for this new IO, and repeat until everything has been figured out.

Right now, the minimal design with the SignalTap synthesizes, but I'm not able to program the FPGA with my dirt cheap 
knock-off USB Blaster interface. Sometimes Quartus is able to identify the FPGA, sometimes not.

When I connect the USB Blaster dongle to my EP2C5 mini board, it's working fine, so tool permissions etc should be OK.

I think it's a matter of signal integrity of the USB Blaster clone. 

Tomorrow, I'll try again with a high quality Terasic USB Blaster clone that we use at work.

# References

All posts in this series:

* [Hacking the eeColor Color3](/2018/04/08/Hacking-the-eeColor-Color3.html) 
* [eeColor Color3: Getting Ready for Reverse Engineering](/2018/04/09/Color3-Getting-Ready-for-Reverse-Engineering.html)
* [eeColor Color3: SiI9136 and SiI9233 Connections to FPGA](/2018/04/11/Color3-Sil9136-and-Sil9233-Connections-to-FPGA.html)
* [eeColor Color3: HDMI TX is Up!](/2018/04/15/Color3-HDMI-TX-is-Up.html)
* [eeColor Color3: SiI9233 and SiI9136 I2C Traces](/2018/04/22/Color3-Sil9233-and-Sil9136-I2C-Traces.html)
* [eeColor Color3: HDMI RX to HDMI TX is UP!!!](/2018/04/23/Color3-HDMI-RX-to-HDMI-TX-is-UP.html)
