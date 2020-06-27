---
layout: post
title:  Debugging My First STM32 Program on the BlackIce-II Board
date:   2018-03-24 00:00:00 -1000
categories: 
---

* TOC
{:toc}

My larger goal is to create a new firmware called "icehub", which will enable a bunch of new 
development features. Instead of using the standard ST libraries, I want to use 
i[`libopencm3`](https://github.com/libopencm3/libopencm3) instead: 
it's an open source library that works with most Cortex based SOCs and microcontrollers. 

Today, I wanted to create my first `libopencm3` program, a blinking LED obviously, run it 
on the STM32 of the BlackIce-II board, and step through it with the debugger.

After [yesterday's success](/2018/03/23/Connecting-GDB-to-the-BlackIce-II-STM32L433.html) 
of getting the Blue Pill to connect to the Blackice, this certainly wasn't going to be overly 
complicated! Right?!

# Step 1: Adding Support for the STM32L433RCT

`libopencm3` has support for 1stm32l41, but only a few specific types. My L433 was of course not part of the list.

Adding support turned out to be pretty easy: I just needed to tell how much ROM and RAM it has and 
add that information to `./ld/devices.data`. (You don't need to do that anymore: I submitted a
[pull request](https://github.com/libopencm3/libopencm3/pull/899), and it's now part of the official repo.)

There are a lot of examples as part of the library, and there's even 
an [`l4`](https://github.com/libopencm3/libopencm3-examples/tree/master/examples/stm32/l4) 
directory for that, but a shared Makefile is missing. So that had to be fixed as well. 
(This has since been fixed in the official repo too.)

After this, I could compile the `libopencm3-examples/examples/stm32/l4/stm32l476g-disco/basics` example.

# Step 2: Creating a blinking LED Program

Since I ultimately want to do a lot of USB-related stuff, I started with a `usb_cdcacm` example from 
the F1 examples directory. This forced me to start digging into the whole clock architecture of the STM32, 
because the F1 is really different there. Not the most efficient way to get to blinking LED.

Anyway, eventually I ended up with something that compiles.

On the BlackIce-II board, the DBG1 LED is the only one that can be controlled directly by the STM32, 
so that's the one!

# Step 3: Running it with the Blue Pill - Black Magic Probe. And failing.

* After power, the STM32 starts to execute code from flash address 0x0800_0000. 
* My blinking LED binary is also targeted for that address. 
* So you need to flash that.

**This is where I ran into a crucial limitation of the Black Magic Probe: it doesn't support flash operations!**

I changed the address map to create a binary that is mapped to address 0x2000_0000, the RAM of the STM32. 
And it gets loaded fine there. However I could not figure out to get GDB to execute from an address in that range.

I needed a different solution: my original STLink v2 dongle!

# Step 4: The STLink v2  the BlackIce-II

After yesterday, I'm a wiser man now, so I added an extra GND wire between the STLink and the BlackIce board, I 
fired up openocd, and *HURRAY!* it connected just fine!

What's more: when you telnet into openocd, you can issue flash read and write operations!

And that's what I did: 

* I reverted my linker 0x2000_0000 changes
* Built a binary for flash address 0x0800_0000.
* Flashed it with openocd
* Linked GDB to openocd
* Within GDB:
    ```
load cdcacm.elf
br main
continue        <<<< un somehow doesn't work
    ```
* BOOM! It just worked!

What's more: the LED was blinking correctly right away!

# Conclusion

Ultimately, I would love to debug my programs from RAM instead of flash, but for now, I'm moving 
back to using the STLink instead of the Black Magic Probe.

