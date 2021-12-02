---
layout: post
title: SpinalHDL I2C Controller
date:  2021-10-17 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

An APB connected version of the I2C controller,  found [here](https://github.com/SpinalHDL/SpinalHDL/blob/d40b8d339ab3ae29a6c403ba75a08d3d9fb6550b/lib/src/main/scala/spinal/lib/com/i2c/Apb3I2cCtrl.scala#L38-L57),
looks like this:

```scala
case class Apb3I2cCtrl(generics : I2cSlaveMemoryMappedGenerics) extends Component{
  val io = new Bundle{
    val apb =  slave(Apb3(Apb3I2cCtrl.getApb3Config))
    val i2c = master(I2c())
    val interrupt = out Bool()
  }

  val i2cCtrl = new I2cSlave(generics.ctrlGenerics)

  val busCtrl = Apb3SlaveFactory(io.apb)
  val bridge = i2cCtrl.io.driveFrom(busCtrl,0)(generics)

  //Phy
  io.i2c.scl.write := RegNext(bridge.i2cBuffer.scl.write) init(True)
  io.i2c.sda.write := RegNext(bridge.i2cBuffer.sda.write) init(True)
  bridge.i2cBuffer.scl.read := io.i2c.scl.read
  bridge.i2cBuffer.sda.read := io.i2c.sda.read

  io.interrupt := bridge.interruptCtrl.interrupt
}
```

Let's go over that one by one. 

It has the expected toplevel IO bundles.

* APB interface

    ```scala
    val apb =  slave(Apb3(Apb3I2cCtrl.getApb3Config))
	```

* the [I2C pins](https://github.com/SpinalHDL/SpinalHDL/blob/d40b8d339ab3ae29a6c403ba75a08d3d9fb6550b/lib/src/main/scala/spinal/lib/com/i2c/Misc.scala#L37-L51) themselves.

    ```scala
    val i2c = master(I2c())
	```

* an interrupt output

    ```scala
    val interrupt = out Bool()
	```

There's a submodule with the unfortunate name of `i2cCtrl`, because it's actually an instance of 
[`I2cCtrl`](https://github.com/SpinalHDL/SpinalHDL/blob/d40b8d339ab3ae29a6c403ba75a08d3d9fb6550b/lib/src/main/scala/spinal/lib/com/i2c/I2CSlave.scala#L148).

```scala
  val i2cCtrl = new I2cSlave(generics.ctrlGenerics)
```

In standard I2C terminology, an I2C bus has masters and slaves, and when a chip or FPGA supports both, it has different designs and instances for each
type. So when you see `I2cSlave`, you'd expect that to be, well, an I2C slave design. That's not the case!

The I2cSlave component of the SpinalHDL I2C controller contains a piece of logic that's common between a traditional I2C slave and
I2C master. 

* It keeps track of the overall state of an I2C transaction: NONE/START/DRIVE data/READ data/STOP/DROP.
* It samples the value of the SDA at the rising edge of SCL.
* When asked to, it drives a new value on SDA after a falling edge of SCL.
* It stretches SCL when it needs to drive an new SDA value, but no data is available.

, and feeds back that state to a higher level entity via
a command/respond bus. The command part of the bus 



