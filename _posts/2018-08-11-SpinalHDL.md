---
layout: post
title:  "Moving Away from Verilog - A First Look at SpinalHDL"
date:   2018-08-11 22:00:00 -0700
categories: RTL
---

# Introduction

Electronics in general and digital design is what I do. I love coming up with an new archticture for a major block. 
I love writing RTL. I love debugging my code up to the point where everything just works. It's what I do for a living
and I don't want to do anything else.

When I love it so much that I also want to do it in my spare time (though it needs to compete for attention with my
mountain bike...)

There only one problem: I also love to write and debug code efficiently, and it's very hard to match the tools of
a professional environment at home.

# The Verboseness of Verilog

The biggest problem by far is Verilog. Especially the way modules need to be connected together.

We've all been here:

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

Now there are a couple of ways to work around this, but all of them have disadvantages that are disqualifying. (This is
obviously very subjective!)

## Verilog-mode

One of the common recommendations is to use Emacs [verilog-mode](https://www.veripool.org/projects/verilog-mode/wiki/Examples).

Verilog mode will analyze your code and expand some commented magic words into signal lists.

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

I heard from friends in the industry that it's used quite a bit in professional environments, so I gave it a try.

* it didn't do as much as I wanted it to do.
* what it was supposed to do, didn't always work.
* it's visually really ugly (just look at the code above!)
* the indenting rules were inconsistent and definitely not the way I wanted it, even after spending a lot of time trying to tweak it.

verilog-mode is tool that can save a lot of time, but ultimately, it's an ugly hack that rubbed me the wrong way.
Two months after trying it the first time, I gave it a second chance only to drop it soon after again. It's just not for me.

## SystemVerilog

SystemVerilog has records and interfaces and they are a fantastic way to remove a large part of the verboseness, so that's 
where I looked next.

The main issue with it is that it's just not supported very well if you're doing this as a hobbyist.

The only tool that supports a decent amount of features is [Verilator](https://www.veripool.org/wiki/verilator). But 
neither [Icarus Verilog](http://iverilog.icarus.com) nor [Yosys](http://www.clifford.at/yosys/) support records or interfaces. 
And even if you're using the free (as in beer) versions of commerical tools, then you're often out of luck. 
The old [Xilinx ISE](https://www.xilinx.com/products/design-tools/ise-design-suite.html) 
(which I use for my [Pano Logic project](https://github.com/tomverbeure/panologic)) has plenty of limitations and outright bugs for
plenty of regular Verilog constructs, so SystemVerilog is completely out of the question. The same is true for 
[Lattice iCEcube2](http://www.latticesemi.com/iCEcube2): you have to use Synplify Pro for the synthesis part.

A minimal SystemVerilog to Verilog translator could be a solution, at some point I started working on exactly that, but right now
it doesn't exist. 

And even SystemVerilog doesn't have features that could be really useful.

## What I Really Want

What I really want is a system where a zero fanout signal down deep in your design hierarchy automatically
ripples through all the way to an upper hierachy levels until it finds a signal of the same name. One where I can use regular expressions to
rename whole clusters of signals with one line (expect that one signal that you don't want to rename). One where you have hundreds of plugins to write 
FSMs with all kinds of verification features enabled by default. One where fully verified, parameterized multi-threaded FIFO with rewind can be instantiated 
with a few lines of code. I don't even want to type the name of the module at the top of the file, because it's inferred
from the file name.

Such systems exists, but they're always proprietary, and maintained by a well funded CAD department.

And even if I could write my own watered down, minimalistic version of it, I'd be afraid of stepping on IP of previous employers.

# SpinalHDL

Since Verilog and SystemVerilog with assorted hacks didn't work out, I started to look at alternatives. I experimented a bit with
[MyHDL](http://myhdl.org/) and [migen](https://m-labs.hk/migen/manual/index.html#https://m-labs.hk/migen/manual/index.html#), but 
eventually I found [SpinalHDL](https://spinalhdl.github.io/SpinalDoc/).

SpinalHDL is a library of RTL related classes that are written in Scala.

The library contains everything you need to build construct RTL:
 
* Data types

    Basic data types such as single wires (Bool), vectors (Bits), signed and unsigned integers (UInt, SInt), and Enums. Composite types
    such a records (Bundle) and arrays (Vec).

    Support for signed and unsigned fixed point and even floating point is under development.

* Hierarchy

    Verilog modules are called Components. And each component can contain multiple Areas, which have their down scope but can
    reach out to other areas. 

* Higher Level of Abstraction

    Since everything is really a Scala object, Scala functions can create pretty much anything you want: Areas with logic and registers,
    full components.

    And those functions can be passed as an argument to a Component object, which makes it possible to create very powerful abstractions.


For example, you could create a timer block that hangs on a CPU bus. But instead of specifying a specific bus (say, AXI) with very specific signals,
you could give it a function or a abstract object that has a generic API that could apply to kind of bus.

The timer block gets its request by using this generic API.

When you instantiate the timer block in your design, you pass along a concrete bus interface: AXI or Wishbone or whatever interface you have in mind.

The end result, will be a design with that particular bus, but the design of the Timer block itself is entirely generic and interface agnostic.

And that's exactly one of the [examples](https://spinalhdl.github.io/SpinalDoc/spinal/examples/timer/) that is given in the SpinalHDL manual, but 
I'm going into a bit more detail here.

Here's the full code:

```Scala
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

  def driveFrom(busCtrl : BusSlaveFactory,baseAddress : BigInt)(ticks : Seq[Bool],clears : Seq[Bool]) = new Area {
    //Address 0 => clear/tick masks + bus
    val ticksEnable  = busCtrl.createReadWrite(Bits(ticks.length bits),baseAddress + 0,0) init(0)
    val clearsEnable = busCtrl.createReadWrite(Bits(clears.length bits),baseAddress + 0,16) init(0)
    val busClearing  = False

    io.clear := (clearsEnable & clears.asBits).orR | busClearing
    io.tick  := (ticksEnable  & ticks.asBits ).orR

    //Address 4 => read/write limit (+ auto clear)
    busCtrl.driveAndRead(io.limit,baseAddress + 4)
    busClearing setWhen(busCtrl.isWriting(baseAddress + 4))

    //Address 8 => read timer value / write => clear timer value
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
it very easy to pass parameters around, and change some of them as needed. One could also create recursive hardware.

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

Note that Bundles are a general way of grouping signals that belong together, they're not restricted to just IOs. And, of course, they
can be hierarchical, with nested Bundles and all that. That fact that they are assigned to `io` is really just
the choice of the designer, who could have chosen any other name. Or decide to have multiple Bundles for IOs.

Since a Bundle is a class, you can subclass it to make your design more abstract. For example, you could
create a Bundle subclass that's called `ApbInterface`.

The implementation it pretty straightforward.

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

One things that can't be seen above is that RTL constructs don't use Scala keywords, but objects and methods from the SpinalHDL library.

For example, Scala uses `if (...) <...> else <...>` like many other languages. `if` and `else` are reserved keywords.

However, if you want to do such a construct for your RTL, you need to use `when(...){ <...> }.otherwise{ <...> }`. `when` is an object of the
WhenContext and `otherwise` is method of the that `when` object.

You *can* still use if-else keywords, but those don't convert to RTL: they are evaluated during the equivalent of elaboration, if you will. They are
like `if ... generate` statements in Verilog.

Another interesting aspect is that you can freely mix assignement to combinational and registered signals. Registered signals are indicated
as such by wrapping `Reg(...)` around the type.

The real interesting part starts with the `driveFrom` method.

This method doesn't add new hardware to the Timer module directly, but it creates a new Area object that references the signals of
the `io` bundle, creates some glue logic for the interface hardware, registers this glue logic with a bus factory object.

```Scala
  def driveFrom(busCtrl : BusSlaveFactory,baseAddress : BigInt)(ticks : Seq[Bool],clears : Seq[Bool]) = new Area {
```

`busCtrl` is an object of the `BusSlaveFactory` class. This is an abstract class that can be used to support any kind of bus that
you want. The method doesn't need to know what kind of bus it is, all it really cares about it is that it has some methods available
to tie itself into this bus with some registers, starting at a register that is determined by `baseAddress`.

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

It is the task of the `busCtrl` factory object to gather the information of all registers that will hang off the bus by calls to 
`createReadWrite`, `driveAndRead`, `read` and `write`, and, eventually, construct all the registers and wires that make up the bus fabric.

Finally, the example goes on actually use the Timer, with a bus connect to it. The most important parts are here:

```Scala
case class ApbTimer(width : Int) extends Component{
  val io = new Bundle{
    val apb = Apb3(ApbConfig(addressWidth = 8, dataWidth = 32))
    ...
  }
  
  ...
  val timerA = Timer(width = 32)
  ...
  val busCtrl = Apb3SlaveFactory(io.apb)
  ...
  val timerABridge = timerA.driveFrom(busCtrl,0x40)(
    // The first element is True, which allows you to have a mode where the timer is always counting up.
    ticks  = List(True, prescaler.io.overflow),
    // By looping the timer full to the clears, it allows you to create an autoreload mode.
    clears = List(timerA.io.full)
  )
  
  val interruptCtrl = InterruptCtrl(4)
  val interruptCtrlBridge = interruptCtrl.driveFrom(busCtrl,0x10)
  interruptCtrl.io.inputs(0) := timerA.io.full
  ..
}
```

Things about the bus are now concrete:

* The `ApbTimer` module has IOs that include an Apb3 bus.
* `timerA` is a 32-bit wide timer.
* `busCtrl` is an `Apb3SlaveFactory` object whose task it is to gather all the requirements of the bus and eventually
  generate the hardware for the Apb bus factory.
* `timerABridge` asks `timerA` to wire up its internals to the bus.
* Finally, the `full` output of `timerA` feeds into the input of an interrupt controller

If at some later point, we want to hang the timer on a Wishbone bus, all we need to do is replace Apb3, ApbConfig, and Apb3SlaveFactory by their equivalent 
and we're done.



