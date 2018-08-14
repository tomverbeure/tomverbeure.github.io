---
layout: post
title:  "Moving Away from Verilog - A First Look at SpinalHDL"
date:   2018-08-11 22:00:00 -0700
categories: RTL
---

# Introduction

Electronics in general and digital design in particular is what I do. I love coming up with a new architecture for a major block. 
I love writing RTL. I love debugging my code up to the point where everything just works. 

It's what I do for a living, and it's what I want to do as a hobby (though it competes for attention with my mountain bike...)

There's only one problem: I want to write and debug code efficiently, and it's very hard to match the tools of
a professional environment at home.

# The Verboseness of Verilog

The biggest problem by far is Verilog. Especially the verbosity in the way modules need to be connected together.

We've all been [here](https://github.com/tomverbeure/panologic/blob/57d7f782f2c6061ea81fd954507cf2bba4a76c9e/bringup/rtl/soc.v#L32-L83):

```Verilog


    wire        mem_cmd_valid;
    wire        mem_cmd_ready;
    wire        mem_cmd_instr;
    wire        mem_cmd_wr;
    wire [31:0] mem_cmd_addr;
    wire [31:0] mem_cmd_wdata;
    wire [3:0]  mem_cmd_be;
    wire        mem_rsp_ready;
    wire [31:0] mem_rsp_rdata;

    wire mem_rsp_ready_gpio;
    wire [31:0] mem_rsp_rdata_gpio;

    ...

    vexriscv_wrapper cpu (
        .clk            (clk),
        .reset_         (reset_),
        .mem_cmd_valid  (mem_cmd_valid),
        .mem_cmd_ready  (mem_cmd_ready),
        .mem_cmd_wr     (mem_cmd_wr),
        .mem_cmd_instr  (mem_cmd_instr),
        .mem_cmd_addr   (mem_cmd_addr),
        .mem_cmd_wdata  (mem_cmd_wdata),
        .mem_cmd_be     (mem_cmd_be),
        .mem_rsp_ready  (mem_rsp_ready),
        .mem_rsp_rdata  (mem_rsp_rdata),
        .irq            (irq        )
    );

    ...

    gpio #(.NR_GPIOS(8)) u_gpio(
            .clk        (clk),
            .reset_     (reset_),
    
            .mem_cmd_sel    (mem_cmd_sel_gpio),
            .mem_cmd_valid  (mem_cmd_valid),
            .mem_cmd_wr     (mem_cmd_wr),
            .mem_cmd_addr   (mem_cmd_addr[11:0]),
            .mem_cmd_wdata  (mem_cmd_wdata),
    
            .mem_rsp_ready  (mem_rsp_ready_gpio),
            .mem_rsp_rdata  (mem_rsp_rdata_gpio),
    
            .gpio_oe(gpio_oe),
            .gpio_do(gpio_do),
            .gpio_di(gpio_di)
        );
```

There are ways to work around this, but all of them have disadvantages that are disqualifying. (This is
obviously very subjective!)

## Verilog-mode

One of the common recommendations is to use Emacs [verilog-mode](https://www.veripool.org/projects/verilog-mode/wiki/Examples). (You don't
need to use the Emacs *editor*. There are Vim macros to run verilog-mode in batch mode.)

Verilog mode will analyze your code and expand some magic words in strategically placed comments into signal lists.

The net result is something like this:

```Verilog
module autosense (/*AUTOARG*/
                  // Outputs
                  out, out2,
                  // Inputs
                  ina, inb, inc
                  );
   
   input        ina;
   input        inb;
   input        inc;
   output [1:0] out;
   output       out2;
   
   /*AUTOREG*/
   // Beginning of automatic regs (for this module's undeclared outputs)
   reg [1:0]    out;
   reg          out2;
   // End of automatics
```

I heard from friends in the industry that Verilog-mode is used quite a bit in professional environments, so I gave it a try.

Without making it into a separate blog post, my problem with Verilog-mode was that:

* it didn't do as much as I wanted it to do.
* what it was supposed to do, worked most of the time, but not always.
* it's visually really ugly (just look at the code above!)
* the indenting rules were inconsistent and definitely not the way I wanted it, even after spending a lot of time trying to tweak it.

Verilog-mode is tool that can save a lot of time, but ultimately, it felt like an ugly hack that rubbed me the wrong way.
Two months after trying it the first time, I gave it a second chance only to drop it soon after again. It's just not for me.

## SystemVerilog

SystemVerilog has records and interfaces and they are a fantastic way to remove a large part of the verboseness, so that's 
where I looked next.

