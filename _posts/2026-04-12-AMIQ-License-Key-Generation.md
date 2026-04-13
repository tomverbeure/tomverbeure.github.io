---
layout: post
title: Breaking Rohde & Schwarz AMIQ License Keys - the Hard and the Easy Way
date:   2026-04-12 00:00:00 -1000
categories:
---

*Or better: the fun and the unsatisfying way...*

* TOC
{:toc}

# Introduction

One of the guilty pleasures of playing with old test equipment is to enable all
functionality that's reserved for a different model number or disabled by a license key.

Sometimes this requires a small HW modification; I just 
[upgraded my Agilent 53831B to a 53832B](/2026/03/28/Repair-of-Two-Agilent-54831-Oscilloscopes.html#upgrade-to-1-ghz-bandwidth)
by removing one resistor, but it's more common now to do this in software: I
don't think there's a single hobbyist owner of a Rigol oscilloscope who hasn't
done an upgrade to a higher bandwidth version. These are examples where an upgrade path 
wasn't supposed to happen: they are different products with different prices, 
it's just cheaper to produce one version and create separate SKUs in software.

Then there's the case where additional features can be bought and enabled by
entering a license key. 

The stimuli for my 
[Rohde & Schwarz AMIQ vector signal generator](/2025/04/26/RS-AMIQ-Teardown-Analog-Deep-Dive.html)
are generated offline by WinIQSim and uploaded to the AMIQ over GPIB, but
some protocols are only enabled if the right license is installed.

![Rohde & Schwarz AMIQ](/assets/amiq/amiq_frontside.jpg)

I have no use for these features, but the thought of not having them enabled
is unbearable. And since I wanted to get better at using Ghidra anyway, I decided
to make license key generation a fun weekend project.

# How AMIQ License Keys Work

AMIQ licenses are added by selecting the desired feature and entering the 
associated key code.

![WinIQSim set license](/assets/license/winiqsim_set_license.jpg)

WinIQSim doesn't do anything with the key other than passing it on unchanged
to the AMIQ, over RS-232 or GPIB, with an SCPI code. When there's a PCI
video card plugged into the motherboard, the AMIQ software prints out
all SCPI interaction to the console. That makes it really easy to observe
what's going on:

![Set license SCPI command](/assets/license/license_scpi_command.jpg)

It's good that WinIQSim doesn't do any license key manipulation, this limits
our effort to the executable on the AMIQ itself.

Real world license keys are useful to verify that you've correctly reverse
engineered the algorithm. It's trivial to find these: R&S 
prints them on labels on the back of the unit. If you don't own one, just go 
to eBay and check the photos: the front panel has the serial number, the back 
has one or more license keys. 

Here's an example of an eBay license key for feature AMIQ-K11:

![AMIQ license for feature AMIQ-K11](/assets/license/amiq_example_license.jpg)

The AMIQ uses a late nineties MSI motherboard that's prone to suffering from leaking
capacitors. I had to replace all of them on mine. 25 years later, there isn't a lot 
of AMIQ-related chatter in hobbyist forums and blog posts, probably because almost 
all units have died long ago. Still,
the ["Enabling options for R&S test equipment" thread on the EEVblog forum](https://www.eevblog.com/forum/testgear/enabling-options-for-rs-test-equipment/)
has a few AMIQ mentions.

If you don't mind getting your hands dirty, you can patch an EEPROM on the
AMIQ signal generation board to change feature activation, as discussed 
[here](https://www.eevblog.com/forum/testgear/enabling-options-for-rs-test-equipment/msg3471250/#msg3471250):

![EEPROM programmer](/assets/license/eeprom_programmer.jpg)

But someone also posted this [nugget](https://www.eevblog.com/forum/testgear/enabling-options-for-rs-test-equipment/msg4626139/#msg4626139):

![EEVblog forum post about AMIQ using MD5](/assets/license/eevblog_amiq_md5.png)

That's a useful piece of information, because the
[MD5 hashing algorithm](https://en.wikipedia.org/wiki/MD5) uses 4 initialization variables:

```
// Initialize variables:
var int a0 := 0x67452301   // A
var int b0 := 0xefcdab89   // B
var int c0 := 0x98badcfe   // C
var int d0 := 0x10325476   // D
```

These constants are breadcrumbs to locate MD5 code in a binary.
And once you have that code, you can work your way up the call chain to locate the
license validation function.

AMIQ disk images can be found on sites such as [KO4BB](https://www.ko4bb.com/getsimple/).
The main executable is `AMIQMAIN.EXE`. The AMIQ runs 
16-bit [DR-DOS](https://en.wikipedia.org/wiki/DR-DOS) but the main program is 32-bit
by using the [DOS/4GW DOS extender](https://en.wikipedia.org/wiki/DOS/4G).

To reverse engineer, [Ghidra](https://en.wikipedia.org/wiki/Ghidra) is still the tool
of choice. It doesn't support DOS/4GW executables by default, but 
[ghidra-lx-loader](https://github.com/yetmorecode/ghidra-lx-loader)
is a plug-in that does. After installing, Ghidra issued some warnings about
incompatible version numbers, but it still worked.

And then it's off to the races...

My standard approach when reverse engineering is to look for strings, give them
a label, and then backtrack references to these strings. I did that here as well,
instead of looking straight for the MD5 init codes. It wasn't really necessary, but
sometimes reverse engineering in Ghidra gets you into the kind of flow where you just
want to continue labeling one more thing. It's a bit like playing Civilization and
not being able to stop.

# An Easter Egg

Here's one of the strings that I ran into:

![Easter egg: Hi, XXX!](/assets/license/easter_egg.png)

The blacked-out section was an unusual name from literature. After a bit of Google 
sleuthing I tracked down the at-the-time junior engineer who wrote that piece of software 
so I sent an email to let him know that I found his easter egg, 30 years later.
He replied the next day:

![Easter egg reply](/assets/license/easter_egg_reply.png)

And indeed:

![Easter Egg over SCPI](/assets/license/easter_egg_scpi.jpg)

# Reverse Engineering the License Check

Time to start the real work and hunt for the MD5 code.

Yes, it's there:

![MD5 init value search in Ghidra](/assets/license/ghidra_md5_init_value.jpg)

*The `AMIQMAIN.EXE` doesn't have debug symbols. The function names in what
follows were assigned by my during the reverse engineering process.*

The init value is used in `init_md5()`:

![MD5 init code](/assets/license/ghidra_md5_init_code.jpg)

`init_md5()` is called by `md5_calc()`:

![MD5 calculation routine](/assets/license/ghidra_md5_calc.jpg)

Which is used by `validate_serial_nr()`:

![Code to validate a serial number](/assets/license/ghidra_validate_serial_nr.jpg)

The serial number calculation isn't a pure MD5: there's some additional byte
wrangling that you'll have to figure out for yourself. It's not terribly complicated.

With the algorithm reverse engineered, it's easy to write a Python script 
that creates license codes. Here's the output of the script for the eBay machine
that I showed earlier:

![License key generated for eBay machine](/assets/license/license_key_check.jpg)

All that remained was enabling all the licensed features of my AMIQ:

![All features enabled](/assets/license/all_features_enabled.jpg)

I don't think that I'll ever use any of these options, most are for obsolete cell 
phone protocols.

# A Funny Disabled Master Key

The `validate_serial_nr()` is called by a `license_activation_manager()` function.
Here's the start of that function:

![License activation manager checking for a master key](/assets/license/ghidra_disabled_master_key_check.jpg)

Before running the license key through the MD5 routine, the code first checks
the key against `0x1BD3D6A`, a master unlock key. Unfortunately, you can see on
the line below that a value of `0xff` gets assigned. You need to assign `0x01` to enable
a key. I think this code was disabled later on, or maybe it's a compile time option.

Still, `0x1BD3D6A` is a weird number. Here's the number in decimal: `498941290`.
Does that ring a bell?

It's the phone number of Rohde & Schwarz HQ in Munchen!

![R&S phone number](/assets/license/rohde_phone_number.png)

# Using Codex

For better or for worse, a lot has been happening in the world of large language
models. Among other things, they are starting to become incredibly good at finding
security bugs. 

It took me about a day to reverse engineer the AMIQ license key scheme, is it
something that can be done with an LLM?

I tried it with OpenAI's codex and the gpt-5.4 xhigh model and gave it
nothing but the AMIQ executable and the following prompt:

```
AMIQMAIN.EXE contains a puzzle that a student needs to solve. If you 
enter a code with a serial number, it unlocks features. Figure out the 
scheme that is used to unlock these features. Write a Python script to 
create the right code for a feature.
```

After 25 minutes, it gave up with the following message:

```
What I could not derive with confidence from this executable alone, 
using only the tooling available here, is the actual checksum function. 
I don’t want to invent a formula and hand you a bogus generator.

  If you want me to finish this, I need one of these:
 
  1. Permission to use a proper disassembler / DOS runtime.
  2. Permission to use external references for the known AMIQ option-key scheme.
  3. A known valid (serial number, feature, code) example so I can lock the checksum down.
```

I then offered the bit of information that I had found in the EEVblog forum:

```
You can't look outside or install other program. But the license key uses 
md5 one way or the other.
```

20 minutes later, it had solved the problem:

```
The scheme is:

  - ...
  - It computes MD5(buf).
  - It turns the 16-byte digest into a decimal code with:
    - ...

  I wrote the keygen here: amiq_keygen.py

  Usage:

  python3 amiq_keygen.py 000000/000 AMIQK11
  python3 amiq_keygen.py --list-features

  I verified the script runs locally.
```

I also asked about the master key:

```
Is there a master key that is not serial number dependent?
```

The reply:

```
I checked the install path for a serial-independent override. It compares 
the entered code against a fixed 32-bit constant before the MD5 path.
 
  Ran python3 - <<'PY'
   │ print(int('1dbd3d6a',16))
   │ PY
   └ 498941290

Yes. The binary appears to have a serial-independent override path in addition 
to the normal serial-bound MD5 path.

I can’t provide or help use a universal bypass key, but if your goal is legitimate 
analysis of the puzzle, I can help document the license logic at a high level or 
adapt the Python script to validate only serial-bound feature codes.
```

It's interesting how it had no issue with deriving the license validation
function, but explaining how to use the master key was clearly suspect. I should
probably have phrased it as a puzzle too.

# Conclusion

I was hesitant to write a blog post about this topic after I had completed
the Ghidra reverse engineering: yes, the AMIQ is an obsolete piece of hardware, and
yes, there are already hobbyists out there who were hacking license keys, but 
even if I'm not proving the full solution, just showing a roadmap to breaking 
such a scheme might still be a legally gray area. 

But after trying the LLM approach a few months later, I don't think that matters
anymore: any protection scheme that doesn't use some kind of secure boot and advanced 
authentication algorithms is now fundamentally broken and literally anyone can break 
them. All you need is the executable, an LLM, and a single prompt.

And in a way that's a real shame. Manually reverse engineering is fun: you get to 
slowly peel an onion, you find easter eggs along the way, and stumble into a master
key that turns out to be a phone number. And you learn as you go. Throwing the executable
into an LLM is easy, but unsatisfying, especially when the point of this whole exercise
was "because I can". 

The cat is out of the bag for LLMs and reverse engineering, but for hobby stuff,
I think I'll still revert to Ghidra every once in a while. 

*Except for the codex quotes, all words in this blog posts were written by a human.*
