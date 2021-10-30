---
layout: post
title: The Intel JTAG Primitive - Using JTAG without Virtual JTAG
date:  2021-10-30 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my blog post about the Intel JTAG UART](/2021/05/02/Intel-JTAG-UART.html),
I wrote about Intel's [Virtual JTAG](/2021/05/02/Intel-JTAG-UART.html#the-intels-virtual-jtag-system) system:
an ingenious way to connect up to 254 clients to a central JTAG hub, with client discovery features and other good stuff.

![Intel Virtual JTAG diagram](/assets/jtag_uart/intel_virtual_jtag.png)

Intel uses it for its own JTAG debug units, JTAG UART, SignalTap, Nios2 debugger, but it also supports adding
[your own units](https://github.com/binary-logic/vj-uart).

All of that is is great, but there's one problem: if you don't want to use the Quartus SystemConsole (and the pleasure of using $#!#$ 
Tcl to control it), then you need a bit of a software layer to do JTAG client discovery, select the right JTAG client, and the custom
ways to send instructions and data to the client TAP.

OpenOCD has [this software layer](https://github.com/openocd-org/openocd/blob/master/src/target/openrisc/or1k_tap_vjtag.c), 
but it's only supported for OpenRisc CPUs and its JTAG UART. In an ideal world, OpenOCD should expand that support for many more CPUs and 
targets, and there was some chatter about it by an Intel employee on the OpenOCD mailing list, but so far it hasn't happened.

On Xilinx and most Lattice FPGAs, there are much easier ways to connect a user-defined JTAG scan chain to the FPGA TAP controller: you just
need to instantiate a BSCANE (Xilinx) or a JTAGG (Lattice) primitive cell, connect one or two chains, and that's it.

But Intel doesn't have such a primitive cell... Or so I thought, until 
somebody mentioned the existence of such a thing 
[in a thread on the /r/FPGA subreddit](https://old.reddit.com/r/FPGA/comments/q01mar/connect_fpgas_jtag_if_with_softcores_jtag/hf6gtli/):

> Alternatively you can instantiate the JTAG primitive and bypass the SLD junk. That works fine with OpenOCD. 
> You can see a migen/LiteX example here: 
> [https://gist.github.com/jevinskie/811a4fd6deba7fff7280f6908ae37437](https://gist.github.com/jevinskie/811a4fd6deba7fff7280f6908ae37437)

The example given is written in Migen, which is amazing if you can stand the syntax (I can't, unfortunately, and for hobby stuff, I don't want
to use things that I don't like), but it doesn't really explain what's going on.

In this blog post, I'll explain what the primitive does, and create my own example.

# Intel's JTAG Controller Primitive

So, Intel has a JTAG primitive that can be used to connect your own scan chain. Or better: primitives, because
different FPGA families have primitives with a different name:

```
component arriaii_jtag
component arriaiigz_jtag
component arriav_jtag
component arriavgz_jtag
component cyclone_jtag
component cyclone10lp_jtag
component cycloneii_jtag
component cycloneiii_jtag
component cycloneiiils_jtag
component cycloneiv_jtag
component cycloneive_jtag
component cyclonev_jtag
component fiftyfivenm_jtag
component maxii_jtag
component maxv_jtag
component stratix_jtag
component stratixgx_jtag
component stratixii_jtag
component stratixiigx_jtag
component stratixiii_jtag
component stratixiv_jtag
component stratixv_jtag
component twentynm_jtagblock
component twentynm_jtag
component twentynm_hps_interface_jtag
component fiftyfivenm_jtag
```

Other FPGA vendors have different primitives as well, Lattice, for example, has [`JTAGA` to `JTAGG`](https://github.com/tomverbeure/ecp5_jtag/blob/main/README.md).

I'm using an [Arrow DECA](/2021/04/23/Arrow-DECA-FPGA-board.html) 
board with a MAX10 FPGA. There's no `max10_jtag` primitive in the list above, but fear not, it uses the
`fiftyfivenm_jtag` block... because MAX10 uses a 55nm silicon process.

The ports of the `fiftyfivenm_jtag` primitive can be found in a the `fiftyfivenm_atoms.v` simulation
library of my Quartus installation, in my `./intelFPGA_lite/20.1/quartus/eda/sim_lib/`
directory.

```verilog
...

module    fiftyfivenm_jtag    (
    tms,
    tck,
    tdi,
    tdoutap,    //controller by fsac_allow_fiftyfivenm_tdoutap INI
    tdouser,
    tmscore,    //controller by sgn_enable_fiftyfivenm_jtag_core_access INI
    tckcore,    //controller by sgn_enable_fiftyfivenm_jtag_core_access INI
    tdicore,    //controller by sgn_enable_fiftyfivenm_jtag_core_access INI
    corectl,    //controller by sgn_enable_fiftyfivenm_jtag_core_access INI
    ntdopinena, //controller by sgn_enable_fiftyfivenm_jtag_core_access INI
    tdo,
    tmsutap,
    tckutap,
    tdiutap,
    shiftuser,
    clkdruser,
    updateuser,
    runidleuser,
    usr1user,
    tdocore             //controller by sgn_enable_fiftyfivenm_jtag_core_access INI
);

    parameter    lpm_type    =    "fiftyfivenm_jtag";

    input tms;
    input tck;
    input tdi;
    input tdoutap;
    input tdouser;
    input tmscore;
    input tckcore;
    input tdicore;
    input corectl;
    input ntdopinena;

    output tdo;
    output tmsutap;
    output tckutap;
    output tdiutap;
    output shiftuser;
    output clkdruser;
    output updateuser;
    output runidleuser;
    output usr1user;
    output tdocore;

...
```

There's almost no official documentation of the JTAG primitives, and whatever exists is in the context
of FPGA design security features. 
If found Intel application note [AN 556: Using the Design Security Features in Intel FPGAs](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/an/an556.pdf)
the most useful. Only a small part of the app note involves the JTAG primitive, but page 32 has the following
diagram:

![Intel JTAG primitive diagram](/assets/intel_jtag_primitive/intel_jtag_primitive.png)

We can see 3 functional regions:

* The section is blue is the primitive itself. It contains a standard JTAG test access port (TAP) controller
and some multiplexers. This section is a fixed part of the FPGA, not something that lives in the programmable
core region. After all, you need this to load a new bitstream in an empty FPGA.
* The bottom right are the FPGA IO pins that are reserved for JTAG operation. These
are the pins to which you connect your USB Blaster if your FPGA board doesn't have a USB Blaster integrated
on the PCB (as is the case for my Arrow DECA board.)
* The top right lives in the programmable part of the FPGA. This is the part that we can play with.

*Don't take this diagram as gospel: it's a fairly accurate representation, but some things don't apply
to the JTAG primitives of all FPGA families. For example, the `ntdopinenable` pin of the `fiftyfivenm_jtag`
cell has no impact on my MAX10 design.*

# A Huge Caveat when Using the JTAG Controller Primitive

You need to be aware of a major issue when you want to bypass the Virtual JTAG infrastructure and roll your own
JTAG logic: **you can't use anything anymore that relies on virtual JTAG!**

Forget about debugging your design with a SignalTap: it's not going to happen.

It's already not common to use JTAG for your own projects, but this restriction makes using the 
JTAG primitive a hard sell. Still, there are some cases where it might be useful:

* The SLD hub of the virtual JTAG infrastructure requires around 150 logic cells. That's nothing for 
  a large FPGA, but on something like a MAX10 10M02 with just 2000 logic elements, those 150 cells
  could be very uncomfortable. (See [this post on Intel's support forum](https://community.intel.com/t5/Programmable-Devices/JTAG-USER1-register-on-Max-10/m-p/1255094/highlight/true#M78858).)
* Designs that were ported over from smaller CPLDs might rely on the JTAG primitive. It's good to be backward
  compatible. 
* The already mentioned software layer that's needed to operate virtual JTAG might stand in the way. A
  good example is my favorite little CPU, the VexRiscv. Its JTAG debug unit along with its custom
  version of OpenOCD (see [my earlier blog post](/2021/07/18/VexRiscv-OpenOCD-and-Traps.html) can be made 
  to work with pretty much any JTAG chain, but virtual JTAG is not supported.
* the JTAG primitive makes it possible to open up certain design security features that were locked
  down with a fuse. This is not important for hobby designs, but there are production situations where
  this can be important.

# The JTAG Controller Primitive to Bypass Design Security Features

Official documentation fo the JTAG primitive is very hard to find, and whatever exists is
in the context of FPGA design security features. Most hobbyists will not use that, but it's still
interesting in its own right, so let's talk about that first and turn to Intel application
note 
[AN 556: Using the Design Security Features in Intel FPGAs](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/an/an556.pdf).

The most important usage of an FPGA JTAG port is to load new bitstream into the FPGA or to program a new
bitstream into a connected flash PROM. Modern FPGAs have all kinds of additional features, such as 
programming a non-volatile bitstream decryption key (one time only!), loading a volatile bitstream
decryption key, setting a tamper protection fuse, JTAG access lock and so forth. These features are commonly 
used in a board production environment, and JTAG is the perfect port to control that.

On Intel FPGAs, the JTAG access lock feature is particularly interesting: it disables all non-standard JTAG instructions.
Only vanilla instructions such as `BYPASS`, `IDCODE, `EXTEST` etc (see table 17 of the AN 556 application
note) remain after a bitstream has been loaded.

It is possible to disable the JTAG access lock by shifting in the UNLOCK instruction into the JTAG controller.
Which is funny, because all non-standard instructions where disabled?! 

Intel has the perfect solution for that: it's JTAG primitive has the option to drive the FPGA TAP with
internal signals instead of the external IOs. If you want to disable access lock, your own design needs
to create a JTAG-compatible trace.

The application note describes how to use the JTAG primitive in that kind of situation, but nothing else.

# The JTAG Controller Primitive to Attach Your Own Custom User Scan Chain

With the access security part behind us, let's look at the interesting, undocumented, part: attaching
you own custom scan chain to the JTAG TAP.

Let's go over the different pins of the Intel JTAG primitive.

**Standard JTAG TAP Control Pins**

The first 4 pins are the standard JTAG pins and must be connected directly to the FPGA JTAG IO pins.

| Signal Name | Direction | Description | 
|-------------|-----------|-------------|
| tck | input | FPGA TCK IO pin | 
| tms | input | FPGA TMS IO pin | 
| tdi | input | FPGA TDI IO pin | 
| tdo | output | FPGA TDO IO pin | 

In Quartus, the JTAG IO pins have the `altera_reserved_` prefix. All you need to
do is wire them up like this:

```verilog
module top(
        input  wire     clk,
        input  wire     button,
        output reg      led0,
        output reg      led1,
        output reg      led2,

        input  wire     altera_reserved_tck,
        input  wire     altera_reserved_tms,
        input  wire     altera_reserved_tdi,
        output wire     altera_reserved_tdo
    );

...

    fiftyfivenm_jtag u_jtag(
        .tms(altera_reserved_tms),
        .tck(altera_reserved_tck),
        .tdi(altera_reserved_tdi),
        .tdo(altera_reserved_tdo),

...
```

**Alternate Core JTAG TAP Control Signals**

The next 4 signals are the alternate JTAG signals that are used to control the JTAG TAP
from the FPGA core logic. These are the pins that are used in the earlier described
situation when you want the core logic to send JTAG commands to the TAP.

| Signal Name | Direction | Description | 
|-------------|-----------|-------------|
| corectl | input | Switch JTAG TAP pins to alternate control pins. |
| tckcore | input | Alternate TCK pin that comes from the core logic| 
| tmscore | input | Alternate TMS pin that comes from the core logic| 
| tdicore | input | Alternate TDI pin that comes from the core logic| 
| tdocore | output | Alternate TDI pin that comes to the core logic| 

`corectl` must be set to 1 switch from external IOs to core signals.

For our use case, we can simply strap this signal to 0, and always control the
JTAG TAP with external IOs.

*Some Intel FPGAs, such as the Cyclone 10 LP family, don't support `tckcore, 
`tmscore`, `tdicore` and the `corectl` pins. You could just not wire them up
and count on Quartus strapping them to 0 by default...*

**User JTAG Signals**

| Signal Name | Direction | Description | 
|-------------|-----------|-------------|
| tckutap | output | Core version of external JTAG TCK IO pin |
| tmsutap | output | Core version of external JTAG TMS IO pin |
| tdiutap | output | Core version of external JTAG TDI IO pin |

The earlier mentioned `tck`, `tms`, `tdi` pins can only be connected to the
external IO pins. They are not available for use by the FPGA core logic.
However, they are fed through to these 3 signals, which are available to 
the FPGA core logic.

You can use them to connect them to your own JTAG TAP (to track the 
states of the FPGA JTAG TAP), to shift data into your own shift register etc.

FIXME: | tdoutap | input | Core version of external JTAG TCK IO pin |

**User Scan Chain Control Signals**

The next signals are some of the most useful if you want to quickly connect your own
scan chain to the FPGA TAP. I could not find any official documentation for any
of these signals, but it was easy to figure out after bringing them out to some
FPGA GPIOs and recording transactions with a Saleae Logic Pro 16 logic analyzer.

| Signal Name | Direction | Description | 
|-------------|-----------|-------------|
| usr1user | output | High when the IR register is set to USER1 (0x00e). |
| clkdruser | output | TCK clock when when IR is USER0 or USER1 and the TAP states are Capture-DR or Shift-DR.   |
| shiftuser | output | High when IR is USER0 or USER1 and the TAP state is Shift-DR.  |
| updateuser | output | High when IR is USER0 or USER1 and the TAP state is Update-DR. |
| runidleuser | output | High when IR is USER0 or USER1 and the TAP state is Run-Test/Idle. |
| tdouser | input | Routed to TDO when IR is USER0 or USER1. |

The Intel JTAG TAP has built-in support for 2 core provided scan chains, USER0 and USER1, that
can be selected with IR values of 0x00c and 0x00d resp. They are normally used to make all
virtual JTAG magic happen, but without that, we can now use them as we want.

This example attaches a scan chain to USER0:

```verilog
    reg [7:0] user0_shiftreg = 0;
    reg [7:0] user0_reg      = 0;

    always @(posedge tckutap) begin
        if (!usr1user) begin
            if (shiftuser) begin
                user0_shiftreg  <= { tdiutap, user0_shiftreg[7:1] };
            end
    
            if (updateuser) begin
                user0_reg       <= user0_shiftreg;
            end
        end
    end

    always @(negedge tckutap) begin
        tdouser  <= !usr1user ? user0_shiftreg[0] : 1'b0;
    end
```

# A Tracking JTAG TAP FSM

The `user` signals are sufficient load a shift register with a new value
and update the final register, but, inexplicably, there's no
`captureuser` equivalent to load the shift register with a value
right before scanning out.

This can be remedied by adding an FSM in the core logic that tracks the states of the 
FPGA TAP by using the `tckutap` and `tmsutap` signals.

There are million open source JTAG TAP FSM implementations out there. I'd be remiss if 
I didn't add one myself:

```verilog
    localparam jtag_exit2_dr            = 0;
    localparam jtag_exit1_dr            = 1;
    localparam jtag_shift_dr            = 2;
    localparam jtag_pause_dr            = 3;
    localparam jtag_select_ir_scan      = 4;
    localparam jtag_update_dr           = 5;
    localparam jtag_capture_dr          = 6;
    localparam jtag_select_dr_scan      = 7;
    localparam jtag_exit2_ir            = 8;
    localparam jtag_exit1_ir            = 9;
    localparam jtag_shift_ir            = 10;
    localparam jtag_pause_ir            = 11;
    localparam jtag_run_test_idle       = 12;
    localparam jtag_update_ir           = 13;
    localparam jtag_capture_ir          = 14;
    localparam jtag_test_logic_reset    = 15;

    reg [3:0] jtag_fsm_state = 15;

    always @(posedge tckutap) begin
        case(jtag_fsm_state) 
            jtag_test_logic_reset: jtag_fsm_state <= tmsutap ? jtag_test_logic_reset : jtag_run_test_idle;
            jtag_run_test_idle   : jtag_fsm_state <= tmsutap ? jtag_select_dr_scan   : jtag_run_test_idle;
            jtag_select_dr_scan  : jtag_fsm_state <= tmsutap ? jtag_select_ir_scan   : jtag_capture_dr;
            jtag_capture_dr      : jtag_fsm_state <= tmsutap ? jtag_exit1_dr         : jtag_shift_dr;
            jtag_shift_dr        : jtag_fsm_state <= tmsutap ? jtag_exit1_dr         : jtag_shift_dr;
            jtag_exit1_dr        : jtag_fsm_state <= tmsutap ? jtag_update_dr        : jtag_pause_dr;
            jtag_pause_dr        : jtag_fsm_state <= tmsutap ? jtag_exit2_dr         : jtag_pause_dr;
            jtag_exit2_dr        : jtag_fsm_state <= tmsutap ? jtag_update_dr        : jtag_shift_dr;
            jtag_update_dr       : jtag_fsm_state <= tmsutap ? jtag_select_dr_scan   : jtag_run_test_idle;
            jtag_select_ir_scan  : jtag_fsm_state <= tmsutap ? jtag_test_logic_reset : jtag_capture_ir;
            jtag_capture_ir      : jtag_fsm_state <= tmsutap ? jtag_exit1_ir         : jtag_shift_ir;
            jtag_shift_ir        : jtag_fsm_state <= tmsutap ? jtag_exit1_ir         : jtag_shift_ir;
            jtag_exit1_ir        : jtag_fsm_state <= tmsutap ? jtag_update_ir        : jtag_pause_ir;
            jtag_pause_ir        : jtag_fsm_state <= tmsutap ? jtag_exit2_ir         : jtag_pause_dr;
            jtag_exit2_ir        : jtag_fsm_state <= tmsutap ? jtag_update_ir        : jtag_shift_ir;
            jtag_update_ir       : jtag_fsm_state <= tmsutap ? jtag_select_dr_scan   : jtag_run_test_idle;
        endcase
    end

    wire capture_dr;
    assign capture_dr    = (jtag_fsm_state == jtag_capture_dr);
```

`capture_dr` will trigger whenever the FSM passes throught the Capture-DR state. In combination with the
`usr1user` signal, we can use this to capture a new value into the USER1 shift register, but we can't do
that for USER0 since there's no separate `usr0user` signal. So if we want that, we need to track the contents
of the IR register too:

```verilog
    reg [9:0] ir_shiftreg = 0;
    reg [9:0] ir_reg = 0;

    always @(posedge tckutap) begin
        if (jtag_fsm_state == jtag_shift_ir) begin
            ir_shiftreg <= { tdiutap, ir_shiftreg[9:1] };
        end

        if (jtag_fsm_state == jtag_update_ir) begin
            ir_reg <= ir_shiftreg;
        end
    end
```

We can now create a `captureuser` signal, and use that to capture a value in the USER0 shift register before
shifting out. In the example below, we're capturing the number of times the USER0 register has seen a capture-DR
event:

```verilog
    // 0x00C: USER0, 0x00E: USER1
    wire captureuser;
    assign captureuser = capture_dr && (ir_reg == 10'h00c || ir_reg == 10'h00e);

    reg [7:0] user0_shiftreg = 0;
    reg [7:0] user0_reg      = 0;

    reg [7:0] user0_counter  = 0;

    always @(posedge tckutap) begin
        if (!usr1user) begin
            if (captureuser) begin                      // <----------------
                user0_shiftreg  <= user0_counter;
                user0_counter   <= user0_counter + 1;
            end

            if (shiftuser) begin
                user0_shiftreg  <= { tdiutap, user0_shiftreg[7:1] };
            end
    
            if (updateuser) begin
                user0_reg       <= user0_shiftreg;
            end
        end
    end

    always @(negedge tckutap) begin
        tdouser  <= !usr1user ? user0_shiftreg[0] : 1'b0;
    end
```


