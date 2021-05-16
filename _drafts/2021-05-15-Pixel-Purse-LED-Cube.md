---
layout: post
title: Pixel Purse LED Cube Controlled by Cisco 3G Modem
date:  2021-05-15 00:00:00 -1000
categories:
---

*I presented this project at BangBangCon West 2020, but never got around to writing
down the details...*

* TOC
{:toc}

# Introduction

I can't pinpoint exactly when it happened, but there was a time, between 2018
and 2020, where LED cubes were a bit of thing in the world of hobby electronics.

On Twitter, I could follow day-by-day journey of [kbob](https://twitter.com/kernlbob) (aka Bob Miller)
when trying to come up with the best possible 3D printed solution. The 
[end result](https://twitter.com/kernlbob/status/1169342374960619522) is amazing. 

![kbob's LED cube](/assets/led_cube/kbob_led_cube.jpg)

He also wrote [a blog post](https://kbob.github.io/2019/08/23/led-cubes) with 
a history of LED cubes as well as some implementation details.

At the Hackaday Superconference 2019, [Greg Davill](https://twitter.com/GregDavill) 
took things to the [next level](https://gregdavill.com/blog/2020/6/13/miniature-3456x-led-cube). 
After first building something with off-the-shelve LED matrix panels, like kbob and everybody
else, he designed one from scratch, LED PCB and aluminum frame included. 

![Greg's LED cube](/assets/led_cube/gregs_led_cube.jpg)

I always wanted to do something with LED panels myself, but there was nothing that kicked
in, until August 2019, when the [Pixel Purse](https://www.amazon.com/Project-Mc2-Toy-Light-Purse/dp/B071LQR2QG/ref=sr_1_1) 
went on sale on Amazon for $6.16. (As I write this, the price is back at $52.)

I wrote a [Pixel Purse Teardown blog post](https://tomverbeure.github.io/2019/10/03/Pixel-Purse.html),
but what I forgot to mention back then was that I bought not 1 but 12 purses, because
that's what you need to cover the 6 sides of a cube.

This was not as easy as you'd think: Amazon had a limit of only 2 purses per 
customer, but I recruited 5 victims at work and soon enough a stack of 6 boxes 
was dropped off at my work cubicle:

![Amazon boxes with 12 Pixel Purses](/assets/led_cube/12_pixel_purses.jpg)

The loot after disassembling all of them:

* 12 32x16 LED panels
* 48 AA batteries (low quality!)
* 12 4Mbit SPI flash PROMs
* a bunch of screws and voltage regulators

![12 purses disassembled](/assets/led_cube/purses_disassembled.jpg)

Even with the most important components in hand, I didn't actually started building
anything: my attention had shifted to other projects. But at the end of November, 
Josh asked me if I had anything interesting to present for the upcoming !!Con West 2020?

I did not, but I wondered if I could make an LED cube that was driven by the
Cisco HWIC-3G-CDMA modem that [I had just reverse engineered](/2019/11/11/Cisco-HWIC-3G-CDMA.html)?

![Cisco HWIC-3G-CDMA modem](/assets/cisco-hwic-3g-cdma/pcb_top_annotated.png)

On December 22nd, 2019, I received confirmation that my "Cisco Purses Cubed!" talk proposal
had been accepted, and "please, confirm your participation by December 30th." 
At that point, I had nothing but the LED panels and the Cisco modem. There was no
RTL code, no way to connect the modem to the LED HUB75 interface, and no plan for the
mechanical structure.

But at least, there was Christmas!

Over the course of a couple of days, I was able to get 2 panels to light up
in a way that wasn't totally random, which made me confident enough to
foolishly confirm on New Year's Eve that yes, I'd be able to present my cube
at the end of February. My wife had picked up some rumors about a virus on Chinese 
forums and was wondering whether she should cancel a business trip to Wuhan.

![Two panels lighted up](/assets/led_cube/two_panels_lighting_up.jpg)

The race was on!

# PCBs as Mechanical Structure

PCB are an example of high precision manufacturing at mass scale yet low cost. And we,
hobbyists, can go along for the ride for next to nothing a company like 
[JLCPCB](https://www.jlcpcb.com) will deliver 5 high quality PCBs for $2 + $5 shipping if 
you can wait 3 weeks. Add another $9, and the time from initial order to PCBs at your doorstep 
can be 6 days!

I had just received the Thanksgiving sale 3D printer, but with only 2 months to go, 
there was no time to learn 3D modelling and how to use the printer from scratch. A laser
cutter was out for the same reason, so I decided on using PCBs for the mechanical structure 
that would keep the LED panels together.

The idea was to build 8 corner pieces that each consist of 3 identical corners, and to
use 90 degree pin headers and soldering to fuse the 3 PCBs into a solid unit.

Each of the 24 pieces looks like this:

![PCB drawing](/assets/led_cube/pcb_drawing.png)

KiCAD is a great PCB design tool, but terrible for mechanical drawings. There was
no time, however, to learn something else. The 5 circles match exactly the location
of the screw holes in the LED matrix panel, and the different width indents are necessary
to avoid various components on the panel.

I used [kicad-util](https://gitlab.com/dren.dk/kicad-util) to add mouse bites and
bridges between multiple instances of the same corner. It takes a bit to learn
how it works, and the error messages aren't always helpful, but it was very useful
once I got the hang of it.

![PCB drawing panelized](/assets/led_cube/pcb_drawing_panelized.png)

With 5 corners per PCB and 10 PCBs ordered, I had 50 corners, double the 24 that I 
thought were needed:

![PCB corners produced](/assets/led_cube/pcb_corners_produced.jpg)

# Cube Assembly - First Try

When the corner piece PCBs arrived, I could try the first assembly.

There were good points:

* the location of the screw holes were spot on. My calipers had done a great job!
* the general concept of making corner pieces worked, in general. It was possible to
  assemble all 12 LED panels and create a set-sustaining structure, as long as you'd
  orient the panels the right way.

But also some bad ones:

* the location of the pin header holes in combination with the 90 degree pin headers
  themselves resulted in huge unsightly seams between the panels.
* the 2 panels on the same surface weren't linked together. They were very easy to shift,
  which made things even uglier (see red rectangle below.)

![First assembly](/assets/led_cube/first_assembly_more.jpg)


![First assembly closeup](/assets/led_cube/first_assembly.jpg)

# Cube Assembly - Second Try

For the first assembly, I was using double-row 90 degree headers. I figured that
switching to a single row would go a long way in reducing the gap.

![Inside view of corner piece](/assets/led_cube/corner_piece_inside.jpg)

![Outside view of corner piece](/assets/led_cube/corner_piece_outside.jpg)

Much better! At least the gap between the PCBs of the corner pieces are gone. It's
still not perfect: even if the corner piece PCBs touch each other on the inside,
the thickness of the PCB itself means that there's a gap on the outside.

![Second assembly closeup](/assets/led_cube/second_assembly_closeup.jpg)

To make that go away, I'd have to move the screw holes on the corner piece
more towards the corner. But there was no time for a redesign, so I just
went with what I had. I had to scrap the 8 corner pieces that I had already
made, but I had ordered enough PCBs for a second set. Phew!

The problem of linking the 2 panels on the same surface was unexpectedly
solved by observing the screw holes on one leg of the corner piece were
spaced exactly right. I could reuse the scrapped pieces for that.

![Panel connection piece](/assets/led_cube/connection_piece.jpg)

Tying the 2 panels together worked wonders. The cube wasn't perfect, but
it was definitely good enough.

During the project, I had to rebuild the cube multiple times. It was tedious
but also satisfying to see it come together. I particularly liked the
Star Wars Death Star Tunnel vibe of this view:

![Death Star Tunnel View](/assets/led_cube/starwars_death_star_tunnel.jpg)

Fully assembled:

![Cube fully assembled](/assets/led_cube/fully_assembled.jpg)

The seams are there, but once lighted up, the animation on the LED panels
distracts from the imperfections.

# HWIC Interface & HUB75 Adapter Boards

Cisco routers have extension slots for options like WAN ports, modems etc. They use
a proprietary HWIC connector that isn't available on Digikey or Mouser. On the
HWIC-3G-CDMA modem, the HWIC connector has a bunch of GPIOs that route straigth
to the Cyclone II FPGA as well as configurations that are used to download
the FPGA bitstream into the FPGA at bootup by means of the passive serial method.

I needed an interface board that plugged into the HWIC connectors and some
logic to download the bitstream into the FPGA at power up.

The HWIC connector has 1 row with pins that are compatible with standard
2.54mm pin headers. This row is used to supply power to the board. It also
has 2 rows with holes that are spaced 1.27mm as part. These contain the 
IOs.

![HWIC Connector](/assets/led_cube/hwic_connector.jpg)

My earlier prototype used a soldered board with only one row of 1.27mm pins
and with 50% of the pins in that row removed. That wasn't enough to drive
a full HUB75 interface, which is why my earlier picture only had red LEDs
lighting up!

With a PCB, I'd be able to connect all the pins that I needed:

![HWIC Interface Board](/assets/led_cube/hwic_interface_board.jpg)

In addition to the 3 rows with pins, there's a room to connect an SDcard
and an ATtiny to manage downloading a bitstream from the SDcard into the FPGA.

Unfortunately, minutes after receiving the boards on New Year's Eve, I found out
that I had swapped around the 2.54mm row and the 1.27mm rows!

I was able salvage the board by soldering the pins on the other side. I had enough
GPIO pins now to drive a full HUB75 interface.

![HWIC Interface Board Soldered](/assets/led_cube/hwic_interface_board_soldered.jpg)

The interface board routes the 1.27mm GPIO pins to a regular 2.54mm pin header. I wanted
the board to be general purpose, so the pin header does not use a HUB75 configuration.
I designed an additional PCB for that:

![GPIO to HUB75 board](/assets/led_cube/GPIO_to_HUB75_board.jpg)

It arrived on January 16th, together with the fixed HWIC interface board.

*Hot Tip: when you spin different revisions of a board, uses different PCB colors
for each revision to avoid using the wrong version!*

# Overall FPGA Digital Design

All the hardware needs smarts to drive the right timing to the LED panels.

By now, you should know that these panels use a relatively standard HUB75 
protocol. I could spend a lot of words describing the details of this protocol,
but [Glen Akin's tutorial](https://bikerglen.com/projects/lighting/led-panel-1up/)
already does that very well.

The most important part to remember is that it uses 1-bit per color component
(3 bits per pixel) and that is shifts the values of 1 or 2 rows (depending
on the panel type) of the matrix into a shift register which then gets
displayed.

It's your job to continuously refresh the LED rows to give the impression that
all LEDs are lighted up at the same time. And if you want more than just
1 color per component, you need to do it even faster and create the right
intensity with pulse-length modulation.

I *love* writing RTL, so there was no way I'd reuse somebody else's code for that!

Here's the architecture that I came up with:

![Digital Design Block Diagram](/assets/led_cube/led_cube-block_diagram.svg)

The CPU will be responsible to create interesting images that get written in the
LED frame buffer RAM.

The HUB75 Streamer fetches the pixels in the correct sequence, sends them through
a gamma correction lookup table, and dims them as needed.

The HUB75 Phy implements the low level HUB75 protocol, creates the desired output
pins timings etc.

The gamma correction is very important: not only does it make sure that color
gradients look right to our eye, it also pushes more LED values to a lower 
intensity. LEDs consume a ton of power, so this is an important battery saving
step.

The same is true for the dimming function: it simply multiplies all pixel values
to a smaller value.

The CPU could do this in software, but both functions are trivial to implement in 
hardware, and doing frees up a lot of cycles in the 50MHz CPU.

# Correction for Panel Orientation in the HUB75 Streamer

The LED panels were assembled in such a way that the internal cabling was as 
straightforward as possible. You can see a bit of that in the Death Start
picture earlier, but that doesn't show interconnecting different sides
of the cube. There's a rats nest of cables in the end!

An optimal cabling doesn't mean that LEDs are located in the most logical
location from a software point of view: there are different orientations
and rotations for each of the 16 LED panels.

I wanted software to be as easy as possible. That's why the LED RAM has the
LED locations in a logical order that easy to use for the software. The
stream is responsible to fetch the LED values in a order that matches
the physical cabling.

This is one of those things where SpinalHdl shines. Here is the 
[hardware structure](https://github.com/tomverbeure/cube/blob/70fef2f4ca1a75b4572f08cdb1270337a5284cef/spinal/src/main/scala/cube/Hub75Intfc.scala#L12-L25) 
that configures the scan order of LEDs:

```scala
case class PanelInfoHW(conf: Hub75Config) extends Bundle {
    val topLeftXCoord           = SInt(2 bits)
    val topLeftYCoord           = SInt(2 bits)
    val topLeftZCoord           = SInt(2 bits)

    val memAddrStartPh0         = UInt(log2Up(conf.total_nr_pixels+1) bits)
    val memAddrStartPh1         = UInt(log2Up(conf.total_nr_pixels+1) bits)
    val memAddrColMul           = SInt(log2Up(conf.panel_cols)+2 bits)
    val memAddrRowMul           = SInt(log2Up(conf.panel_cols)+2 bits)

    val xIncr                   = SInt(2 bits)
    val yIncr                   = SInt(2 bits)
    val zIncr                   = SInt(2 bits)
}
```

And here are the 
[actual values for the 12 panels](https://github.com/tomverbeure/cube/blob/70fef2f4ca1a75b4572f08cdb1270337a5284cef/spinal/src/main/scala/cube/CubeTop.scala#L17-L39):

```scala
    val panels = ArrayBuffer[PanelInfo]()

    //                topLeftCoord   Side  Top      Rot    xyzIncr
    panels += PanelInfo(-1, 1,-1,       5, true,    0,     0,-1, 1)
    panels += PanelInfo(-1, 0,-1,       5, false,   0,     0,-1, 1)

    panels += PanelInfo(-1, 1,-1,       4, true,    0,     1, 0, 1)
    panels += PanelInfo(-1, 1, 0,       4, false,   0,     1, 0, 1)

    panels += PanelInfo(-1,-1, 1,       3, true,    0,     1, 0,-1)
    panels += PanelInfo(-1,-1, 0,       3, false,   0,     1, 0,-1)

    panels += PanelInfo( 1, 1,-1,       2, true,    0,    -1,-1, 0)
    panels += PanelInfo( 1, 0,-1,       2, false,   0,    -1,-1, 0)

    panels += PanelInfo( 1, 1, 1,       1, true,    90,    0,-1,-1)
    panels += PanelInfo( 1, 0, 1,       1, false,   90,    0,-1,-1)

    panels += PanelInfo(-1, 1, 1,       0, true,    180,   1,-1, 0)
    panels += PanelInfo(-1, 0, 1,       0, true,    0,     1,-1, 0)
```

After changing these configuration parameters too many times, and getting tired of
waiting for synthesis results, 
[I made these configuration parameter programmable by the CPU](https://github.com/tomverbeure/cube/blob/70fef2f4ca1a75b4572f08cdb1270337a5284cef/spinal/src/main/scala/cube/Hub75Streamer.scala#L225-L244).
That way, I could use [the fast update memory update hack](/2021/04/25/Intel-FPGA-RAM-Bitstream-Patching.html) that I 
described in a recent blog post.

# From One to Two HUB75 Ports

For simplicity, my initial plan was to use 1 HUB75 port.

That worked great for 8 panels, but I started seeing corruption on the 9th LED panel.

I didn't put the signal on an oscilloscope to confirm, but I'm pretty certain
that there were timing issues after going through too many ribbon cables. (I don't
remember if slowing the clock made things work better.)

In any case, it shows that committing to a talk without working out all the
details first carries significant risk: adding a second HUB75 interface exhausted
all the available GPIOs on the HWIC interface!

# Rick, Pac-man, Mario

"Never Gonna Give You Up" may not be the Hello World of moving images ("Bad Apple"
is probaby the one to hold that title), but it's close.

![Rick](/assets/led_cube/rick_orig.gif)

I found a GIF with his smooth moves, and created a little pipeline that does the following:

* Extract all individual images
* Resize to 32x23 pixels, so that everything fits in a 32x32 LED matrix
* Join all images into 1 image
* Create a palette only 16 colors
* Reduce all individual images to 4 bits per pixel to save memory
* Save images as pure binary

This is all done in a Makefile that you can find [here](https://github.com/tomverbeure/cube/blob/master/movie/Makefile).

Here's Rick in all his resolution reduced glory:

![Rick](/assets/led_cube/rick.jpg)

Notice how all the bright LEDs pull a 1A at 3.3V, good for 3.3W. Dialing down brightness
is essential to make everything work on a triplet of AA batteries!

You can also see the tags "4" and "5" taped on the panel. They are taped
with the right orientation and location to make it easy to remember the panel
configuration parameters.

The resolution is obviously very low, when looking at it from a few meters, and with
animation enabled, it's undeniably Rick.

A single animation would be a bit poor, so I added Pac-man chasing and
being chased by ghosts:

![Pac-man](/assets/led_cube/pacman.jpg)

And Mario running around with nothing to do:

![Mario](/assets/led_cube/mario.jpg)

The bitmaps use either 2 or 4 colors and defined as 
[binary structs](https://github.com/tomverbeure/cube/blob/70fef2f4ca1a75b4572f08cdb1270337a5284cef/sw/main.c#L39-L301) 
in the main C code:

```c
uint32_t ghost_left_0[14] = {
    0b0000000000010101010000000000,
    0b0000000101010101010101000000,
    0b0000010101010101010101010000,
    0b0001010101010101010101010100,
    0b0001010111110101010111110100,
    0b0001011111111101011111111100,
    0b0101011111101001011111101001,
    0b0101011111101001011111101001,
    0b0101010111110101010111110101,
    0b0101010101010101010101010101,
    0b0101010101010101010101010101,
    0b0101010101010101010101010101,
    0b0101010100010101010001010101,
    0b0001010000000101000000010100,
};
```

If you didn't know that [GCC supports binary constants](https://gcc.gnu.org/onlinedocs/gcc/Binary-constants.html), 
now you do!

# Unexpected Short Circuits Solved with UV Hardened Glue

After yet another assembly, I noticed that some LED panels would stop functioning
correctly by holding it the wrong way.

This was quickly root caused as a short circuit. The head of the screws that 
tie the corner pieces to the LED panel would sometimes touch multiple LED
pins at the same time. 

![screw surrounded by LEDs](/assets/led_cube/screws_short_circuits.jpg)

I should have used plastic screws instead, but lacking those, I used UV hardening
glue on each screw to create an insulation layer.

![Screw with layer of UV hardening glue](/assets/led_cube/uv_hardening_glue.jpg)

These glues sell for just a couple of dollars on AliExpress or 
[Amazon](https://www.amazon.com/Paddsun-Second-Plastic-Welding-Compound/dp/B078V45GYY) and
despite the terrible chemical smell, they're awesome. I use them all the time to hold delicately 
soldered wires in place on a PCB.

The only issue was the tedium of adding this insulating later on all the screws: 
there are 72 of them!

# Integrating It All and Shortcuts

There are a few practical questions that still need to be answered:

* How to fix the electronics 

    The answer to that is simple: I took a shortcut. There are so many
    cables inside that you can just stuff the Cisco modem in there and it
    will still suspended amount all the mess.

    It would be a terrible idea if you were planning to travel with it,
    but it was good enough for a one-time demonstration.

* What about batteries and how do you switch it on and off?

    Switching the thing on and off was linked to 'solving' the battery
    issue: I just had 2 wires going out of the cube and connected them to
    the batteries when I needed to work.

    Not elegant at all, but I ran out of time.

* How do you open the cube?

    By having the bolts inside-out for the top panel. Opening the cube is a matter of
    removing 8 tiny bolts.

I also took a shortcut to configure the FPGA: I didn't finish the subproject of loading
the bitstream from an SDcard and loading it into the FPGA with the ATtiny of the 
HWIC interface board.

Instead, I had a USB-Blaster ribbon cable handing out off the bottom of the cube.
After powering up the cube, I'd quickly use a laptop and Quartus to download the 
bitstream into the FPGA. I practiced this manouver a couple of times, and it 
went without a hitch during the presentation.

# The End Result

The presentation went very well!

I spent quite some time on the low cost of PCBs, and how to use that to your
advantage when making mechanical designs, since that's probably not well known
with a computer science oriented audience.

<iframe width="560" height="315" src="https://www.youtube.com/embed/0tBU5-lJYmU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

There's some desire to clean up the loose ends at some point: the HWIC interface
board would be better with a PMOD interface, I want the bitstream loader to work,
and a particle simlation guided by an accelerometer isn't very original, but it looks
so incredibly cool.

But I doubt that these will ever happen. There are so many interesting project to be
done, and this one has largely run its course.


# References

* [kicad-util](https://gitlab.com/dren.dk/kicad-util)

    Panelization, mouse bites etc.

 * [Glen Akins' RGB LED Panel Driver Tutorial](https://bikerglen.com/projects/lighting/led-panel-1up/)

