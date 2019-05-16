---
layout: post
title: Setting Up an ADSB-Exchange Feeder
date:   2019-05-11 10:00:00 -0700
categories:
---

* [Introduction](#Introduction)

# Introduction

You're probably seen those websites like [flightradar24.com](https://www.flightradar24.com/37.35,-122.03/10)
that display all the airplanes on a map, provide information about flight
delays etc.

![Flightradar24]({{ "/assets/adsb/flightradar24-screenshot.png" | absolute_url }})

Have you ever wondered where their data comes from?

Most of it comes from [ADS-B](https://en.wikipedia.org/wiki/Automatic_dependent_surveillance_%E2%80%93_broadcast): a system
whereby (almost) each airplane in the sky broadcasts information about its location, altitude, speed, call sign, airplane type and
tons of other pieces of information.

The cool thing is that this is all broadcast in the open, unencrypted, and the data can be received and decoded with a
trivially simple and cheap SDR setup.

It's one thing to have planes transmit this data, it's another to aggregate this data for general consumption. 

Flightradar24 and others encourage people all over the world to set up ADS-B feeders: permanent SDR receiver stations that send the
received ADS-B data to them, where the data gets sanitized and stored in a database. It's basically all crowd sourced.

In addition to the map view, they provide APIs to query real-time or historical flight data, usually for per-use fee.

At least, that's the case for commerical operators. There's also a non-commerical alternative: [ADS-B Exchange](https://adsbexchange.com).
Not only do they provide an API with free access for non-commercial purposes, they also make it a point to not remove
information that commercial providers might filter away, such as certain military flights.

Just like the commerical operators, ADS-B Exchange relies on volunteers all over the world to continuously feed them with
the latest data.

# Tracking Local Airplanes

For the past 2 years, I've been keeping track of airplane traffic over our neighborhood. This kind of data
makes it possible to analyze trends (number of flight per day, shifting traffic patterns etc.)

The make screen is just a list of airplanes for a particular day:

![Airplane List]({{ "/assets/adsb/airplane_list.png" | absolute_url }})

For each airplane, you can see its trajectory. Here's a plane that arrives at SFO:

![Airplane Track]({{ "/assets/adsb/airplane_track.png" | absolute_url }})

You can also plot all the airplanes of a particular day on the map. Here's a busy day of planes arriving at SJC:

![Airplane Day Map]({{ "/assets/adsb/airplane_day_map.png" | absolute_url }})

The website runs on a cheap [Linode VPS](https://linode.com) using PostgreSQL with the PostGIS extension. 

Having never written SQL more complex than simple SELECT statements, one of the fun parts was learning how to write 
a single query that could find all the planes for a particular day which at some point of their trajectory were within 
a certain distance of our neighborhood.

I have no doubt that there must be much better ways than the way I did it, but the code actually seems to work:

```SQL
SELECT closest_point_query.plane_track_id AS plane_track_id,
    ST_Distance(closest_point_query.closest_point, ST_SetSRID(ST_MakePoint(#{lon}, #{lat}),4326), TRUE)/1000 AS distance,
    ST_Z(closest_point_query.closest_point) AS altitude,
    ST_M(closest_point_query.closest_point) AS time,
    ST_M(closest_point_query.closest_point_with_speed) AS speed,
    ST_AsText(closest_point_query.closest_point) AS closest_point

FROM (
    -- Find closest interpolated point on the track
    SELECT create_line_query.plane_track_id,
        (ST_LineInterpolatePoint(
            create_line_query.line_with_time,
            ST_LineLocatePoint(create_line_query.line_with_time, ST_SetSRID(ST_MakePoint(#{lon}, #{lat}),4326))
        )) AS closest_point,
        (ST_LineInterpolatePoint(
            create_line_query.line_with_speed,
            ST_LineLocatePoint(create_line_query.line_with_time, ST_SetSRID(ST_MakePoint(#{lon}, #{lat}),4326))
        )) AS closest_point_with_speed
    FROM (
        -- Convert points of a track into a line string, one that include time as M nd another one that include speed as M
        SELECT ptp.plane_track_id,
        (ST_MakeLine(
            ST_SetSRID(
            ST_MakePoint(
                ST_X(ST_AsText(ptp.coordinate)),
                ST_Y(ST_AsText(ptp.coordinate)),
                ST_Z(ST_AsText(ptp.coordinate)),
                EXTRACT(EPOCH FROM time)),4326
            ) ORDER BY time
        )) AS line_with_time,
        (ST_MakeLine(
            ST_SetSRID(
            ST_MakePoint(
                ST_X(ST_AsText(ptp.coordinate)),
                ST_Y(ST_AsText(ptp.coordinate)),
                ST_Z(ST_AsText(ptp.coordinate)),
                ptp.speed),4326
            ) ORDER BY time
        )) AS line_with_speed
        FROM plane_track_points AS ptp INNER JOIN plane_tracks AS pt ON (ptp.plane_track_id = pt.id)
        WHERE pt.created_at < '#{end_time_str}' AND pt.last_pos_time >= '#{start_time_str}'
        GROUP BY ptp.plane_track_id
    ) AS create_line_query
) AS closest_point_query
WHERE     ST_Z(closest_point_query.closest_point) < #{altitude} 
      AND ST_Z(closest_point_query.closest_point) > 500
      AND ST_Distance(closest_point_query.closest_point, ST_SetSRID(ST_MakePoint(#{lon}, #{lat}),4326), TRUE)/1000 < #{distance}
ORDER by time
```

There were 2 ways to get the airplane data for this application:

* Stick an antenna on the roof and record the ADS-B data straight from all the planes in the neighborhood: a good
  antenna with unobstructed views can get a range of more than 100 miles!
* Use the ADS-B Exchange API

The API route is much more reliable, because it doesn't have a single point of failure. So that's the way it was implemented.

Keeping the ADS-B Exchange website and API up and running is a very costly affair, so we set up an automated monthly donation to
cover a (very tiny) fraction of their total hosting costs.

But since crowd sourcing the data is such an important aspect of the whole operation, all API users are asked to set up a feeder
as well.

In the remainder of this blog post, I'll go through the steps that I had to go through to make this happen.

# The Hardware

* Raspberry Pi 3B.
  Almost all installations are using a Raspberry Pi 3B. This is not really necessary, but it has built-in Wifi
  and since there's a good chance that you will mount everything somewhere outside, that makes it easy to connect
  to your home network.
* SDR USB Device
  An SDR (Software Defined Radio) device makes it possible acquire RF signals, sample them to the digital domain, and then
  hand it over to your CPU to decode the acquired data. You can use it to process tons of different signals, FM radio, GPS,
  ADS-B, and many more. Cheap SDR devices (~$20) cover a pretty large freqency range, from 500 kHz to 1.7 GHz. If you want to
  experiment with SDR, this is perfect to start with.
  One disadvantage of this wide range is that an uninteresting signal on one frequency band may impact the quality of reception
  on another.
  If you have a very specific application which has a signal on a specific frequency, it's very useful to place an analog
  band pass filter between the antenna and the SDR device that only passes signals in the band of interest.
  Since I'm only interested in ADS-B, I bought the [FlightAware Pro Stick Plus](https://www.amazon.com/gp/product/B01M7REJJW):
  it's the same price as any other cheap RTL dongle, but it has a built-in analog filter which greatly improved the ADS-B
  performance!
* Antenna
  




* Buy a Raspberry Pi
* Install Raspbian
    * Download Raspbian here: https://www.raspberrypi.org/downloads/raspbian/
        * I uses Raspbian Stretch with desktop and recommended software (1.9GB)
        * I downloaded verions 2019-04-08, which was the latest at that time.
        * Unzip after download. You will now have a .img file of ~5.4GB.
    * Download and Install Etcher to flash your SDCard (https://www.balena.io/etcher/)
    * Use Etcher to flash the .img file to an SDCard. 
        * This will erase all the existing content!
        * On my MacBook with a very fast Class 10 micro SD Card, this took about 3min for programming and validation. (10min on a much slower
          SD Card.) If running PiAware is all you'll ever do on this Raspberry Pi, there's little need for a fast SD card...
* Configure Raspberry Pi
    * Insert flashed SDCard
    * Connect USB keyboard and mouse
    * Connect to monitor with HDMI cable
    * Power up, follow instructions on the screen to set up, update latest software etc.
        * Installing the latest updated and languages can take quite a bit of time!
    * Eventually, your Raspberry Pi will ask to reboot.
    * Enable SSH
        * Raspberry Icon -> Preferences -> Raspberry Pi Configuration -> Interfaces -> SSH: Enable
        * Enable SSH without a screen: https://howchoo.com/g/ote0ywmzywj/how-to-enable-ssh-on-raspbian-without-a-screen
* Install PiAware flight tracking software (https://flightaware.com/adsb/piaware/install)
    * Open a terminal
    * <Follow steps on page until and including reboot>
* Using the scripts
    * https://www.adsbexchange.com/how-to-feed/
    * Follow instructions on the screen 
    * When everything is done, all should be working
* Checking that everything is ok
    * Go to http://www.adsbexchange.com/myip

