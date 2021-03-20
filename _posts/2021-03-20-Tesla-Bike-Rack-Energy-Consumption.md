---
layout: post
title: Tesla Model Y Energy Consumption With and Without Bikes on Rack
date:  2021-03-20 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I recently celebrated my 50th birthday. My old car was getting, well old, so decided that after a lifetime of 
second hand cars, now was as a good time as any to get myself the most stereotypical of Silicon Valley toys: a Tesla.

It's a long-range Model Y: rated at a maximum ~320mi per charge, it should be good enough for a one-way trip 
to Tahoe, with plenty of cargo space for luggage and bike accessories.

Since I don't (yet) want to soil the inside of the car with mountain biking dirt, I ordered it with a tow hitch
pre-installed, and I bought a Kuat Sherpa 2.0 bike rack. 

# The Kuat Sherpa 2.0 Hitch Rack

At 35 pounds, the Sherpa is one of the lighter bike racks out there. Compared to most other bike racks,
it looks very good.

![No bikes on the bike rack](/assets/tesla/no_bikes_pictures.jpg)

The rack is easy to operate, and can carry 2 bikes. On the negative side, it can't be extended to 3 or 4 bikes, 
and the weight per bike is limited to 40 lbs only.

My daily rider is a 27 lbs Santa Cruz Chameleon C with 29" wheels, and my backup bike is an old 34 lbs Santa 
Cruz Blur LT, so the 40 lbs limit is currently not an issue, but if I ever "upgrade" to an electric bike (old 
age, you know), chances are that I'll probaby have to change the rack as well.

![Two bikes on the bike rack](/assets/tesla/with_bike_picture.jpg)

The Chameleon has a pretty long wheel base, and I was a bit concerned about it not quite fitting onto
the rack. The real wheel goes a little bit past the length of the rack, but with the tie-down strap,
it's all good.

# Energy Consumption Test 

I wanted to get an idea about the energy consumption impact of having bikes mounted on the rack.  Since I rarely remove 
the rack from my car, my baseline is having the rack mounted without bikes.

On a sunny Saturday morning, I decided to 2 identical drives, one with and one without bikes, and compare
the results.

![Map with Test Route](/assets/tesla/test_route.png)

Here are the parameters:

* 21.8 miles total
* 2.5 mi suburban traffic, 19.3 mi highway traffic
* obey the legal speed limit

    In practice, that's 65mph for 88% of the ride, and a mix of 25mph and 40mph
    for all the rest.

* use cruise control to maintain the speed, to ensure consistency in the way the 
  accelerator is operated
* no use of auto-pilot 
* AC and heating disabled
* driving style set to standard, not chill.
* outside conditions: 57F (14C), light wind
* 2 drives were done back-to-back to ensure as similar conditions as possible

I wanted to avoid being stuck behind cars in front of me since that would lower wind resistance and make
results less comparable between the 2 drives. By obeying the speed limit, I counted on other traffic
to always be faster than me, and that was indeed the case. 

# Results

The Tesla dashboard has an option to display the instantaneous energy consumption per mile over the last 30 miles. 
There's no easy way to export this data, so I simply took a picture after the 2 rides, and used my
limited Pixelmator skills to align and overlay the 2 graphs.

The results speak for themselves:

![Energy Consumption Graphs with and withou bikes](/assets/tesla/graph_overlay.png)

Despite all my efforts to make the conditions as close as possible betweent the two drives, there
was a short slowdown on the second drive. Other than that, the form of the graphs are very similar,
except for the offset between the 2. 

The Tesla keeps track of the average consumption per mile over a whole trip:

Without bikes: 267 Wh/mi

![Trip statistics without bikes](/assets/tesla/no_bikes_end_stats.jpg)

With bikes: 311 Wh/mi

![Trip statistics with bikes](/assets/tesla/with_bikes_end_stats.jpg)

**On average, the consumption with bikes was 18% larger than without.**

The Model Y Long-Range has a 75kWh battery, good for a range difference of 280 mi vs 241 mi
in these test circumstances.

In reality, the range will be quite a bit lower. For example, the weekend traffic to Tahoe has
a lot of stop-and-go traffic, and speeds may be a little bit higher too. And there'll be
road won't be nearly as flat on the way to the mountains!

The bikes weigh around 60 pounds combined. For a comparision that only tests the impact
of using a bike rack, I'd have do a test run with the bike loaded into the trunk, but 
this was a test to check the practical impact of hitting the road with bikes mounted.
Furthermore, the car has an empthy weight of 4416 lbs. The bikes only add around 1.5%
of extra weight.


