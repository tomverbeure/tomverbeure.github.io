---
layout: post
title: Cosimulating Verilog and VHDL with CXXRTL
date:  2020-11-04 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my first blog post about CXXRTL](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html), I talked
about how CXXRTL is just a Yosys backend, and that this has the benefit that it can simulate anything
that has been converted from some source input format (Verilog, blif, VHDL, SystemVerilog) to the
Yosys' internal RTLIL format.

Most people think of Yosys as a tool to synthesize Verilog, and that's definitely the dominant use
case, but in the past years, significant progress has been made in integrating 
[gHDL](https://ghdl.readthedocs.io/en/latest/about.html), an open source VHDL compiler, into
Yosys as well.

The result of this effort is [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin). It's not
part of the main Yosys GitHub repo (yet?), but a stand-alone Yosys plugin that has its own GitHub
project.

I spent the first 10 years of my career writing VHDL (and, not knowing any better, I was a big fan of it),
but after moving to the US West Coast, I've been a happy Verilog user. And I want to keep it that way!

But I thought it'd be fun to convert theory into practise, and see how far gHDL and the gHDL Yosys plugin
have progressed, and if it was possible to simulate a trivial VHDL design with Yosys and CXXRTL.

Taking things a step further, I also tried to run a Verilog/VHDL cosimulation, where one part of the design
is written in Verilog, and another in VHDL.

# Installating a Yosys + gHDL Combo

If you've already compiled Yosys in the past, installing gHDL and the plug-in is surprisingly easy. On an Ubuntu 20.4 
system, it took less than 20 min, and almost all of that was just compilation time.

Here are the steps:

* Build and install the latest version of [Yosys](https://github.com/YosysHQ/yosys)

    The Yosys project describes very well how to compile.

* Build and install gHDL

    * Install `gnat`

        GNAT is the GNU ADA compiler. VHDL constructs are based on ADA language constructs, and a
        large part of gHDL is written in ADA.

        On my system, it was as simple as running `sudo apt install gnat-9`

    * Clone ghdl repo and compile

        ```
        git clone https://github.com/ghdl/ghdl.git` 
        cd ghdl
        ./configure --prefix=/opt/ghdl
        make install
        ```

        I install most experimental tools in the `/opt` directory. By default, everything gets installed
        in `/usr/local/` instead.

    * Add the gHDL binary to your PATH

        I added the following line to `~/.profile`: 

        ```
        export PATH=/opt/ghdl/bin:$PATH
        ```
        
* Build Install [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)

    ```
    git clone https://github.com/ghdl/ghdl-yosys-plugin.git
    cd ghdl-yosys-plugin
    # GHDL needs to point to the executable, not the installation path!
    make GHDL=/opt/ghdl/bin/ghdl
    sudo make GHDL=/opt/ghdl/bin/ghdl install
    ```

    When the `yosys` binary is in your PATH, the last line above will copy the `ghdl` plugin to the
    `/usr/local/share/yosys/plugins/` directory.


And that's really it!

# Compiling and Simulating Your First VHDL Code with Yosys

The canonical way to process VHDL code has 2 major steps:

* Analyze the VHDL code

    This step parser the VHDL code, does a bunch of syntactic and semantic checks, and stores the
    analyzed design objects in a library. The default library is the "work" library.

* Elaborate the analyzed design

    During this step, the various analyzed design objects are merged together, various conditional generation
    options are executed, interconnections are verified etc.

Verilog has the same steps, but they're usually not made explicity.

When using gHDL in combination with Yosys, the regular `ghdl` command (outside of Yosys) is used to analyze
all the VHDL code into a standard gHDL library. And the `ghdl` command inside Yosys, which was added through
the plugin, is used to elaborate the design and convert it to Yosys' RTLIL format.

Once available in RTLIL format, running a CXXRTL simulation is no different for VHDL than for a Verilog design.

I converted my trivial [`blink_basic`](https://github.com/tomverbeure/cxxrtl_eval/tree/master/blink_basic) CXXRTL example 
to VHDL. You can find it in the [`blink_basic_vhdl'](https://github.com/tomverbeure/cxxrtl_eval/tree/master/blink_basic_vhdl)
directory.

The design is just an LED connected to a bit of a counter:

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity blink is
    port (
        clk     : in std_logic;
        led     : out std_logic
    );
end blink;

architecture RTL of blink is
    signal counter          : unsigned(11 downto 0) := "000000000000";
begin

    process(clk) begin
        if rising_edge(clk) then
            counter         <= counter + 1;
        end if;
    end process;

    led <= counter(7);

end RTL; 
```

**Analyze the VHDL**

```
ghdl analyze blink_basic.vhdl
```

If all goes well, `ghdl` won't print anything on the screen, but you'll notice that a `work-obj93.cf` file was created.
That's the work library with the analyzed design.


**Create the CXXRTL simulation model with Yosys**

Load the design into Yosys, elaborate and converted it RTLIL with the new `ghdl` command, and create a CXXRTL simulation file:

```
yosys -m ghdl "ghdl blink; write_cxxrtl blink.cpp
```

The `-m ghdl` part tells Yosys to load the `ghdl` plugin.

**Compile the design and testbench into an executable**

```
clang++ -g -O3 -std=c++14 -I `yosys-config --datdir`/include main.cpp  -o blink
```

**Run the simulation**

```
~/projects/cxxrtl_eval/blink_basic_vhdl$ ./blink 
cycle 128 - led: 1, counter: 129
cycle 256 - led: 0, counter: 257
cycle 384 - led: 1, counter: 385
cycle 512 - led: 0, counter: 513
cycle 640 - led: 1, counter: 641
cycle 768 - led: 0, counter: 769
cycle 896 - led: 1, counter: 897
```

Whenever I'm dealing with projects that require tying together different tools, I expect a lot of hassle with compilation
and integration issues, but there's was none of that here: everything just worked&trade;!

# Cosimulating a VHDL RISC-V CPU inside a Verilog SOC

If you already used gHDL to simulate your pure VHDL designs, there's really no need to use CXXRTL unless
you depend on one of its specific strengths.

But here's something that no open source simulator has been reserved for expensive proprietary simulators
for decades: cosimulation of mixed Verilog/VHDL designs! 

To demonstate this, I started with [my original RISC-V design](https://github.com/tomverbeure/cxxrtl_eval/tree/master/spinal/src/main/scala/example)
that I used to benchmark CXXRTL and to demonstrate [simulation save/restore checkpoints](/2020/10/26/Simulation-Save-Restore-with-CXXRTL.html). 

It's originally written in [SpinalHDL](https://spinalhdl.github.io/SpinalDoc-RTD/), but SpinalHDL generated a Verilog file
that can be found [here](https://github.com/tomverbeure/cxxrtl_eval/blob/master/spinal/ExampleTop.sim.v) in my repo as well.

Here's what I did:

* Load the full original Verilog design (which includes a VexRiscv CPU) into Yosys
* Remove the VexRiscv module from the design database
* Compile a VHDL-based RISC-V CPU with gHDL
* Write a Verilog wrapper that glues the new RISC-V CPU to the external interface of the VexRiscv
* Simulate this Frankenstein design with CXXRTL

You can find everything in the [rpu_vhdl directory](https://github.com/tomverbeure/cxxrtl_eval/tree/master/rpu_vhdl)
of my [cxxrtl_eval](https://github.com/tomverbeure/cxxrtl_eval) GitHub repo.

[`./run.sh`](https://github.com/tomverbeure/cxxrtl_eval/blob/master/rpu_vhdl/run.sh) is 
all you need to compile and simulate!

**VectorBlox RISC-V CPU**

VectorBlox was a startup that designed the open source ORCA RISC-V CPU. They were acquired by Microchip,
but there are still some cloned GitHub repos out there with the source code. I tried hard to use this
CPU because it has a similar pipeline and interfaces as a VexRiscv, but I'm pretty sure I ran into
a pipelining bug in their load/store unit.


**RPU RISC-V CPU**

I then switched to Colin Riley's (aka [@domipheus](https://twitter.com/domipheus)) RPU. Much like the 
ubiquitous [picorv32](https://github.com/cliffordwolf/picorv32), it's a very slow RISC-V implementation 
that only executes one instructions at time, instead of processing multiple instructions in different pipeline 
stages. 

You can find the original RPU [here](https://github.com/Domipheus/RPU).

Instead of split instruction and data bus, it only has a single memory bus for both, which is just fine
for my usage.

**Analyze the VHDL**

This is just an extension of the earlier example.

Note that I'm using VHDL-2008 (the default is VHDL-93). This is not necessary for this design, but
it was necessary to analyze the ORCA design. If you later run the `ghdl` command instead Yosys, 
make sure to specify the matching standard version as well!

```
RPU=./RPU/vhdl/

OPTIONS="--std=08 -fsynopsys"

ghdl -a $OPTIONS $RPU/constants.vhd $RPU/alu_int32_div.vhd \
                 $RPU/control_unit.vhd $RPU/csr_unit.vhd \
                 $RPU/lint_unit.vhd $RPU/mem_controller.vhd \
                 $RPU/pc_unit.vhd $RPU/register_set.vhd \
                 $RPU/unit_alu_RV32_I.vhd $RPU/unit_decoder_RV32I.vhd \
                 $RPU/core.vhd
```

**VexRiscv_wrapper.v**

The [wrapper design](https://github.com/tomverbeure/cxxrtl_eval/blob/master/rpu_vhdl/VexRiscv_wrapper.v) is 
simple, with a minor twist.

The SOC design expects an instruction memory bus and a data memory bus. The RPU has only one
bus, so I'm tying that interface to the data bus of the SOC, and strap the instruction bus to
idle.

Most RISC-V CPUs handle byte to 32-bit word alignment inside the CPU core, but the RPU does not. So the following
[adaption logic](https://github.com/tomverbeure/cxxrtl_eval/blob/469037922a7b5883aa2c7c607d152c550dfc2b1f/rpu_vhdl/VexRiscv_wrapper.v#L79-L93) 
was required in the wrapper:

```verilog
  always @(*) begin
      MEM_I_data    = dBus_rsp_data;        // Default to avoid a latch

      case(MEM_O_byteEnable)
          2'b00: begin
              // Byte access
              MEM_I_data    = (dBus_rsp_data >> (MEM_O_addr[1:0] * 8)) & 32'hff;
          end
          2'b01: begin
              // HalfWord access
              MEM_I_data    = (dBus_rsp_data >> (MEM_O_addr[1] * 16)) & 32'hffff;
          end
          2'b10: begin
              MEM_I_data    = dBus_rsp_data;
          end
      endcase
  end
```

I didn't wire up an interrupts, etc. This is just a basic example!

**Processing in Yosys**

Yosys ties everyting together:

```
# Load the Verilog design with the VexRiscv CPU
read_verilog ../spinal/ExampleTop.sim.v
# Remove the VexRiscv module from the design database
delete VexRiscv
# Load a replacement VexRiscv design that instantiates the RPU
read_verilog VexRiscv_wrapper.v
# Elaborate the RPU (named "core") to RTLIL
ghdl --std=08 core
# Bring together all design modules into 1 hierarchical design
hierarchy -check -top ExampleTop
# Create CXXRTL simulation model
write_cxxrtl -Og ExampleTop.sim.cpp
```
**Compile testbench and design model to an executable**

I'm using exactly the same testbench code as the one for my
CXXRTL benchmark:

```
clang++-9 -g -O3 -I`yosys-config --datdir`/include  \
        -DEXAMPLE_TOP=\"ExampleTop.sim.cpp\" 
        -std=c++14 -I../lib main.cpp ../lib/cxxrtl_lib.cpp 
        -o tb
```

The result is a `./tb` executable binary.

**Simulate!!!**

```
> ./tb 2 waves.vcd

UART TX: 
UART TX: 

UART TX: H
UART TX: e
UART TX: l
UART TX: l
UART TX: o
UART TX:  
UART TX: W
UART TX: o
UART TX: r
UART TX: l
UART TX: d
UART TX: !
UART TX: 
UART TX: 

led_red: 1 0
led_red: 0 1
led_green: 1
led_green: 0
led_blue: 1
led_red: 1 1
led_blue: 0
led_red: 0 2
led_green: 1
led_green: 0
```

The RPU only executes about 1 instruction every 5 clock cycles whereas the
VexRiscv is a bit less than 1 instruction every 1.1 clock cycles, but other
than that, everything works just the same!

**Waveforms**

For this run, I dumped waveforms, so you can use `gtkwave` on this mixed Verilog/VHDL
design. 

In the screenshot below, you can see the memory bus of the RPU from the VHDL
part of the design, and the APB bus of the UART which is written in Verilog:

![Mixed Verilog/VHDL VCD Waveforms](/assets/cxxrtl/mixed_verilog_vhdl_waveforms.png)

# Limitations

I didn't run into major issue, but there are some things to be aware of.

* VHDL `assert` statements

    gHDL converts VHDL `assert` statements into RTLIL `$assert` cells. These are used by Yosys
    for formal property checking, but CXXRTL doesn't know what to do with it.

    The current work-around is to just comment out these statements (RPU doesn't have them,
    ORCA does.)

    Ideally, the `ghdl` plugin should have an option to ignore `assert` statements, or
    CXXRTL needs to find a way to deal with them. (E.g. ignore them too, or even add
    simulation-time assertion checking!)

* VHDL-specific simulation behavior is dropped

    VHDL has numerical types that abort a simulation when there is a range overflow.

    Since Yosys is ultimately a synthesis tool (in the case of CXXRTL, it synthesizes to
    C++), these kind of change are dropped. Don't use gHDL and CXXRTL to verify that
    range constraints are met during simulation!

* VHDL Records etc

    I didn't try this myself, but the `ghdl` plugin flattens complex types into a single vector.

    This can make debugging waveforms very hard!

* Case-sensitivity

    VHDL is case insensitive. Verilog is case sensitive. Yosys is case sensitive as well.

    This is something to keep in mind when you run into naming issues. (I didn't.)

# Conclusion

Mixed VHDL/Verilog can now be done with pure open source tools, and it works well!

# References

* [Domipheus Labs - TPU/RPU Series Quick Links](http://labs.domipheus.com/blog/tpu-series-quick-links/)

    A list with all the blog posts about the RPU RISC-V CPU.

* [CXXRTL, a Yosys Simulation Backend](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html) 
* [Simulation Save/Restore Checkpointing with CXXRTL](/2020/10/26/Simulation-Save-Restore-with-CXXRTL.html)

    My earlier blog posts about CXXRTL

* [gHDL Documentation](https://ghdl.readthedocs.io/en/latest/about.html)
* [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin)


