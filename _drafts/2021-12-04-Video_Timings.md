---
layout: post
title: Video Timings
date:  2021-12-04 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

* What are video timings
* History of video timings
    * NTSC: march 1941 following 1936 recommendation by RMA.
    * SECAM: patented 1956
    * PAL video timing specification: patented 1962, first broadcast 1967

        * https://en.wikipedia.org/wiki/PAL
        * http://martin.hinner.info/vga/pal.html

    * VESA standards history: http://www1.ecs.uni-ruse.bg/kp/less/dispalys/VD-site/vesa/ve00005.html

        * August 1989 VESA Mode 6AH Graphics Standard: Defines consistent initialization numbers for 
          800 x 600, 16-color Super VGA, which allows programs to set this graphics mode on all Super VGA boards.

        * November 1990 VESA Monitor Timing Manufacturing Guideline for 1024 x 768 with 60Hz Refresh Rate: 
          VG901101: Documents the most common timing parameters in current monitor and board products running 
          1024 x 768 Super VGA at 60Hz. All products manufactured to VESA's 1024 x 768 / 60Hz guideline work together.

        * Earliest timings in the DMT standard are 800x600@56 and 60Hz: 8/6/90. (document VG900601 and VG900602)

        * DMT standard milestones in spec don't really match the one on the old website...

    * GTF: Generalized Timing Formula: 1996

        * https://glenwing.github.io/docs/VESA-GTF-1.1.pdf
        * DMT spec: "The GTF method works well on paper since it relies on being able to create a pixel frequency of 
           infinite resolution. This, however, is not practical for real world applications where clock generators 
           have a finite resolution."
        * GTF designed for CRT, with high blank times -> high pixel rates. Wasted BW, higher-than-needed clock rates.
        * "VESA recommends that the fixed reference frequency (i.e. typically the fixed crystal reference used by the video 
           phase locked oscillator for subsequent programmable pixel clock synthesis) be one selected from the N x 2.25MHz 
           family of rates."

           Apparently a multiple 2.25MHz is used by legacy timings .

        * Secondary GTF: smaller h blank timings.

        * sync polarity determines primary or secondary GTF timing.

        * "Choice of sync pulse polarity is important because this aids the monitor in identifying which particular 
           mode is being displayed, and therefore how to set the parameters controlling the displayed image size and 
           position, etc. While all combinations of polarities exist in use, some polarity combinations are used more 
           than others; for instance, VESA DMTs typically use positive going sync signals."

        * Trailing edge of h-sync always in the center of hblank.

        * monitor uses horizontal and vertical scan ranges in EDID to communicate limits.

        * Q: There are many standard timing formats, including those created by VESA. Will GTF replace these?
          A: Standard timings, such as the standard VGA 60Hz timing, will continue to exist and be used, but may 
          eventually be replaced by GTF versions. VESA will still maintain its existing Display Monitor Timings (DMT) 
          and may even produce new discrete timings in the future that do not comply with the GTF method.

        * Q: How does the monitor avoid confusion between the 350-line VGA mode and a secondary GTF timing?
          A: The monitor knows that all timing modes with a horizontal frequency below the “Second GTF start 
          frequency” shall be treated as legacy timings. The Second GTF start frequency shall always be set to a 
          value higher than the horizontal frequency used for any supported legacy timings that have horizontal 
          positive and vertical negative sync polarities.

    * DMT: Display Monitor Timing Standard.

        * just a list of fixed timings. That's it.
        * when a DMT timing exists, Nvidia will typically select it over the GTF timing.
          https://www.nvidia.com/content/Control-Panel-Help/vLatest/en-us/mergedProjects/nvdsp/To_change_the_timing_formula_for_your_HDTV.htm
        * first version (Release 0.0): 1994
        * March 1996 The Discrete Monitor Timings (DMT) Standard 1.0: This standard presents a set of timing 
          standards for display monitors and covers resolutions all the way from 640 x 350 up to 1280 x 1024 and 
          from 60 Hz up to 85 Hz.
        * 2-byte code (std timing), 3-byte code (CVT). See E-EDID standard on how to derive.

    * CVT
        * VESA standard since March 2003.
        * Older generations: timing and formats done by hand and lagged industry needs.
        * CVT: method of creating timings so that new timings can be created simply and easily.
        * Long term goal: CVT replaces DMT

    * CEA-861
        * Focus on consumer electronics devices, DTV
        * Spec refers to CVT and GTF but not DMT



# Footnote

Blah Blah[^1]

[^1]: This is a footnote...


