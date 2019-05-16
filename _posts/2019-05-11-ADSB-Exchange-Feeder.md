---
layout: post
title: Setting Up an ADSB-Exchange Feeder
date:   2019-05-11 10:00:00 -0700
categories:
---

* [Introduction](#introduction)
* [Tracking Local Airplanes](#tracking-local-airplanes)
* [The Hardware](#the-hardware)
* [Software Installation](#software-installation)

# Introduction

You're probably seen those websites like [flightradar24.com](https://www.flightradar24.com/37.35,-122.03/10)
that display all the airplanes on a map, provide information about flight
delays etc.

![Flightradar24]({{ "/assets/adsb/flightradar24-screenshot.png" | absolute_url }})

Have you ever wondered where their data comes from?

Most of it comes from [ADS-B](https://en.wikipedia.org/wiki/Automatic_dependent_surveillance_%E2%80%93_broadcast) 
and [MLAT](https://flightaware.com/adsb/mlat/).

ADS-B is a system whereby airplanes broadcast information about their location, altitude, speed, call sign, airplane type and
tons of other pieces of information.

This broadcast is in the open, unencrypted, and the data can be received and decoded with a trivially simple and cheap SDR setup.

Per [FAA mandate](https://www.faa.gov/nextgen/equipadsb/), almost all airplanes are required to have an ADS-B transmitter by 
Jan 1, 2020. However, commercial airliners have been outfitted with ADS-B equipment for years.

MLAT is a fallback for those planes that don't have ADS-B: they still have the traditional transponder that broadcasts identification 
and altitude data. This transponder information can also be received by the same SDR setup, and tagged with a timestamp. When this data 
is received by multiple stations, the location of the plane can still be determined through triangulation based on the time difference of 
arrival.

It's one thing to have planes transmit this data, it's another to aggregate this data for general consumption. 

Flightradar24 and others encourage euthousiasts all over the world to set up ADS-B feeders: permanent SDR receiver stations that send the
received ADS-B data to them, where the data gets sanitized and stored in a database. It's one large crowd-sourcing operation.

In addition to the map view, they provide APIs to query real-time or historical flight data, usually for per-use fee.

At least, that's the case for commerical operators. There's also a non-commerical alternative: [ADS-B Exchange](https://adsbexchange.com).
Not only does ADS-B Exchange provide an API with free access for non-commercial purposes, they also make it a point to not remove
information that commercial providers might filter away, such as certain military flights.

Just like the commerical operators, ADS-B Exchange relies on volunteers all over the world to continuously feed them with
the latest data.

# Tracking Local Airplanes

So what's a possible use of this data?

For the past 2 years, I've been keeping track of airplane traffic over my neighborhood. This kind of data
makes it possible to analyze trends (number of flights per day, shifting traffic patterns etc.)

The main screen is just a list of airplanes for a particular day:

![Airplane List]({{ "/assets/adsb/airplane_list.png" | absolute_url }})

For each airplane, you can see its trajectory overlaid on a map. Here's a plane that arrives at SFO:

![Airplane Track]({{ "/assets/adsb/airplane_track.png" | absolute_url }})

You can also plot all the airplanes of a particular day on the map. Here's a busy day of planes arriving at SJC:

![Airplane Day Map]({{ "/assets/adsb/airplane_day_map.png" | absolute_url }})

The website runs on a cheap [Linode VPS](https://linode.com) using PostgreSQL with the PostGIS spatial database extension. 

While developing this application, there were 2 ways to get the airplane data for this application:

* Stick an antenna on the roof and record the ADS-B data straight from all the planes in the neighborhood: a good
  antenna with unobstructed views can get a range of more than 100 miles!
* Use the ADS-B Exchange API

The API route is much more reliable, because it doesn't have a single point of failure. So that's the way it was implemented.

The ADS-B Exchange website is a non-profit operation that runs tons of servers to receive a continuous stream of data points
from all over the world, process it, store into a database, display data on a map, and drive the API. It is a very
costly affiar.

Since I'm using the API at a steady rate, I set up an automated monthly donation to cover a very tiny fraction of their total hosting 
costs.

But since crowd sourcing the data is such an important aspect of the whole operation, all API users are asked to set up a feeder
as well.

In the remainder of this blog post, I'll go through the steps that I had to go through to make this happen.

# The Hardware

* [Raspberry Pi 3B(+)](https://www.amazon.com/gp/product/B01LPLPBS8) - $36 

  ![Raspberry Pi 3B+]({{ "/assets/adsb/raspberry_pi.jpg" | absolute_url }})

  Most new installations are using a Raspberry Pi 3B. An earlier version works too, but this one has built-in Wifi.
  Since there's a good chance that you will mount it somewhere outside, the Wifi makes it easy to connect to your home network.

* Micro SD Card (8GB+) - $4

  ![micro SD Card]({{ "/assets/adsb/micro_sd_card.jpg" | absolute_url }})

  Your Raspberry Pi will need to run Linux. A full-featured Raspbian Linux installation will take close to 6GB of storage
  so 8GB will be the minimum capacity of the micro SD card.


* SDR USB Device - [FlightAware Pro Stick Plus](https://www.amazon.com/gp/product/B01M7REJJW) - $20

  ![FlightAware Pro Stick Plus]({{ "/assets/adsb/FlightAware_ProStick_Plus.jpg" | absolute_url }})

  An SDR (Software Defined Radio) device makes it possible acquire RF signals, sample a particular band to the digital domain, 
  and then hand it over to your CPU to decode the acquired data. You can use it to process tons of different signals, FM radio, GPS,
  ADS-B, and many more. 

  Cheap all-round SDR devices (~$20) cover a pretty large frequency range, from 500 kHz to 1.7 GHz. If you want to
  experiment with SDR, they are perfect to start with. One disadvantage of this wide range is that an uninteresting signal on 
  one frequency band may impact the quality of reception on another.

  If you have a very specific application which has a signal on a specific frequency, it's very useful to have an analog
  band pass filter between the antenna and the SDR receiver that only passes signals in the band of interest. There are
  [discrete analog filters](https://www.amazon.com/ADS-B-1090MHz-Band-pass-SMA-Filter/dp/B010GBQXK8) that do exactly that.

  ![ADSB Bandpass Filter]({{ "/assets/adsb/adsb_bandpass_filter.jpg" | absolute_url }})

  However, if you know up front that you're only interested in ADS-B, you can buy the 
  [FlightAware Pro Stick Plus](https://flightaware.com/adsb/prostick/) USB dongle: it has the same price as any other cheap 
  unfiltered RTL dongle, but it has the analog filter built in!

* [Antenna](https://www.amazon.com/gp/product/B00WZL6WPO) - $40

  You can find [tiny antennas](https://www.amazon.com/1090Mhz-Antenna-Connector-2-5dbi-Adapter/dp/B013S8B234), often with a magnet 
  in the base, that are perfectly fine for receiving nearby airplanes. These antennas can also be used for other SDR experiments.

  My goal was to have a permanent high-quality setup. You can find plenty of website that tell you how to make a decent
  antenna yourself, but for esthetic reasons and plain laziness, I choose [66cm/26" antenna by FlightAware](https://www.amazon.com/gp/product/B00WZL6WPO).
  It's pretty cheap and gets excellent reviews.
  
* [Cable](https://www.amazon.com/gp/product/B07J54LCL7) - $16

  ![Cable]({{ "/assets/adsb/cable.png" | absolute_url }})

  You need to connect your antenna to your SDR dongle!

  Different antennas and SDR dongles have different cables, so be careful.

  The FlightAware SDR dongle has a SMA F connector. The antenna has an N-type connector. So I needed an 
  [N Male to SMA Male cable](https://www.amazon.com/gp/product/B07J54LCL7).

Everything together, the full setup cost around $116. You can easily reduce by $50 by switching to the tiny antenna.

# Software Installation

The [ADS-B Exchange website](https://www.adsbexchange.com/how-to-feed/) has a page dedicated to setting up a feeder but it's
written with the assumption that the reader already knows what he or she is doing.

So I go into a little more details.

* Install Raspbian

    Raspbian is the Raspberry Pi specific Linux distribution. Using a PC or Mac with a SD card interface, Raspbian must be flashed 
    onto the micro SD card.

    * Download Raspbian from the [Raspberry Pi website](https://www.raspberrypi.org/downloads/raspbian/).
        * I selected the zip file of *Raspbian Stretch with desktop and recommended software* (1.9GB).
        * At the time, version 2019-04-08 was the most recent one.
        * Unzip after download. You will now have a .img file of ~5.4GB.
    * Download and install [Etcher](https://www.balena.io/etcher/), a tool to flash an SD card with a new disk image.
    * Use Etcher to flash the .img file to an SD card. 
        * This will erase all the existing content on the SD card!

* Configure Raspberry Pi

    The Raspbian that you just flashed contains a full featured windowed desktop. The easieast way to proceed is to configure everything
    through this desktop, so that's what I did. However, it requires an HDMI monitor, mouse, and keyboard.

    * Insert flashed SD card.
    * Connect USB keyboard and mouse.
    * Connect to monitor with HDMI cable.
    * Power up. You should see a desktop after about 1 minute.
    * Follow installation instructions on the screen to set up password, keyboard, Wifi, timezone etc.
    * When asked to update to latest software, say yet. Go get some coffee, it will take a good 10 minutes to update.
    * Eventually, your Raspberry Pi will ask to reboot. Do so.

* Enable SSH

    Right now, your Raspberry Pi is a little desktop computer, but when it's installed somewhere in your attic or on the
    side of your house, you'll have to access it through SSH. By default, SSH is not enabled.

    To enable: Click Raspberry Icon -> Preferences -> Raspberry Pi Configuration -> Interfaces -> SSH: Enable

* Install [PiAware flight tracking software](https://flightaware.com/adsb/piaware/install)

    * Open a terminal
    * <Follow steps on page until and including reboot>
* Using the scripts
    * https://www.adsbexchange.com/how-to-feed/
    * Follow instructions on the screen 
    * When everything is done, all should be working
* Checking that everything is ok
    * Go to http://www.adsbexchange.com/myip

