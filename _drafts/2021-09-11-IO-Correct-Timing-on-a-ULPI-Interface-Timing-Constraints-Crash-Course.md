---
layout: post
title: Correct Timing on a ULPI Interface - Timing Constraints Crash Course
date:  2021-09-11 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction



# A Crash Course in Timing Constraints

Timing constrains are used to specify timing relationships between different elements of a design,
which are then used during synthesis, placement, static timing analysis.

They are used to check the following aspects of a design:

* setup time

    The setup time is the minimum time during which a signal must be stable **before**
    it can reliably be captured by flip-flop the active edge of a clock (the 'latching edge').

* hold time

    The hold time is the minium time during which a signal must be stable
    **after** the active edge of a clock to reliably capture a signal.

* a delay specification

    In some cases, a minimum or maximal delay is required that's unrelated to a setup or
    hold requirement.


![setup and hold time diagram](/assets/io_timings/io_timings-setup_hold.svg)

For all timing checks, there'll be a launching edge and a latching edge, there'll be
a timing requirement between those 2 that must be met, and there'll be one or more
path of design elements from a start point to an end point through which this 
timing requirement is calculated.

*Note: while there's always a launching and a latching edge, that doesn't necessarily
mean that there are clocks involved! Usually there are, but there are cases where
these edges are defined without the presence of clocks.*

When checking setup times, a static timing analysis tool will look for the longest path between a
given start and an end point. But when testing hold times, it will look for the shortest path for the
same 2 points.

![different longest vs shortest path between the same 2 launch and latch FFs](/assets/io_timings/io_timings-longest_vs_shortest_path.svg)

![setup timing waveform diagram](/assets/io_timings/io_timings-setup_launch_to_latch.svg)

![hold timing waveform diagram](/assets/io_timings/io_timings-hold_launch_to_latch.svg)



In the diagram above, the rising edge of the clock is the active edge, but a falling
edge is possible too.

The sum of the setup and hold time is the window during which a signal must remain constant
to reliably capture and store data into a flip-flop.

