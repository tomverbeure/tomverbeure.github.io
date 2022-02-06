
# 3.3. timing chart
# Pixel clock: 20MHz
# H period: 40uS        -> 800 cycles
# H fp: 1.2uS           -> 24
# H sync: 3.2uS         -> 64
# H bp: 6.8uS           -> 136
# H disp start: 10uS    -> 200
# H disp time: 28.8uS   -> 576

# V total: 417
# V fp: 4
# V sync: 3
# V bp: 42
# V disp start: 45
# V disp lines: 368

# [  195.456360] [drm:ironlake_crtc_compute_clock [i915]] *ERROR* Couldn't find PLL settings for mode!

# Doesn't work: pixel clock too low.
# Minimum pixel clock: 25MHz
#xrandr -d :0 --newmode "576x368_60" 20 \
#    576 600 664 800 \
#    368 372 375 417 \
#    -VSync -HSync
#xrandr -d :0 --addmode VGA-1 "576x368_60" --verbose
#xrandr -d :0 --output VGA-1 --mode "576x368_60" --verbose
        
# Works:
#xrandr -d :0 --newmode overscan 40 \
#    1152 1200 1328 1600 \
#    368 372 375 417 \
#    -VSync -HSync
#xrandr -d :0 --addmode VGA-1 overscan --verbose

# pacman: 224x288 (~7:9 ratio) -> rotate CRC: 288x224 -> 576x244 -> 1152x368
# convert pacman_native_90deg.png -sample 1152x368! pacman_native_90deg_sample.png


# When CPU board is gone, fans are off. CRT still works.

xrandr -d :0 --newmode overscan3 80 \
    1152 1200 1328 1600 \
    736 744 750 834 \
    -VSync -HSync
xrandr -d :0 --addmode VGA-1 overscan3 --verbose
xrandr -d :0 --output VGA-1 --mode overscan3 --verbose

