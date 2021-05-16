---
layout: post
title: Add a USB Interface to Your FPGA Design
date:  2021-05-11 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

# TinyFPGA-Bootloader

* [TinyFPGA-Bootloader](https://github.com/tinyfpga/TinyFPGA-Bootloader) on GitHub

    * RTL code is in the [common](https://github.com/tinyfpga/TinyFPGA-Bootloader/tree/master/common) directory.
    * Matt Venn's [Bootloader explanation](https://github.com/mattvenn/understanding-tinyfpga-bootloader)

    * Hierarchy:

    ```
tinyfpga_bootloader:
    * LED control logic
    * USB DP/DN IO ports (FS only)
    * SPI IO ports to program SPI flash
    * USB Engine:
        - usb_serial_ctrl_ep ctrl_ep_inst:
            * Control EP
            * Handles SETUP packets
            * Control transfer FSM:  IDLE, SETUP, DATA_IN, DATA_OUT, STATUS_IN, STATUS_OUT
            * ROM with all descriptors
            * Announces CDC serial device (Communication Device Class)
            * 1 configuration
            * 2 interfaces
                * CDC: interface class 0x02, Abstract Control Model (ACM) interface subclass 0x02, 1 endpoint
                * CDC-Data: interface class 0x0a , interface subclass 0x00, 2 endpoints

        - usb_spi_bridge_ep usb_spi_bridge_ep_inst:
            * Deals with programming SPI
            * 2 FSMs:
                * Command sequencer: higher level SPI flash commands
                * SPI protocol engine: low level stuff

        - usb_fe_pe usb_fs_pe_inst:
            * This handles all the generic USB stuff.

            - usb_fs_in_arb usb_fs_in_arb_inst:
                * priority arbiter with data mux. When there are multiple in_ep_req requester
                  the data of the lowest one is passed on.
                * the in_ep_req signals are coming from the serial_ctrl_ep and the spi_bridge_ep.
                  When they don't have any data to return, the usb_fs_in_pe 
                
            - usb_fs_out_arb usb_fs_out_arb_inst:
                * simply priority arbiter without data mux

            - usb_fs_in_pe usb_fs_in_pe_inst:
                * IN protocol engine that sends data to the host
                * multiple FSMs:
                    * endpoint FSM: 
                        * for-generate loop creates 1 FSM per IN endpoint.
                    * IN transfer FSM: 
                        * handles the overall packet flow: IDLE, RCVD_IN, SEND_DATA, WAIT_ACK
                        * when TOKEN is received, current_endp selects the active EP FSM

            - usb_fs_out_pe usb_fs_out_pe_inst:
                * OUT protocol engine that receives data from the host
                * Multiple FSMs:
                    * endpoint FSM: 
                        * for-generate loop creates 1 FSM per OUT endpoint.
                    * OUT transfer FSM:
                        * IDLE, RCVD_OUT, RCVD_DATA_START, RCVD_DATA_END
                        

            - usb_fs_rx usb_fs_rx_inst:
                * Low level receive protocol engine: converts incoming serial bitstream into a byte stream, tokens etc.

            - usb_fs_tx_mux usb_fs_tx_mux_inst:
                * selects between IN or OUT protocol engine to transfer data back to host

            - usb_fs_tx usb_fx_tx_inst:
                * Low level transmit protocol engine: given a byte stream, convert to serial data
                * Generate SYNC, PID, CRC, DATA, EOP
    ```

# ValentyUSB

    * [RTL](https://github.com/im-tomu/valentyusb/tree/master/valentyusb/usbcore)