Whole books are written about timing specifications. It's not possible to summarize all of that in a
single section of a blog post. What follows is a short summary that shows how static timing analyzis 
engines deal with setup and hold timing when dealing with different clocks. It's primarily
written for my own benefit, when I need a quick refresher on the topic. If you want to a more
elaborate explanation that's still very practical, I highly recommend Ryan Scoville's 
[TimeQuest User Guide](https://www.intel.com/content/dam/altera-www/global/en_US/uploads/3/3f/TimeQuest_User_Guide.pdf).
It targets the Intel FPGA tools, but almost everything he discusses is also applicable for Xilinx and
even ASIC tools from Synopsys and Cadence.

**Setup Time**

When a timing analysis tool checks the setup time, it does the following for each path 
between 2 flip-flops:

1. Check if the path between 2 flip-flops can be ignored.

    The timing constraints will often mark paths as false paths. 
    
    A good example of this are paths between flip-flops that belong to asynchronous
    clock domains.

1. Find the launch clocks: the clocks that are connected to the launching flip-flop.
1. Find the latching clocks: the clocks that are connected to the latching flip-flop.

    It's possible for both the launching and latching flip-flop to have multiple clocks. 
    This can happen when there is a multiplexer in the clock path.

1. Find the shortest possible positive delay between any possible launch edge and any possible
   latching edge. This will be the default setup relationship.

    For the majority for cases, the latch and launch edges will be on the same clock,
    and the shortest possible positive delay will be the same as the clock period:

    ![setup edges trivial](/assets/io_timings/io_timings-setup_edges_trivial.svg)

    But in the example below, the launch clock and latch clock have a different frequency. The
    timing analyzer will go through all launch and latch edge combinations and find the smallest
    value. In this case, that smallest value is 1ns:

    ![setup edges](/assets/io_timings/io_timings-setup_edges.svg)

    When looking for this default setup time, the timing analyzer will looks at clock edges
    at their source, **without taking into account the delay from the source of the
    clock to the clock input of the flip-flop.**

1. Apply an optional multi-cycle adjustment to the setup time to obtain the final setup
   relationship.

    A common case for applying a multi-cycle adjustment is when the launch and latch clock
    have the same frequency, but there is a phase shift between them. 

    In the diagram below, a latch clock was created that is shifted 60[^3] degrees ahead 
    of the launch clock. If the intent of logic is that the data is latched 7ns 
    instead of 1ns after being generated on the launch clock, a 1-cycle multi-cycle adjustment 
    must be applied:

    [^3]: 1ns / 6ns * 360 = 60

    ![setup multi-cycle path](/assets/io_timings/io_timings-setup_multi_cycle_path.svg)

    One reason to have such a phase shifted clock is to make meeting setup timing easier
    In the example above, the delay from the launching to the latching FF can be 1ns higher before
    violating the setup time. This technique is commonly used when dealing with 
    external IO interfaces. (Doing this is not free: shifted a latch clock forward increases 
    the hold time by the same amount!)

1. Calculate the longest launch clock to latch delay: the total delay from the starting point of the launch clock,
   through the launch FFs, to the data input of the latching flip-flop

    ![setup launch to latch delay](/assets/io_timings/io_timings-setup_launch_to_latch_delay.svg)

    If there are multiple combinatorial paths from the launch to latch point, the path with
    the highest delay should be taken.

    In the real world, flip-flops have internal setup time requirements. This setup time
    should be added to the launch clock to latch delay.

1. Calculate the latch delay: delay from the starting point of the latch clock to the latching
   flip-flop

    ![setup latch delay](/assets/io_timings/io_timings-setup_latch_delay.svg)

1. Setup time requirements are met if the time from the launch edge plus the launch to latch delay is smaller 
   than the time of the latch edge plus the latch clock delay.

    ![check setup time](/assets/io_timings/io_timings-check_setup_time.svg)

    In the diagram above, with the launch clock shifted by 60 degress, you can see how setup timing is met.

    Mathematically, this equation must be met:

    *launch clock to latch delay <= setup relationship + latch delay*

    Or for the diagram above: (4ns + 6ns) < 7ns + 5ns -->  10ns <= 12ns --> OK!

**Hold Time**

When a timing analysis tool checks the setup time, it does the following for each path 
between 2 flip-flops:

1. Check if the path between 2 flip-flops can be ignored.
1. Find the launch clocks: the clocks that are connected to the launching flip-flop.
1. Find the latching clocks: the clocks that are connected to the latching flip-flop.

    These steps are the same as for setup time.

1. Find the tighest default hold relationship. This is a bit more difficult than it is for setup time.
   It goes as follows:

    For each launch edge: 

    1. Add the setup relationship.

        Note that this is not the default setup relationship, but the one after
        applying optional multi-cycle adjustments.

    1. Look back and find the first latch edge.
    1. The difference between the launch edge and the latch edge is a default hold relationship. 
    1. Apply multi-cycle adjustment to this default hold relationship to come up with the final
       hold relationship.
    1. The final hold relationship is the largest hold relationship of all the
       numbers found in step 4. 

    For the trival case with identical launch and latch clock, this results in a hold
    relationship of 0ns:

    ![hold edges trivial](/assets/io_timings/io_timings-hold_edges_trivial.svg)

    Here is the earlier case where the latching clock has been shifted forward by 60 degrees.
    Notice how we're using the final setup relationship, after applying the multi-cycle
    adjustment, to determin the latching edge for the hold relationship:

    ![hold edges shifted](/assets/io_timings/io_timings-hold_edges_shifted.svg)

    For completeness, here's also the case with the asynchornous clocks. For each launch clock edge,
    we first add the setup relationship of 1ns, then look back to find the closest latching edge,
    and of all those, we choose the largest value. In this case, that largest value is 0ns:

    ![hold edges async clocks](/assets/io_timings/io_timings-hold_edges_async_clocks.svg)

1. Calculate the shortest launch clock to latch delay: the delay from the starting point of the 
   launch clock, through the launch FFs, to the data input of the latching flip-flop.

    If there are multiple combinatorial paths from the launch to latch point, the path with
    the lowest delay should be taken.

1. Calculate the latch delay: delay from the starting point of the latch clock to the latching
   flip-flop

    These calculations is the same as for setup timing checking. 

1. Hold time constaints are met if the time from the launch edge plus the launch to latch delay
   is larger than the time of the latch edge plus the latch clock delay.

    ![check hold time](/assets/io_timings/io_timings-check_hold_time.svg)

    Mathematically, this equation must be met:

    *launch clock to latch delay >= hold relationship + latch delay*

    Or for the diagram above: (2ns + 2ns) >= 3ns + 2ns -->  4ns <= 5ns --> NOT OK!

# Timing Constraint Commands

In Quartus, Vivado, and most other modern FPGA or ASIC synthesis and timing analysis tools
(not Xilinx ISE!), timing constraints are specified with an `.sdc` file, short for
Synospys Design Constraint file. An SDC file is really just TCL file (the world's most
wretched programming language) with custom timing specification commands. You can
use `if`, `eval` and other standard TCL constructs, which is useful if you have different
configurations, such as slightly different constraints for different FPGA chips or
boards.

Here is a very quick view at the most important timing constraint commands.

* `create_clock -name <clock name> -period <clock period> [clock design element]`

    This defines a clock and specifies where on a timeline there will be endlessly repeating
    rising and falling edges. 

    You can optionally specify a clock design element (such as a FPGA IO port or the pin 
    of a PLL), in which case clock calculation will ripple through all the connected elements of 
    said clock (e.g. the delay through a clock buffer will be taking into account). 

    Or you don't specify such an design element in which case you create a so-called virtual 
    clock.

    In general, virtual clocks are used to create timing constraints that are related to
    external interfaces. For example, to define a clock of an external chip that has signals
    that interface with our FPGA logic.

    Regular, non-virtual, clocks are used to specify timing inside your FPGA.

    We'll see both of them later in this blog post.

* `create_generated_clock ...`

    A generated clock is a clock that is created internally in the design as a derivative from 
    another so-called master clock. A good example is a clock that is created by a PLL, where the input 
    of the PLL is the master clock.

    There are [a lot of options](https://www.intel.com/content/www/us/en/programmable/quartushelp/13.0/mergedProjects/tafs/tafs/tcl_pkg_sdc_ver_1.5_cmd_create_generated_clock.htm) 
    that allow you to set ratios, phase shifts, duty cycle, etc.

* `set_input_delay -clock <clock name> <delay> <design elements> [-max|-min]`

    This command create an imaginary, ideal flip-flop with zero clock-to-output delay, 
    connected to a given clock, and a delay element, the output of which is connected to the design elements.

    ![set_input_delay conceptual diagram](/assets/io_timings/io_timings-set_input_delay.svg)

    By using the `-min` and the `-max` options, you can specify the delay as a
    range instead of a single fixed value.

* `set_output_delay -clock <clock name> <delay> <design elements> [-max|-min]`

    The opposite of `set_input_delay`, this command connects the given design elements to an
    imaginary delay element which feeds into the data input of an ideal flip-flip that
    is again connected to the given clock.

    ![set_output_delay conceptual diagram](/assets/io_timings/io_timings-set_output_delay.svg)

    Just like `set_input_delay`, the delay can also be a range instead of a single value.

* `set_max_delay [-from <design elements>] [-to <design elemenets>] <value>`

    The earlier `set_input_delay` and `set_output_delay` command are used to specify 
    higher level timing constraints, in that they add 'fake' delay and FFs elements to the overall 
    design and treat them like other FFs, gates and delays. When you change the clock speed, the 
    timing calculations to these fake FFs will change accordingly.

    `set_max_delay` is different: it sets a setup constraints at a specific point in time.
    When you change the clock for a register that drives a design element to which a max delay
    is assigned, this max delay will not change, and thus the setup time won't change either.

    It's best to not use `set_max_delay` if you can avoid it, but it's good to have it for

* `set_clock_latency -source <delay> <clock name>`

    This command is not very common, but it can be used to add a delay to a clock, e.g. to
    model the signal travel time across a PCB before it hits the clock pin of an FPGA.

# ULPI IO Timing

It's now time to revert our attention back to the failing ULPI hardware.

Since the simulation is working fine but the hardware does not, timing related issues should be
an immediate concern. So let's have a look at the the IO timing requirements in the ULPI specification and
translate them into timing constraints.

At first sight, they are relatively straightforward:

![ULPI Specification Timing Diagram](/assets/io_timings/ulpi_io_timing_specification.png)

*(I edited the diagram to remove 4-bit DDR mode, because most ULPI PHYs don't support this mode.)*

The PHY is in "Output clock" mode. All the timings above are using the clock IO pad of the PHY
as reference point.

**ULPI Clock Definition**

It's always good practise to define a virtual clock for the logic that lives outside of the chip/FPGA. 
It's not shown in the diagram and table, but the ULPI clock has a frequency of 60MHz.  Let's define 
the clock as follows:

```tcl
create_clock -name ulpi_clk_phy -period 16.6
```

*Note how the clock that I defined above isn't linked to any FPGA pin. That's what
makes it a virtual clock.*

The clock pin of the PHY is connected to `ulpi_clk` pin of the Link, our
FPGA. According to Google, the speed of light in a PCB is around 16.3cm/ns. 
The distance from the ULPI PHY to the FPGA on the DECA board is around 2cm, which gives 
a delay of around 0.12ns. That's too low to worry about, but let's just roll with it, and
define the FPGA ULPI clock like this:

```tcl
create_clock -name ulpi_clk -period 16.6 [get_ports ulpi_clk]
set_clock_latency -source 0.12 [get_clocks {ulpi_clk}]
```

**Link to PHY Setup time: 6.0ns**

A setup time specifies how long a signal must be stable at a capture point
(e.g. the input of a flip-flop) before it can reliably be captured/latched. 

The weird thing about the ULPI specification is that it shows a maximum value. That 
doesn't make a lot of sense: setup times are supposed to be a minimum value. This 
turns out to be a bug in the specification.[^2] 

[^2]: So much for always assuming that the chip, compiler, or specification is correct!

The TUSB1210 datasheet has the same timing numbers as the ULPI specification, but correctly 
lists the setup time as a minimum value:

![TUSB1210 Timing Specification](/assets/io_timings/tusb1210_timing_specification.png)

Note that the setup time is listed for "control in, 8-bit data in", from the point of
view of the PHY, with signals going into the chip. We need to construct timing constraints 
for the other side, the link, which is driving the signals.  

Also remember that specifying a minimum setup time at a latching point is that same
as adding an extra delay right for this latching point. And, finally, that we can
model the latching point at the PHY as a flip-flop.

All this taken together means that we can convert the setup time for the PHY into a 
maximum output delay for the link:

```tcl
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 6 [get_ports {ulpi_data[*]}] -max
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 6 [get_ports {ulpi_stp}] -max
```

That statement above attaches fake flip-flops to the ULPI output pins of the FPGA. The
`-max` specification is important: the specification says that the setup time for that
PHY must be a minimum of 6ns. However, a longer setup time is fine too. From the point
of the link, this means that the additional delay of 6ns is a maximum value.

**Link to PHY Hold time: 0ns**

Similarly, the 0ns hold time for ULPI PHY input pins becomes a 0ns minimum output delay for the link:

```tcl
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 0 [get_ports {ulpi_data[*]}] -min
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 0 [get_ports {ulpi_stp}] -min
```

**PHY to Link Maximum Output delay: 9ns**

Just the way setup and hold time for the PHY convert to output delay parameters for the link,
the output delay of the PHY converts to an input delay.

```tcl
set_input_delay -max -clock [get_clocks {ulpi_clk}] 9 [get_ports {ulpi_data[*]}]
set_input_delay -max -clock [get_clocks {ulpi_clk}] 9 [get_ports {ulpi_direction}]
set_input_delay -max -clock [get_clocks {ulpi_clk}] 9 [get_ports {ulpi_nxt}]
```

The 9ns is the maximum delay from clock to output inside the PHY. It is important to
specify it as such with the `-max` option, because chances are that, in practice, that
number will be much lower.

**PHY to Link Minimum Output delay: ???**

Neither the specification nor the TUSB1210 datasheet list a minimum value for the output delay. 
But this is an important value on the receiving end, the link, because the minimum output delay 
determines the settings that check for hold violations. Lacking a concrete number, I assume a value 
of 0 ns, because that's almost always a good conservative value.

```tcl
set_input_delay -min -clock [get_clocks {ulpi_clk}] 0 [get_ports {ulpi_data[*]}]
set_input_delay -min -clock [get_clocks {ulpi_clk}] 0 [get_ports {ulpi_direction}]
set_input_delay -min -clock [get_clocks {ulpi_clk}] 0 [get_ports {ulpi_nxt}]
```

*Another popular ULPI PHY chip, the [USB3300][USB3300-product-page], is more helpful in specifying 
a minimum output delay:* 

![USB3300 Interface Timing](/assets/io_timings/usb3300_interface_timing.png)

*For this PHY, I would specify a 2ns hold time as input delay, instead of 0 ns.
Also notice how the maximum output delay is 5ns instead of 9ns, which makes
it much easier for the link to meet input timings.*

**Full Timing Constraints**

Everything combined, the SDC timing constraints look like
this:

```tcl
# ULPI PHY Timing Constraints
create_clock -name ulpi_clk_phy -period 16.6

# Link -> PHY signals
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 6 [get_ports {ulpi_data[*]}] -max
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 6 [get_ports {ulpi_stp}] -max

set_output_delay -clock [get_clocks {ulpi_clk_phy}] 0 [get_ports {ulpi_data[*]}] -min
set_output_delay -clock [get_clocks {ulpi_clk_phy}] 0 [get_ports {ulpi_stp}] -min

# PHY -> Link signals
set_input_delay -max -clock [get_clocks {ulpi_clk}] 9 [get_ports {ulpi_data[*]}]
set_input_delay -max -clock [get_clocks {ulpi_clk}] 9 [get_ports {ulpi_direction}]
set_input_delay -max -clock [get_clocks {ulpi_clk}] 9 [get_ports {ulpi_nxt}]

set_input_delay -min -clock [get_clocks {ulpi_clk}] 0 [get_ports {ulpi_data[*]}]
set_input_delay -min -clock [get_clocks {ulpi_clk}] 0 [get_ports {ulpi_direction}]
set_input_delay -min -clock [get_clocks {ulpi_clk}] 0 [get_ports {ulpi_nxt}]

# ULPI Clock for core logic
create_clock -name ulpi_clk -period 16.6 [get_ports ulpi_clk]
set_clock_latency -source 0.12 [get_clocks {ulpi_clk}]
```

# An Unexpected Timing Violation

With the timing constraints above, we immediately run into issues: the static timing analyzer
detects a huge timing violation of more than 4ns.

The 8 violating paths are from the `ulpi_direction` pin to the 8 `ulpi_data` pins:

![ulpi direction violation - summary of paths](/assets/io_timings/naive_timing_ulpi_dir-summary_of_paths.png)

The Data Path tab shows that this is a pure combinatorial path from outside the FPGA, through the
FPGA core logic, and back to the outside the FPGA. There are no flip-flop elements involved at all.

![ulpi direction violation - data path](/assets/io_timings/naive_timing_ulpi_dir-data_path.png)

The Waveform tab visualizes the problem:

![ulpi direction violation - waveform](/assets/io_timings/naive_timing_ulpi_dir-waveform.png)

We applied a 9ns input delay to `ulpi_direction` and a 6ns output delay to the `ulpi_data` pins
with the `set_input_delay` and `set_output_delay` commands. Remember that using these 2 commands
is the equivalent of adding flip-flips at the input and at the output of a design with an 
associated delay.

We also know that `ulpi_dir` is directly connected to the output enable signals of the driver of the
bi-directional `ulpi_data` IO pads. 

With clock period of 16.6ns, an input delay of 9ns, and an output delay of 6ns, there's only 1.6ns
left to travel through the FPGA. That's impossible!

![Equivalent ulpi_dir diagram with set_input_delay and set_output_Delay](/assets/io_timings/io_timings-naive_ulpi_dir.svg)

The issue here is the `set_output_delay` specification: inside the PHY chip, `ulpi_data` is indeed latched
by a flip-flop, and for those there absolutely should be a worst-case delay, but that only happens when
`ulpi_direction` is stable. The ULPI specification told us that there's a bus turn-around cycle
whenever there's a change in `ulpi_dir`.

When `ulpi_dir` changes, during this bus turn-around cycle, we need to make sure that the FPGA stop or 
starts directing `ulpi_data` by the end of the clock cycle. In other words, the 6.0ns output delay
doesn't apply.

What we need is 2 `set_output_delay` statements: one with a delay for 0ns for the path from `ulpi_dir`
to `ulpi_data`, and one with a delay of 6ns for the path from the flip-flops inside the FPGA to 
`ulpi_data`. 

**The problem is: there is no way to specify different `set_output_delay` parameters
for different paths!**


# Static Timing Results with Specification Timing Parameters

After synthesizing the design, Quartus Timing Analyzer gives us the following results.

**Setup Time**

The worse case setup path under worst case conditions (85C, slow process) is an output path from a 
`ulpi_data_out` FF inside the link to an input pin of the PHY:

![Worst Case Setup Path Waveform](/assets/io_timings/output_delay_no_output_FF_no_PLL_waveform.png)

*I love the Waveform diagrams of Quartus Timing Analyzer!*

Quartus breaks up the timing path in the following sections:

* 3.508ns clock delay, from the `ulpi_clk` IO pin to the clock pin of the FF that drives
  the content of the `ulpi_data` IO pin.
* 4.863ns data delay, from the output of the FF to the actual `ulpi_data` IO pin.

This gives a total delay of 8.371ns from the `ulpi_clk` pin to the `ulpi_data` IO pin.

* Earlier, the 6.0ns input delay into the PHY was converted into an output delay constraint. 
  It indeed shows up as such in the waveform. When subtracted from the 16.6ns clock period, we
  get a time of 10.6ns: the latest time at which signals that arrive at the PHY
  must be fully stable.

In our case, the FPGA has the signal stable at 8.371ns, which gives us a 2.209ns positive slack.
Setup timing is met!

![Worst Case Setup Path Table](/assets/io_timings/output_delay_no_output_FF_no_PLL_table.png)

**Hold Time**

For the worst case hold time check, you need to run the analyzer on the fastest conditions: 0C, fast process.

When I run a hold time on my design without explicitly specifying IO paths, the IO paths don't even
show up in the list for the first 1000 nets. 

To get the hold violation for the `ulpi_nxt` path, I need to run the following command:

```tcl
report_timing -from ulpi_nxt -hold -npaths 1000 -detail full_path -panel_name {Report Timing} -multi_corner
```

![ULPI_NXT Hold Time Waveform](/assets/io_timings/hold_time_no_output_FF_no_PLL_fail_waveform.png)

* hold time requirement is set to 0ns.
* data delay from the `ulpi_nxt` IO pin to the data input of the first FF is 2.572ns.
* clock delay from the `ulpi_clk` IO pin to clock input of that same FF is 1.965ns.

Add 0.071ns of clock uncertainty, and you end up with a positive hold time slack of 0.536ns.

![ULPI_NXT Hold Time Table](/assets/io_timings/hold_time_no_output_FF_no_PLL_fail_table.png)

*The hold time check for `ulpi_dir` has similar results.*

0.536ns is a respectable margin, and the numbers on my board should be quite a bit higher
because the temperature in my garage is definitely not 0 Celsius! Under worst case conditions
of 85 C and a slow process, the hold time positive slack is 1.4ns. 

So there is no obvious timing violation, and yet the thing doesn't work. 

What can we do next?

# ULPI Reads Failing in the Real World

Once I had a working simulation, I tried ULPI register reads on the actual hardware. That's
where things went off the rails: the expected values were either plain wrong, or the the interface
was hanging.

I used SignalTap to observe what was going on inside the FPGA:

![ULPI Register Read SignalTap Wrong](/assets/io_timings/ulpi_register_read_signaltap_wrong.png)

In the transaction above, you see value 0xC1 being driven onto `ulpi_data`. Remember: the
upper 2 bits of 0xC1, 2'b11, indicate a register read, and the lower 6 bits, 0x01, indicate the address. 
According to the ULPI specification, register 0x01 contains the MSB of the vendor ID of the PHY. 
The TUSB1210 PHY has a vendor ID of 0x0451. The PHY should return 0x04, but it's returning 0x51!

You can also see how `ulpi_nxt` gets asserted during the first cycle during which 0xC1 is being  
driven by the link.

What is going on here?

The *obvious* first reaction is it that there's a problem with the chip. Everything is simulating fine,
how could I possibly be the problem! I was 
[not the only one with this reaction](https://community.intel.com/t5/Intel-Quartus-Prime-Software/Strange-code-behavior-once-it-works-once-not/m-p/253916/highlight/true?profile.language=ja):

> Maybe I have a clue - I could not communicate with tusb1210 as it is written in ULPI standard. To write to tusb1210 register, 
> I had to make some hacks (i.e. register usb_stupid_test in `top/ULPI.v`), what is ridiculous, but after this hack it finally 
> started to work (for few days...).

But this is a chip that has been in production for years, and there are only 
[2 minor erratas](https://www.ti.com/lit/er/sllz066/sllz066.pdf?ts=1630776676403). 
When with misbehaving C code, assuming a bug in the compiler should be your very last option.  The same is through 
for issues like this.

**When the real world doesn't match your simulation, chances are high that there's a signal integrity or
a timing issue.**

# First Principle Analysis of the Failing Waveform

Let's go back to the beginning and look at the expected waveform, and the waveform recorded by
the SignalTap logic analyzer:

Exptected:

![ULPI Register Read Simulation](/assets/io_timings/ulpi_register_read_simulation_correct.png)

Recorded:

![ULPI Register Read SignalTap Wrong](/assets/io_timings/ulpi_register_read_signaltap_wrong.png)

Once again, we see that in the failing case, `ulpi_nxt` gets asserted during the first cycle,
the cycle in which 0xC1 shows up on the bus. This can simply not happen when `ulpi_nxt` is
driven directly by a flip-flop and under theoretical conditional where the clock edge rises
at exactly the same time everywhere in the synchronous design.

But what happens if that is not the case?

That's what happens below. (Click on the image to get the enlarged version!)

[![ULPI NXT hold time violation](/assets/io_timings/hold_violation.png)](/assets/io_timings/hold_violation.svg){:target="_blank"}

First, we see the delay between the clock at the IO pin of the PHY and the core of the link.

Then we see the progression of events starting with the link sending out a register read
address on `ulpi_data`, the reaction of the PHY by asserting `ulpi_nxt`, how that assertion
is perceived by the link, and ultimately, captured by SignalTap.

If the delay between the clock inside the link in the Phy is large enough, and if the
delay between the FF that creates `ulpi_nxt` in the phy and the arrival of that signal at a FF
inside the link is short enough, you get a classic case shoot-through, where a signal
that meant to arrive at the next cycle, arrives a cycle earlier.

The pattern of the timing diagram above exactly matches the pattern that was captured on the
real SignalTap.

# Fix 1: More Stringent Hold Time Settings

If the theory about an ordinary hold time violation on `ulpi_nxt` is correct, then a potential
fix would be increase the minimum input delay requirements on that signal. Let's change
it from 0ns to -1.0ns:

```tcl
set_input_delay -min -clock [get_clocks {ulpi_clk}] -1.0 [get_ports {ulpi_data[*]}]
set_input_delay -min -clock [get_clocks {ulpi_clk}] -1.0 [get_ports {ulpi_direction}]
set_input_delay -min -clock [get_clocks {ulpi_clk}] -1.0 [get_ports {ulpi_nxt}]
```
Here's the result on SignalTap:

![Register Read Pass](/assets/io_timings/signaltap_pass.png)

It's working now! 

Here's hold time waveform:

![Hold Time with lower input delay](/assets/io_timings/hold_time_with_lower_input_delay_pass_waveform.png)

Compare this figure to the failing case above and... we have a mystery on our hands:
j
* The input delay has been changed from 0ns to -1.0ns, as requested.
* The data delay has increase from 2.572ns to 3.749ns.

    An increase by little more than 1 ns.

* The clock delay is rouglhy the same, with an increase from 1.965ns to 2.096ns.

The end result is that the positive slack is 0.582ns, only 50ps more than the failing case.

When I increase the input delay from -1.0ns to -1.5ns, the data delay increases again by the same amount:
from 3.749ns to 4.240ns. And the resulting positive slack is 0.573ns. For whatever reason, Quartus
force the hold time slack to be ~0.575ns.

Note, however, that this is for the fastest transistor conditions, 0C and fast silicon. Under 
slowest conditions, and with an input delay of -1.5ns, the hold time slack increases from
the earlier 1.4ns to 3.1ns.

The slack on my board, room temperature and probably some silicon that has average speed, must
be somewhere between 0.5ns and 3.1ns.

I find this a very unsatisfying situation: yes, I identified the failing case as a hold time
violation, and, yes, my board is working now. But I don't have timing reports that prove that
a failing condition has been corrected. And because of that, I also can't be sure that my
design works under all silicon conditions.

Unfortunately, there is no easy way on the DECA board to probe the `ulpi_clk` and `ulpi_nxt` signals
close to the FPGA.

# Fix 2: Use a PLL to Align the Phy Clock and the Link Clock

Hold time violations are caused by delays between the launch clock and the capture clock of 
a signal. When these 2 clock edges coincide, a hold violation isn't possible.

In the earlier fix, changing the minimum input delay touched the data delay path, but it didn't fix
the issue of clocks that were skewed by ~2ns due to delay in the clock IO path and the global clock
buffer of the FPGA.

A different fix does just that: it uses a PLL with 1:1 ratio that tries to perfectly align the 
clock at the input of the PLL with the clock at the output of the global clock buffer.


![SN74AVC1T45 Switching Delay](/assets/io_timings/sn74avc1t45_switching_delay.png)


# References

* [USB 2.0 Transceiver Macrocell Interface (UTMI) Specification 1.05][UTMI-specification]
* [UTMI+ Specification Revision 1.0](https://www.nxp.com/docs/en/brochure/UTMI-PLUS-SPECIFICATION.pdf)
* [ULPI Specification][ULPI-specification]
* [Texas Instruments TUSB1210 Product Page][TUSB1210-product-page]
* [Microchip/SMSC USB3300 Product Page][USB3300-product-page]
* [Zed Board Errata: TUSB1210 Min Output Delay](https://www.avnet.com/opasdata/d120001/medias/docus/7/Avnet-ZedBoard-RevD.2-EN-Errata.pdf)

[UTMI-specification]: https://www.intel.com/content/dam/www/public/us/en/documents/technical-specifications/usb2-transceiver-macrocell-interface-specification.pdf
[ULPI-Specification]: https://www.sparkfun.com/datasheets/Components/SMD/ULPI_v1_1.pdf
[TUSB1210-product-page]: https://www.ti.com/product/TUSB1210
[USB3300-product-page]: https://www.microchip.com/wwwproducts/en/USB3300

* Ryan Scoville's [TimeQuest User Guide](https://www.intel.com/content/dam/altera-www/global/en_US/uploads/3/3f/TimeQuest_User_Guide.pdf)

# Footnotes

