---
layout: post
title: HP Laptop 17 RAM Upgrade
date:   2025-02-22 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I do virtually all of my hobby and home computing on Linux and MacOS. The MacOS
stuff on a laptop and almost all Linux work a desktop PC. The desktop PC has Windows 
on it installed as well, but it's too much of a hassle to reboot so it never gets used 
in practice. 

Recently, I've been working on a project that requires a lot of Spice simulations.
[NGspice](https://ngspice.sourceforge.io) works fine under Linux, but it doesn't come
standard with a GUI and, more important, the simulation often refuse to converge
once your design becomes a little bit bigger.

![Laptop with Kicad](/assets/hp17upgrade/laptop_with_kicad.jpg)

Tired of fighting against the tool, I switched to [LTspice](https://ez.analog.com/design-tools-and-calculators/ltspice) 
from Analog Devices. It's free to use and while it support Windows and MacOS in theory, 
the Mac version is many years behind the Windows one and nearly unusuable.

After dual-booting into Windows too many times, a Best Buy deal appeared on my
[BlueSky](https://bsky.app) timeline for an HP laptop for just $330. The specs
were pretty decent too:

* AMD Ryzen 5 7000
* 17.3" 1080p screen
* 512GB SSD
* 8 GB RAM
* Full size keyboard
* Windows 11

Someone at the HP marketing departement spent long hours to come up with a suitable name
and come up "HP Laptop 17".

I generally don't pay attention to what's available on the PC laptop market, but it's hard to
really go wrong for this price so I took the plunge. Worst case, I'd return it.

We're now 8 weeks later and the laptop is still firmly in my possession. In fact, I've used 
it way more than I thought I would. I haven't noticed any performance issues, the screen is pretty
good, the SSD larger than what I need for the limited use case, and, surprisingly, the
trackpad is the better than any Windows laptop that I've ever used, though that's not a high
bar. It doesn't come close to MacBook quality, but palm rejection solid and it's seriously
good at moving the mouse around in CAD applications. 

The two worst parts about it are the keyboard and the limited amount of RAM: 8GB is on the
low side. I can honestly not quantify it whether or not it has a practical impact, but I decided 
to upgrade it anyway. In this blog post, I go through the steps of doing this upgrade.

**Important: there's a good chance that you will damage your laptop when trying this upgade and
almost certainly void your warranty. Do this at your own risk!**

# Selecting the RAM

The laptop wasn't designed to be upgradable and thus you find any official resources about
it. And with such a generic name, there's guaranteed to be multiple hardware versions of the same 
product. To have reasonable confidence that you're buying the correct RAM, check out the 
full product name first. You can find it on the bottom:

Mine is an *HP Laptop 17-cp3005dx*. 

There's some conflicting information about being able to upgrade the thing. The 
[BestBuy Q&A section](https://www.bestbuy.com/site/questions/hp-17-3-full-hd-laptop-amd-ryzen-5-8gb-memory-512gb-ssd-natural-silver/6587274/question/50bf44b8-35e1-3f97-8a82-93e23976ad8a)says the following:

> The HP 17.3" Laptop Model 17-cp3005dx RAM and Storage are soldered to the motherboard, and 
> are not upgradeable on this model.

This is flat out wrong for my device.

After a bit of Googling around, I learned that it has a single 8GB DDR4 SODIMM 260-pin RAM stick 
but that the motherboard has 2 RAM slots and that it can support up to 2x16GB (and probably 2x32GB.) 

I bought a kit with 
[Crucial 2x16GB 3200MHz SODIMMs](https://www.amazon.com/gp/product/B08C4X9VR5/ref=ppx_od_dt_b_asin_title_s01)
from Amazon. As I write this, the price is $44.


# Opening up

**Removing the screws**

This is the easy part.

There are 10 screws at the bottom, 6 of which are hidden underneath the 2 rubber anti-slip strips.
It's easy to peel these stips loose. It's als easy to put them back without losing the stickiness.

![Bottom screws](/assets/hp17upgrade/bottom_screws.jpg)

**Removing the bottom cover**

The bottom cover is held back by those annoying plastic tabs. If you have a plastic spudger or
prying tool, now is the time to use them. I didn't so I used a small screwdriver instead. Chances
are high that you'll leave some tiny scuffmarks on the plastic casing. 

I found it easiest to open the top lid a bit, place the laptop on its side, and start on the
left and right side of the keyboard.

![On the side with small gap](/assets/hp17upgrade/on_the_side_with_small_gap.jpg)

After that, it's a matter of working your way down the long sides at the front and back of the
laptop. There are power and USB connectors that are right against the side of the bottom panel so
be careful not to poke with the spudger or screwdriver inside the case.

![On the side with power connector exposed](/assets/hp17upgrade/on_the_side_with_power_connector_exposed.jpg)

It's a bit of a jarring process, going back and forth and making steady improvement. In addition
to all the clips around the board of the bottom panel, there are also a few in the center that latch on
to the side of the battery. But after enough wiggling and creaking sounds, the panel should come loose.

![Bottom panel completely removed](/assets/hp17upgrade/bottom_panel_completely_removed.jpg)

# Replacing the RAM

As expected, there are 2 SODIMM slots, one of which is populated with a 3200MHz 8GDB RAM stick. At the
bottom right of the image below, you can also see the SSD slot. If you don't enjoy the process of opening
up the laptop and want to upgrade to a larger drive as well, now would be the time for that.

![Motherboard with SODIMM and SSD slot](/assets/hp17upgrade/motherboard_with_sodimm_and_ssd_slot.jpg)

New RAM in place!

![Motherboard with upgraded RAM](/assets/hp17upgrade/motherboard_with_upgraded_ram.jpg)

It's always a good idea to test the surgery before reassembly:

![Laptop on the side with bootup image](/assets/hp17upgrade/on_the_side_with_bootup_image.jpg)

![Windows system screen](/assets/hp17upgrade/windows_screen.jpg)

Success!

# Reassembly

Reassembly of the laptop is much easier than taking it apart. Everything simply clicks together.

The only minor surprise was that both anti-slip strips became a little bit longer...

![Anti-slip strip a little bit longer](/assets/hp17upgrade/anti_slip_strip_longer.jpg)

# References

* [Memory Upgrade for HP 17-cp3005dx Laptop](https://www.memorystock.com/memory/HewlettPackard17cp3005dx.html#:~:text=The%20Laptop%20has%202%20Slots,per%20slot%20for%20your%20Laptop.)
* [Upgrading Newer HP 17.3" Laptop With New RAM And M.2 NVMe SSD](https://www.youtube.com/watch?v=fQRrwJ3xIR8)

    Different model with Intel CPU but the case is the same.

