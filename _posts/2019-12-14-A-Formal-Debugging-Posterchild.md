---
layout: post
title: The Case of the Fantom Packets - A Formal Debugging Posterchild
date:  2019-12-14 00:00:00 -1000
categories:
---

*Some time ago, I ran into a posterchild case of why formal verification should be
a core part of your verification strategy.*

* TOC
{:toc}

# A System that Transmits and Receives Packets

I was dealing a proprietary high-speed communication channel between 2 PCBs that transfered
packets. The packets were guarded by a 16-bit CRC. When the CRC mismatched, the packets were 
supposed to be rejected.

![System Overview]({{ "/assets/fantom_packets/FantomPackets-Overview.svg" | absolute_url }})

The encoding was pretty simple: after the usual descrambling (to maintain a zero DC level across
the transmission line), there was a start of packet symbol (SOP), an end of packet symbol (EOP)
and packet data symbols in between. Like this:

```
SOP
DATA
DATA
DATA
DATA
DATA (CRC)
DATA (CRC)
EOP
```

The number of data symbols in each packet was always the same. (Yes, that made EOP redundant,
but there were good reasons to do it this way.)

A low level packet validity checker looked at the data, calculated the CRC, and determined
the validity of the packet. In parallel with the low level validity checker, incoming packet
symbols were also sent to a number of higher level packet decoders, one for each different higher
level packet type. When a packet reached its end, the higher level decoders were supposed to
accept or reject the decoded data based on the outcome of the low level packet validity checker.

![Rx Packet Architecture]({{ "/assets/fantom_packets/FantomPackets-packet_rx_architecture.svg" | absolute_url }})

The RTL to process these packets was written years ago, hadn't been touched for a long
time, and was considered to be solid.

# Fantom Packets

However, when running this code on a new FPGA board, I noticed that every once in a while
the receiving end would signal the succesful decoding of a particular type of secondary packet *even
though the cable between transmitting and receiving PCBs was unplugged*!

Since this was part of a larger system with many layers, it took many hours of debugging to get
to this conclusion.

There was very little logic between the FPGA receiver IOs and the packet decoding logic, so I
speculated that an unplugged cable resulted in random noise being injected into the system.
The FPGA on a previous board returned zeros when there was no signal present, but the new
one returned random data instead.

With a solid theory in place, the hunt was on to find the root cause.

# Formal to the Rescue

There are different ways to solve this kind of problem.

One way is to throw randoms at the problem. But the issue happened rarely enough to doubt that 
I'd hit it fast. And even if it'd hit, I'd have to wade through a very large waveform to 
observe the failure. In case of randoms, these kind of waveform files can be gigabytes in size.

Another option is code inspection. But the original author of the code had long disappeared, and 
since the code base was relatively large, quick success wasn't guaranteed either.

So instead, I decided to try formal verification. [SymbiYosys](https://symbiyosys.readthedocs.io/en/latest/) 
is the tool of choice here. 

Rather than isolating the code where things might go wrong, I just took everything, and added simple
constraint:

```verilog
always @(posedge clk) begin
    cover(higher_level_packet_decode_valid && !low_level_packet_seen);

    if (low_level_packet_valid) begin
        low_level_packet_seen <= 1'b1;
    end

    if (!reset_) begin
        low_level_packet_seen <= 1'b0;
    end
end
```

That's really it!

Given the randomness of the input data and the relative frequency of the error case, I assumed that
the I didn't hit a case where the 16-bit CRC was matching by pure random chance, and thus that
the low level packet checker never triggered a correct packet. Yet still, the higher level decoder
triggered a successful decode.

# The Bug Root Caused

Even on the relatively large code base, it took only 30 seconds for the formal solver to trigger the cover
condition above, and the waveform of the failure was only around 60 clock cycles long.

Here's what happened:

Upon receiving EOP, the low level decoder signaled to the high level decoder a CRC match or fail, like this:

```verilog
always @(posedge clk) begin
    packet_error <= packet_eop && crc_received != crc_calculated;
end
```

Packet Accepted:

![Packet Accept Case]({{ "/assets/fantom_packets/wavedrom-packet_accept.svg" | absolute_url }})

Packet Rejected:

![Packet Reject Case]({{ "/assets/fantom_packets/wavedrom-packet_reject.svg" | absolute_url }})


The second level packet decoder used `packet_sop` to start decoding a packet, but since
the number of data symbols per packet was always the same, it did not look at `packet_eop`. Worse,
it also didn't reset the packet decoding FSM when it saw a new SOP symbol!

The sequence that triggered the error was as follows:

![Packet Fail Case]({{ "/assets/fantom_packets/wavedrom-fail_case.svg" | absolute_url }})

Since the secondary decoder didn't reset the FSM when seeing an unexpected SOP, it happily progressed
through the packet treating the second SOP as DATA. And it looked at `packet_error` being asserted
by the low level decoder to reject the packet without checking for the presence of `packet_eop`.

But the low level decoder only raised packet error when there was a CRC mismatch at the time of an EOP...
which was never there.

There were obviously multiple issues with this code:

* `packet_error` should have been asserted by default and only be deasserted during a EOP with matching CRC.
* the secondary packet decoder should have been reset upon seeing an SOP in the middle of a packet.
* the secondary packet should also have checked for the presence of an EOP before declaring a packet valid.

Fixed Case:

![Packet Fixed Case]({{ "/assets/fantom_packets/wavedrom-fixed_case.svg" | absolute_url }})

In highsight, a simulation with pure randoms would probably have triggered the whole issue pretty
quickly, but I didn't know it at the time. Meanwhile, with formal verification, this issue was
found almost immediately.

What's more, after fixing the RTL, I reran formal verification and it couldn't find another way to trigger
a false packet decode valid. And that's of course the biggest benefit of running formal verification: with
randoms, your confidence level of hitting all corner cases can be high, but it can't be 100%. And you need
hours of random simulation to get to that level of confidence.  With formal, you can be certain, often
in a much shorter time.

# Conclusion

There are a few take-aways here:

* It's impossible to conclusively prove the absense of false positives with randoms. Formal verification
  is the only way to guarantee that all corner cases have been covered.
* It's never too late to use formal verification: it isn't only useful during the verification stage of 
  a project, it can also be extremely useful to root cause a bug in an existing system.
* Formal verification can be much faster than randoms and code inspection. The testbench can be very
  short compared to a simulation testbench.


