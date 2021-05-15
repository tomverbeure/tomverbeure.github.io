---
layout: post
title: USB System
date:  2021-05-14 00:00:00 -1000
categories:
---

* TOC
{:toc}


# TinyUSB

* [TinyUSB on GitHub](https://github.com/hathach/tinyusb)

* [Porting](https://github.com/hathach/tinyusb/blob/master/docs/porting.md#porting)
* [Add Your Own Board](https://github.com/hathach/tinyusb/blob/master/docs/boards.md#add-your-own-board)

# Compile FOMU code

 * [Change fomu-specific makefile](https://github.com/hathach/tinyusb/blob/2d15e1183064a35cc646a46bddf2b82915114cc8/hw/bsp/fomu/family.mk#L9) 
    to use the right RISC-V compiler:

    In my case: 

    ```diff
-CROSS_COMPILE = riscv-none-embed-
+CROSS_COMPILE = /opt/riscv64-unknown-elf-gcc-10.1.0-2020.08.2-x86_64-apple-darwin/bin/riscv64-unknown-elf-
   ```

* Compile

    From tinyusb root dir:

    ```sh
make -C examples/device/cdc_msc BOARD=fomu
    ```

    ```
AS crt0-vexriscv_asm.o
CC dcd_eptri.o
CC fomu.o
CC board.o
CC main.o
CC msc_disk.o
CC usb_descriptors.o
CC tusb.o
CC tusb_fifo.o
CC usbd.o
CC usbd_control.o
CC audio_device.o
CC cdc_device.o
CC dfu_rt_device.o
CC hid_device.o
CC midi_device.o
CC msc_device.o
CC net_device.o
CC usbtmc_device.o
CC vendor_device.o
LINK _build/fomu/fomu-cdc_msc.elf
CREATE _build/fomu/fomu-cdc_msc.bin
CREATE _build/fomu/fomu-cdc_msc.hex

   text	   data	    bss	    dec	    hex	filename
  13730	   8220	   9764	  31714	   7be2	_build/fomu/fomu-cdc_msc.elf
    ```

    Instead of compiling with `rv32i` and `lto`, use the following options
    to reduce code size:

    ```
  -flto \
  -march=rv32imc \
  -msave-restore \
  -Os \
  ```
    Result:

    ```
   text	   data	    bss	    dec	    hex	filename
  10014	   8220	   9764	  27998	   6d5e	_build/fomu/fomu-cdc_msc.elf
    ```

    Of that 27998 total bytes, 8192 are just for a buffer in `msc_disc.o`.

    For `examples/device/audio_4_channel_mmic`, the code size before changing the
    makefile is:

    ```
   text	   data	    bss	    dec	    hex	filename
  10978	     48	  10264	  21290	   532a	_build/fomu/fomu-audio_4_channel_mic.elf
    ```

* Results are in `./examples/device/cdc_msc/_build/fomu`

    ```
(base) toms-macbook-pro:fomu tom$ pwd; ll
/Users/tom/projects/tinyusb/examples/device/cdc_msc/_build/fomu
total 760
  0 drwxr-xr-x  7 tom  staff     224 May 14 14:04 .
  0 drwxr-xr-x  3 tom  staff      96 May 14 14:00 ..
 48 -rwxr-xr-x  1 tom  staff   21952 May 14 14:04 fomu-cdc_msc.bin
328 -rwxr-xr-x  1 tom  staff  164564 May 14 14:04 fomu-cdc_msc.elf
256 -rw-r--r--  1 tom  staff   88097 May 14 14:04 fomu-cdc_msc.elf.map
128 -rw-r--r--  1 tom  staff   61813 May 14 14:04 fomu-cdc_msc.hex
  0 drwxr-xr-x  5 tom  staff     160 May 14 14:00 obj
    ```

# Porting Steps

* Add register definitions and startup code that is specific to a particular MCU chip.

    Belongs in `hw/mcu/<vendor>/<chip_family`.

    This is usually an SDK, such as the official SDK or something like CMSIS.

    Fomu doesn't have and entry here. The include file with register definitions is located
    in `/hw/bsp/...` instead.

* Add board specific code

    Belongs in `hw/bsp/<your board name>`.

    Fomu code is in [`hw/bsp/fomu`](https://github.com/hathach/tinyusb/tree/master/hw/bsp/fomu):

    * [`./hw/bsp/fomu/family.mk`](https://github.com/hathach/tinyusb/blob/master/hw/bsp/fomu/family.mk)

        Sets a limited number of variables that are specific to FOMU. It also contains a custom
        rule to flash the firmware.

        Since FOMU uses the ValentyUSB core, there are a number of references to that as well.

        According to the [Build](https://github.com/hathach/tinyusb/blob/master/docs/porting.md#build)
        porting instructions, some of the stuff should be in the `board` subdirectory of the FOMU bsp,
        but since there's only 1 board anyway, it doesn't really matter.


    * [`./hw/bsp/fomu/hw/csr.h`](https://github.com/hathach/tinyusb/blob/master/hw/bsp/fomu/include/csr.h)
      has the register map.

        In additional to traditional `#define`, it also contains inline C functions to
        read and write registers.

    * [`./hw/bsp/fomu/fomu.c`](https://github.com/hathach/tinyusb/blob/master/hw/bsp/fomu/fomu.c)

        Implements the minimal set of board-specific generic API calls that are implemented
        in [`/hw/bsp/board.h`](https://github.com/hathach/tinyusb/blob/master/hw/bsp/board.h).

    * [`./hw/bsp/fomu/crt0-vexriscv.S`](https://github.com/hathach/tinyusb/blob/master/hw/bsp/fomu/crt0-vexriscv.S)

        A pretty generic crt.S file. Has support for traps, but requires the trap vector register to
        be [writable](https://github.com/hathach/tinyusb/blob/2d15e1183064a35cc646a46bddf2b82915114cc8/hw/bsp/fomu/crt0-vexriscv.S#L54).

* If you want to add support for a new USB core, you need to 
  add it to [`./src/tusb_option.h`](https://github.com/hathach/tinyusb/blob/master/src/tusb_option.h).

* [USB device driver template](https://github.com/hathach/tinyusb/blob/master/src/portable/template/dcd_template.c)


# ValentyUSB Architecture

* [Hardware source code](https://github.com/im-tomu/valentyusb/tree/master/valentyusb/usbcore)

* There are different toplevels:

    Each toplevel is well documented in the source code itself.

    * [`DummyUSB`](https://github.com/im-tomu/valentyusb/blob/master/valentyusb/usbcore/cpu/dummyusb.py)

    * [`PerEndpointFifoInterface`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/cpu/epfifo.py#L155)

        There's CPU interface bus and a FIFO per endpoint. 

    * [`TriEndpointInterface`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/cpu/eptri.py#L55)

        CPU interface with 3 FIFOs: SETUP, IN, OUT.

        Each FIFO supports 16 endpoints though.

        Since there's only 1 FIFO that is shared for all endpoints, packets for endpoints that are
        currently not being serviced by the FIFO are NAKed. 

        For example: when the device starts writing data into the IN FIFO, all IN transactions are
        NAKed until there's a write to IN_CTRL.EPNO with the endpoint number that's associated with
        the FIFO data. At that point, an IN requests for that endpoint can be serviced and ACKed, but
        all other IN requests are still NAKed.

        The same is true for OUT transfers as well: all OUT transfers are NAKed except for transactions
        where the CPU has written the endpoint number in OUT_CTRL.EPNO.

        Each endpoint also has a bit to indicate that it is stalled. When a request is made to a stalled
        endpoint, the device replies with a STALL handshake packet.

    * [`MemInterface`](https://github.com/im-tomu/valentyusb/blob/master/valentyusb/usbcore/cpu/epmem.py)

        Uses a single memory for all buffered end data.

    The ValentyUSB example uses PerEndpointFifoInterface, but fomu uses TriEndpointInterface.


* Each toplevel has an `iobuf` as first instantiation parameter

    This is an abstract class that describes the USB IO interface. On the USB core side, it
    has defined signals that describe DP, DN, and an optional pullup control.

    On the IO side, it can be anything you want: raw pins are currently implemented (as is done 
    [here](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/io.py#L13), 
    but you could also define an STUSB03E compatible output.

    There are no comments that make clear what's the core-facing signals, and the direction of those signals,
    but it's the ones [here](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/io.py#L16-L21),
    and the go straigth from the toplevel to the USBTransfer modules, [where](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/sm/transfer.py#L74-L81)
    they are connected to some internal signals.

* [`UsbTransfer`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/sm/transfer.py#L19)

    Used in each of the toplevels.

    *`UsbTransfer` has `TxPipeline` and `TxPacketSend` as submodules. But `TxPacketSend` has the same `TxPipeline`
    as submodule???*

    [Contains](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/sm/transfer.py#L23-L27): 

    * [`TxPacketSend`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/sm/send.py#L19)

        Surrounds data that must be transmitted by a header and a CRC.

    * [`TxPipeline`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/tx/pipeline.py#L16) 

        * [tx pipeline FSM](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/tx/pipeline.py#L107-L143)

            IDLE, SEND_SYNC, SEND_DATA, STUFF_LAST_BIT

        * [`TxShifter`]()

        * [`TxBitstuffer`]()
        
        * [`TxNRZIEncoder`]()

        * FIFO from 12MHz to 48MHz  -> DP/DN/OE


    * [`RxPipeline`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/rx/pipeline.py#L17)

        Full pipeline: DP/DN  -> clock recovery -> NRZI decode -> packet detection -> bitstuff removal -> serial to parallel -> 48MHz to
        12 MHz async FIFOs (2 deep) for 8-bit data and for pkt_start/pkt_end resp.

        Almost the same as what a UTMI interface would provide on RxActive/RxData.

    * [`PacketHeaderDecode`](https://github.com/im-tomu/valentyusb/blob/623cdd45b1c5b0af25c3b9050e1fa5a8065c9749/valentyusb/usbcore/sm/header.py#L16)

        This code treats the data of a token as being part of the header, so it waits for the whole token packet before declaring
        that a header has been received. For DATA and HANDSHAKE, it declares that a header as been received immediately after seeing the PID.

    * Main transfer FSM

        Implements the flow of packets within a transaction.

        * WAIT_TOKEN
        * RECV_TOKEN
        * POLL_RESPONSE
        * WAIT_DATA
        * RECV_DATA
        * SEND_DATA
        * WAIT_HAND
        * SEND_HAND
        * ERROR

    *`PacketHeaderDecode` is in `header.py`. `TxPacketSend` is in `send.py`. What not match filename with module name?*

# USB Basics

* USB has 3 levels of communication:

    * packets

        A single atomic exchange in one direction: tokens, data bursts, handshake, special

    * transactions

        A transaction is an exchange of data. Usually with 3 (for bulk transfers) or 2 (isochronous)
        packats.

        Bulk transfer: token packet, data packet, handshake packet

        ISO transfer: token packet, data packet

    * transfers

        Consist of multiple transactions.


* Low level transactions should be done in hardware (responding with ACK or NAK etc.) Otherwise there's no way
  you'd meet response time requirements etc.
* For high performance, you need an individual FIFO per endpoint.

    Best to have a single, large RAM for that.