The main issue with it is that it's just not supported very well in a hobby environment. 

The only tool that supports a decent amount of features is [Verilator](https://www.veripool.org/wiki/verilator). But 
neither [Icarus Verilog](http://iverilog.icarus.com) nor [Yosys](http://www.clifford.at/yosys/) support records or interfaces. 
And even if you're using the free (as in beer) versions of commerical tools, then you're often out of luck. 
The old [Xilinx ISE](https://www.xilinx.com/products/design-tools/ise-design-suite.html) 
(which I use for my [Pano Logic project](https://github.com/tomverbeure/panologic)) has plenty of limitations and outright bugs for
sometimes even common Verilog constructs, so SystemVerilog is completely out of the question. The same is true for 
[Lattice iCEcube2](http://www.latticesemi.com/iCEcube2): you have to use Synplify Pro for synthesis.

A minimal SystemVerilog to Verilog translator could be a solution, and at some point I started working on exactly that, but right now
it doesn't exist. 

And even SystemVerilog doesn't have features that could be really useful.

## What I Really Want

What I really want is a system where a zero fanout signal down deep in your design hierarchy automatically
ripples through all the way to upper hierachy levels until it finds a signal of the same name. One where I can use regular expressions to
rename whole clusters of signals with one line except that one signal that you don't want to rename. One where you have hundreds of plugins to write 
FSMs with all kinds of verification features enabled by default or generate a fully verified, parameterized multi-threaded FIFO-with-rewind with a 
few lines of code. Hell, I don't even want to type the name of the module at the top of the file when it can be inferred from the file name.

Such systems exist, but they're always proprietary, and maintained by well funded CAD departments.

I could write my own watered down, minimalistic version of it, but I'd be afraid of stepping on the IP of previous employers. And it'd always do
less than what it could be. I want to write RTL, not tools that will allow me to write RTL.

So Verilog and SystemVerilog with assorted hacks didn't work out. And since open source equivalents don't really exist either,
I started to look at radical alternatives: completely different RTL languages.

I experimented a bit with [MyHDL](http://myhdl.org/) and [migen](https://m-labs.hk/migen/manual/index.html#https://m-labs.hk/migen/manual/index.html#), but 
eventually I settled on [SpinalHDL](https://spinalhdl.github.io/SpinalDoc/). 

That's what I'll be writing about for the rest of this article.

# SpinalHDL

## Quick Feature Overview

At its core, SpinalHDL is a library of classes, written in Scala, that are used to describe your hardware.

The library contains everything you need to write RTL:
 
* Data types

    Basic data types such as single wires (Bool), vectors (Bits), signed and unsigned integers (UInt, SInt), and Enums. Composite types
    such a records (Bundle) and arrays (Vec).

    Support for signed and unsigned fixed point and even floating point is under development.

* Hierarchy

    Verilog modules are called Components. And each component can contain multiple Areas, which have their down scope but can
    reach out to other areas. Think of them as souped up Verilog `always` constructs.

* Higher Level of Abstraction

    Since everything is really a Scala object, Scala methods can create pretty much anything you want: Areas with logic and registers,
    full components.

    And those objects can be passed as an argument to a Component object, which makes it possible to create very powerful abstractions.

* Components Library

    In addition to the core library, SpinalHDL also has a components library: a rather large collection of basic building blocks that can be used in your design. 
    From counters to bus interfaces. From a full featured CPUs to an SDRAM controller.

    This components library is excellent, not only because it will reduce the amount of work, but also because it often uses all the tricks 
    in the SpinalHDL book. They are a fantastic way to learn about how SpinalHDL works.

There is a fairly large manual that takes you through most of the basics of the language, so there is little point in repeating all of that here.

Instead, I would like to take you through an example with trivial core functionality that also shows a hint of the greater power of SpinalHDL.

## A Not Totally Trivial Timer Example

There is nothing complex about a timer that is connected to a CPU bus.

But what if we want to make it generic? We don't want to design it for one particular bus interface standard, we want it to work with any 
standard, without having to redesign it later!

Instead of connecting to the bus with low level signals, the timer uses an API of an abstract bus factory object. And it's up to the user 
of the timer block to later provide the details of this bus standard: AXI, APB, Wishbone or whatever interface you have in mind.

When you instantiate the timer block in your design, you pass along a concrete bus factory object. 

The end result will be a timer that works with the bus that you desire, but the design of the Timer block itself is entirely generic 
and interface agnostic.

And that's one of the [examples](https://spinalhdl.github.io/SpinalDoc/spinal/examples/timer/) in the SpinalHDL manual.

The description below is for a slightly different example though, with reduce functionality. You can find the project 
[here](https://github.com/tomverbeure/SpinalTimer) on GitHub.

The [code](https://github.com/tomverbeure/SpinalTimer/blob/master/src/main/scala/mylib/Timer.scala) for the generic timer:

```Scala
package mylib

import spinal.core._
import spinal.lib._
import spinal.lib.bus.misc._

case class Timer(width : Int) extends Component{
  val io = new Bundle{
    val tick      = in Bool
    val clear     = in Bool
    val limit     = in UInt(width bits)

    val full      = out Bool
    val value     = out UInt(width bits)
  }

  val counter = Reg(UInt(width bits))
  when(io.tick && !io.full){
    counter := counter + 1
  }
  when(io.clear){
    counter := 0
  }

  io.full := counter === io.limit && io.tick
  io.value := counter

  def driveFrom(busCtrl : BusSlaveFactory,baseAddress : BigInt)(ticks : Seq[Bool], clears : Seq[Bool]) = new Area {
    // Address 0 => clear/tick masks + bus
    val ticksEnable  = busCtrl.createReadWrite(Bits(ticks.length bits),baseAddress + 0,0) init(0)
    val clearsEnable = busCtrl.createReadWrite(Bits(clears.length bits),baseAddress + 0,16) init(0)
    val busClearing  = False

    io.clear := (clearsEnable & clears.asBits).orR | busClearing
    io.tick  := (ticksEnable  & ticks.asBits ).orR

    // Address 4 => read/write limit (+ auto clear)
    busCtrl.driveAndRead(io.limit,baseAddress + 4)
    busClearing setWhen(busCtrl.isWriting(baseAddress + 4))

    // Address 8 => read timer value / write => clear timer value
    busCtrl.read(io.value,baseAddress + 8)
    busClearing setWhen(busCtrl.isWriting(baseAddress + 8))
  }

}

```

The first part is really pretty straightfoward.

```Scala
case class Timer(width : Int) extends Component{
```

The parameters of the class are similar to Verilog parameters. In this case, 
it's a simple integer, but for more complex designs, it's usually some kind of struct with many parameters. This makes
it very easy to pass parameters around and change some of them as needed. One could also create recursive hardware.

```Scala
  val io = new Bundle{
    val tick      = in Bool
    val clear     = in Bool
    val limit     = in UInt(width bits)

    val full      = out Bool
    val value     = out UInt(width bits)
  }  
```

IOs are grouped into a Bundle in which each item is specified as 'in' or 'out'. 

Bundles are a general way of grouping signals that belong together, they're not restricted to just IOs. And they
can be nested. The fact that they are assigned to an `io` value is really just
the choice of the designer, who could have chosen any other name. Or decide to have multiple Bundles for IOs.

Since a Bundle is a class, you can subclass it. For example, you could
create a Bundle subclass that's called [`Apb3`](https://github.com/SpinalHDL/SpinalHDL/blob/ad8859b669d6b6773705d675aebb7b40397b9dde/lib/src/main/scala/spinal/lib/bus/amba3/apb/APB3.scala#L49-L58https://github.com/SpinalHDL/SpinalHDL/blob/ad8859b669d6b6773705d675aebb7b40397b9dde/lib/src/main/scala/spinal/lib/bus/amba3/apb/APB3.scala#L49-L58).

The implementation of the timer is straightforward as well:

```Scala
  val counter = Reg(UInt(width bits))
  when(io.tick && !io.full){
    counter := counter + 1
  }
  when(io.clear){
    counter := 0
  }

  io.full := counter === io.limit && io.tick
  io.value := counter
```

If you don't know Scala, you won't notice that RTL constructs don't use Scala keywords, but objects and methods from the SpinalHDL library.

For example, Scala uses `if (...) <...> else <...>` like many other languages. `if` and `else` are reserved Scala keywords.

However, if you want to use such a construct in your RTL, you need to use `when(...){ <...> }.otherwise{ <...> }`, where `when` is an object of the
[`WhenContext`](https://github.com/SpinalHDL/SpinalHDL/blob/ad8859b669d6b6773705d675aebb7b40397b9dde/core/src/main/scala/spinal/core/when.scala#L73-L88) and 
`otherwise` is [method](https://github.com/SpinalHDL/SpinalHDL/blob/ad8859b669d6b6773705d675aebb7b40397b9dde/core/src/main/scala/spinal/core/when.scala#L103-L107) 
of the that `when` object. 

When you're using these RTL building constructs, SpinalHDL is building an
AST-like data structure under the hood, just like simulators and synthesis tools do when they're parsing your Verilog code.

You *can* still use if-else keywords, but those don't convert to RTL: they are evaluated during the equivalent of elaboration, if you will. They are
like `if ... generate` statements in Verilog.

Another notable aspect is that you can freely mix assignment to combinational and registered signals. Registered signals are indicated
as such by wrapping `Reg(...)` around the type of the signal.

The real interesting part starts with the `driveFrom` method.

This method doesn't add new hardware to the Timer module itself, but it returns a new Area object that references the signals of
the `io` bundle and creates some glue logic for the interface hardware. It connects this glue logic to bus registers that
are created by the bus factory object.

```Scala
  def driveFrom(busCtrl : BusSlaveFactory,baseAddress : BigInt)(ticks : Seq[Bool],clears : Seq[Bool]) = new Area {
```

`busCtrl` is an object of the `BusSlaveFactory` class. This is an abstract class that can be used to support any kind of bus that
you want. The method doesn't need to know what kind of bus it is dealing with: all it really cares about it is that there are methods available
in this class to tie itself into this bus, with some registers that has a certain base address. 

That's what happens here:

```Scala
    val ticksEnable  = busCtrl.createReadWrite(Bits(ticks.length bits),baseAddress + 0,0) init(0)
    ...
    io.tick  := (ticksEnable  & ticks.asBits ).orR
```

The timer counter increments when `io.tick` is high. Some glue logic is added to create `io.tick`: it comes from a vector of multiple ticks, where 
each bit can individually be masked.

This masking register is `tickEnable`: it's a configuration register that is a field of a bus register that starts at relative address 0, 
and that starts at bit zero within that register. The bus register is read/write.

It is the task of the `busCtrl` factory object to gather the information of all registers that are attached to the bus by calls to 
`createReadWrite`, `driveAndRead`, `read` and `write`, and, eventually, construct all the registers and wires that make up the bus fabric.

With the core Timer in place, we can now build [a Timer that uses an APB bus](https://github.com/tomverbeure/SpinalTimer/blob/master/src/main/scala/mylib/ApbTimer.scala):

```Scala
package mylib

import spinal.core._
import spinal.lib._
import spinal.lib.bus.amba3.apb._

case class ApbTimer(width : Int) extends Component{
  val io = new Bundle{
    val apb = Apb3(ApbConfig(addressWidth = 8, dataWidth = 32))
    val tick      = in Bool
    val interrupt = out Bool
  }
  
  val timer = Timer(width = 32)
  val busCtrl = Apb3SlaveFactory(io.apb)
  ...
  val timerBridge = timer.driveFrom(busCtrl,0x40)(
    // The 'True' allows for a mode where the timer increments each cycle without the need for activity on io.tick
    ticks  = List(True, io.tick),

    // By looping the timer full to the clears, it allows you to create an autoreload mode.
    clears = List(timer.io.full)
  )

  io.interrupt := timer.io.full
}

object ApbTimerVerilog {
  def main(args: Array[String]) {
    SpinalVerilog(new ApbTimer(8))
  }
}
```

Things about the bus are now concrete:

* The `ApbTimer` module has IOs that include an Apb3 bus.
* `timer` is a 32-bit wide timer.
* `busCtrl` is an `Apb3SlaveFactory` object whose task it is to gather all the requirements of the bus and eventually
  generate the hardware for the Apb bus factory.
* `timerBridge` asks `timer` to wire up its internals to the bus.
* Finally, the `full` output of `timer` is an out of the timer, to be used by some other block.

If at some later point, we want to hang the timer on a Wishbone bus, all we need to do is replace Apb3, ApbConfig, and Apb3SlaveFactory by their 
Wishbone equivalent and we're done.

## Generating Verilog

Generating Verilog is matter of calling the `SpinalVerilog` method with our ApbTimer object:

```scala
object ApbTimerVerilog {
  def main(args: Array[String]) {
    SpinalVerilog(new ApbTimer(8))
  }
}
```

Run the following command in the root directory of the project: `sbt "run-main mylib.ApbTimerVerilog"`.

If all goes well, there will now be an `ApbTimer.v` Verilog file.


## A Look at the Generated Verilog

The generated Verilog isn't exactly what you'd write up yourself, but it matches the original code pretty well:

```Verilog
module Timer (
      input   io_tick,
      input   io_clear,
      input  [31:0] io_limit,
      output  io_full,
      output [31:0] io_value,
      input   clk,
      input   reset);
  wire  _zz_1;
  reg [31:0] counter;
  assign io_full = _zz_1;
  assign _zz_1 = ((counter == io_limit) && io_tick);
  assign io_value = counter;
  always @ (posedge clk) begin
    if((io_tick && (! _zz_1)))begin
      counter <= (counter + (32'b00000000000000000000000000000001));
    end
    if(io_clear)begin
      counter <= (32'b00000000000000000000000000000000);
    end
  end

endmodule
```

There's some low hanging fruit for improvement.

This code:

```Verilog
  assign io_full = _zz_1;
  assign _zz_1 = ((counter == io_limit) && io_tick);
```

can easily be simplified to:
```Verilog
  assign io_full = ((counter == io_limit) && io_tick);
```

Similarly, I'd prefer if the tool would keep the formatting of constants similar to the way they were specified in the original source code.
Something like `32'b00000000000000000000000000000001` could be specified as `32'd1`.

I have filed an [RFE](https://github.com/SpinalHDL/SpinalHDL/issues/132) to make SpinalHDL smarter about generating redundant
intermediate signals. The author of SpinalHDL claims that an experienced user will typically not look at the Verilog code, so this isn't 
super important. I believe that's true when you're stuck with limited feature tools like GTKwave that don't have strong source
code tracing features. In that case, the Verilog code is indeed not that important. 

But professional tools like Verdi are very good at fast browsing through source code, and these additional indirections would definitely
be a nuisance. For my use of SpinalHDL as a hobbyist, I don't think it will be a big deal.

Here are some parts of the generated ApbTimer Verilog code:

```Verilog
module ApbTimer (
      input  [7:0] io_apb_PADDR,
      input  [0:0] io_apb_PSEL,
      input   io_apb_PENABLE,
      output  io_apb_PREADY,
      input   io_apb_PWRITE,
      input  [31:0] io_apb_PWDATA,
      output reg [31:0] io_apb_PRDATA,
      output  io_apb_PSLVERROR,
      input   io_tick,
      output  io_interrupt,
      input   clk,
      input   reset);
...
  Timer timer_1 (
    .io_tick(_zz_4),
    .io_clear(_zz_5),
    .io_limit(_zz_1),
    .io_full(_zz_7),
    .io_value(_zz_8),
    .clk(clk),
    .reset(reset)
  );
...
```

Yay for not having to type all those signals myself!

```Verilog
  assign io_apb_PREADY = _zz_6;
  ...
  assign _zz_6 = 1'b1;
  ...
  assign busCtrl_doWrite = (((io_apb_PSEL[0] && io_apb_PENABLE) && _zz_6) && io_apb_PWRITE);
  assign busCtrl_doRead = (((io_apb_PSEL[0] && io_apb_PENABLE) && _zz_6) && (! io_apb_PWRITE));
```

`_zz_6` is another redundant signal that is unnecesary. Whether or not it should also be optimized away from the
last 2 lines is up for debate. (Probably not?)


Finally, let's look at `_zz_1`:

```Verilog
  Timer timer_1 (
    ...
    .io_limit(_zz_1),
    ...
  );
  ...
  always @ (*) begin
      ...
      8'b01000100 : begin
        if(busCtrl_doWrite)begin
          _zz_2 = 1'b1;
        end
        io_apb_PRDATA[31 : 0] = _zz_1;
      end
      ...
    endcase
  end
  ...
  always @ (posedge clk) begin
      ...
    case(io_apb_PADDR)
      8'b01000100 : begin
        if(busCtrl_doWrite)begin
          _zz_1 <= io_apb_PWDATA[31 : 0];
        end
      end
      ...
    endcase
  end
```

The interesting part here is that `_zz_1` is a register. Having anonymous combinational signals is one thing, but anonymous
registered signals are a bigger problem: they can cause all kinds of problems when doing things like formal equivalence checks
and formal verification.

For example, if you want to put an `assert` on `io_limit`, you'd have to use `_zz_1` instead. But as your design changes, that name would
change as well. This is something that will need to be improved.

# Temporary Conclusion

I've only just started to write my first lines of SpinalHDL. It isn't perfect, but I like it so far. You can use it to write
RTL just like you would with Verilog or SystemVerilog, but it has the ability to do a lot more.

The Timer above only scratches the surface of what's possible. One of the biggest attractions is a relatively large
library of examples code,  the most impressive of which is the VexRiscv CPU: an incredibly ingenious implementation of a RISC-V CPU
with tons of configuration options through plugins.

That example takes abstractions to a whole new level, and requires a relatively deep understanding of Scala and SpinalHDL to grasp
what's going on.

In a future posts, I will try to describe how the VexRiscv makes use of some of the special features of SpinalHDL. And I'll also
report on my progress in using the language myself.




