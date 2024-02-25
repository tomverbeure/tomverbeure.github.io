---
layout: post
title:  "Hacking the eeColor Color3"
date:   2018-04-08 00:00:00 -1000
categories: 
---

I'm taking a short break from the BlackIce-II to spend some quality time in my garage with the eeColor color3. 
Originally a real consumer product built with a Cyclone 4 FPGA, a DRAM, an HDMI receiver and an HDMI transmitter, 
it got its 15 minutes of fame when it was 
[featured on Hackaday](https://hackaday.com/2013/05/08/hdmi-color-processing-board-used-as-an-fpga-dev-board-to-mine-bitcoins/) 
as a potentially really cheap FPGA development board. 

[A few people](http://www.taylorkillian.com/2013/04/using-fpga-of-eecolor-color3.html) mapped out the IOs of the FPGA 
and built a bitcoin miner with it, but I'm not aware of any projects that are using all the features of the board.

Today, most color3 boxes sell for $20 and more (+shipping) on eBay or Amazon, but I was able to grab one for just 
$10+shipping.

It'd be a shame if the scattered reverse engineering information of the color3 that can be found on the web would 
disappear due to standard web-rot, so I've started [a Hackaday project](https://hackaday.io/project/122480-eecolor-color3) 
and a [GitHub page](https://github.com/tomverbeure/color3) to gather all the information I can find today, and, 
hopefully, also document my own progress in getting all the chips to work.

![Color3 Annotated PCB]({{ "/assets/eecolor_color3/color3_PCB_marked.jpg" | absolute_url }})


# References

All posts in this series:

* [Hacking the eeColor Color3](/2018/04/08/Hacking-the-eeColor-Color3.html) 
* [eeColor Color3: Getting Ready for Reverse Engineering](/2018/04/09/Color3-Getting-Ready-for-Reverse-Engineering.html)
* [eeColor Color3: SiI9136 and SiI9233 Connections to FPGA](/2018/04/11/Color3-Sil9136-and-Sil9233-Connections-to-FPGA.html)
* [eeColor Color3: HDMI TX is Up!](/2018/04/15/Color3-HDMI-TX-is-Up.html)
* [eeColor Color3: SiI9233 and SiI9136 I2C Traces](/2018/04/22/Color3-Sil9233-and-Sil9136-I2C-Traces.html)
* [eeColor Color3: HDMI RX to HDMI TX is UP!!!](/2018/04/23/Color3-HDMI-RX-to-HDMI-TX-is-UP.html)
