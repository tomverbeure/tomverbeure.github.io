---
layout: post
title:  "In the lab: Bauch and Lomb StereoZoom 4 with Phone Adapter"
date:   2018-04-29 22:00:00 -0700
categories: tools
---

# The Microscope

In an [earlier log](https://hackaday.io/project/122480-eecolor-color3/log/144836-sii9233-and-sii9136-i2c-traces), 
I already wrote about needing a microscope to solder probe wires onto the pins of a TQFP 144 package.

The microscope in question is a Bauch and Lomb StereoZoom 4. There's a really good article about this microscope
[here](http://www.covingtoninnovations.com/stereozoom/), but the gist of it is this:

* It was produced from 1959 to 2000(!) and sold under the brands of Bauch & Lomb, Leica, and Cambridge Instruments.
* By far the most common configuration has a zoom ratio of the main body from 0.7x to 3.0x, with 10x eye pieces.
* It's a stereo-microscope which means there is a sense of depth. This helps a bit when doing soldering work.

The article linked earlier goes in quite a bit of detail on how to calibrate and align the eyepieces etc. This was
not necessary with the one that I bought. All I had to do was make some minor adjustments for my left eye.

An original manual can be found [here](http://www.science-info.net/docs/leitz/Leica_Stereozoom_Series_Microscopes.pdf).

# The Stand

There are two kind of stands:

* Boom stands, which have a heavy base, a vertical bar and a horizontal bar. That's the kind that I have, and the one
  that I would suggest other to get as well. They make it much easier to mount larger PCBs on a flat surface and you can 
  simply move around the base. 
* "Regular" stand, like the ones used in biology labs etc. 

![Stand]({{ "/assets/microscope/microscope_on_bench.jpg" | absolute_url }})

# Eye Pieces

The most common configuration comes with 10x eye pieces. With the main body magnification going from 0.7x to 3.0x, that gives
a total magnification from 7x to 30x.

My scope came with 15x ehye pieces instead. I don't think it makes a huge difference. When soldering, I also keep the 
scope set at the lowest magification: 0.7x.

# Where to Buy It?

eBay or Craigslist!

As I write this, there are tons of them available on eBay. 

They are offered with a boom stand, regular stand, or no stand at all: just the body, in which case you need to buy one
separately (or improvise and make your own?)

Prices are absolutely all over the place.

Having followed a bunch of auctions on eBay, it's clear now that I got mine for an absolute steal: $95. Similar configurations
sometimes go for $200 and more: $550, even $800. (For these kind of prices, you should be able to find much better
soldering microscopes, such as old models from Vision Engineering.)

Boom stands go for $50 to hundreds of dollars on eBay.

# LED Ring Illuminator

You don't strictly need an illuminator: a lamp on the side will work fine. In fact, when using the phone adaptor, I found that I
got best results with the illuminator switched off: the LED light would refect off the metal of the pins and the phone couldn't
really deal with that. However, when not using the phone, it is simply so much easier to get exactly the right amount of light and
change the intensity as needed.

At the bottom of the main body is a recessed ring in which you can screw an illuminator adaptor (or additonal lenses as well.) This
ring has a diameter of 1.5" or 38mm. Most illuminator rings that I could find on Amazon where from AmScope which expects a recessed
right of 48mm.

However, you can find an AmScope to StereoZoom ring adaptors that will convert from 38mm to 48mm ... for $35 and up.

I ended up buying a $25 
[64 LED AmScope ring illuminator](https://www.amazon.com/gp/product/B00FC7O1DS/ref=oh_aui_detailpage_o06_s00?ie=UTF8&psc=1) 
and I use painter's tape to attach it to the microscope. It's ugly, but it works.

![LED Illuminator]({{ "/assets/microscope/led_illuminator_ring.jpg" | absolute_url }})

# Mobile Phone Adapter

I wanted a mobile phone adapter for two reasons: 

* to be able to work with the microscope without looking through the eye pieces. I need to wear glasses when I do soldering work
  and not looking through the scope. Having to switch all the time between putting them on to look at a data sheet or so, and
  putting them off when doing the actual work is a bit annoying.
* to take pictures of what I'm doing and post it on a blog. :-)

There are two main options: [some holders](https://www.amazon.com/gp/product/B077D8QHQX/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1)
simply make it possible to hold the phone in front of the existing eye piece. 
[Other models](https://www.amazon.com/gp/product/B07412S738/ref=oh_aui_detailpage_o00_s00?ie=UTF8&psc=1) 
have an eye piece themselves.

I bought both to compare them. The ones with eye piece cost about double ($22 vs $12). 

Here's the one with the eye piece:

![Phone Adapter with Eye Piece]({{ "/assets/microscope/phone_adapter_1.jpg" | absolute_url }})

With an iPhone 8 Plus:

![Phone Adapter with Phone]({{ "/assets/microscope/phone_adapter_2.jpg" | absolute_url }})

Mounted on the microscope:

![Phone Adapter on Microscope]({{ "/assets/microscope/phone_mounted_on_microscope.jpg" | absolute_url }})

In terms of usage, there's simply no contest. The one without the eye piece was a pain to align against the eye piece of the
microscope, and there were major issue with glare from stray light. 

There are no such issues with the eye piece integrated model. It's pretty easy to put the phone in the holder in seconds
and have it in the right position.

The resulting pictures and videos are pretty good too!

![image_0.7x_2x]({{ "/assets/microscope/image_0.7x_2x.jpg" | absolute_url }})

In terms of settings, I typically set the microscope to 0.7x magnification, with the iPhone camera set to 2x.

If I set the iPhone to just 1x, you get a large black unused area. Like this:

![image_0.7x_1x]({{ "/assets/microscope/image_0.7x_1x.jpg" | absolute_url }})

It's totally possible to set the microscope to 3x, but in that case you lose a lot of depth of view: you can 
focus on the bottom of a TQFP144 pin and have the top of the pin unsharp or vice versa. As can be seen here:

![image_3.0x_2x]({{ "/assets/microscope/image_3.0x_2x.jpg" | absolute_url }})

Nothing prevent you from making videos, such as this one from a previous post:

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/267073327" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

I'm not an animal who makes videos in portrait mode, but portrait mode is the natural position of the holder when inserted into the
microscope. So more painter's tape was required to keep the phone in landscape orientation.


