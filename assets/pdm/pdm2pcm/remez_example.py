#! /usr/bin/env python3
from scipy import signal

Fs  = 48                # Sample rate
Fpb = 6                 # End of pass band
Fsb = 10                # Start of stop band
Apb = 0.05              # Max Pass band ripple in dB
Asb = 60                # Min stop band attenuation in dB
N   = 37                # Order of the filter (=number of taps-1)

# Remez weight calculation: https://www.dsprelated.com/showcode/209.php
err_pb = (1 - 10**(-Apb/20))/2      # /2 is not part of the article above, but makes the result consistent with pyFDA
err_sb = 10**(-Asb/20)

w_pb = 1/err_pb
w_sb = 1/err_sb
    
# Calculate that FIR coefficients
h = signal.remez(
      N+1,                      # Desired number of taps
      [0., Fpb/Fs, Fsb/Fs, .5], # Filter inflection points
      [1,0],          # Desired gain for each of the bands: 1 in the pass band, 0 in the stop band
      [w_pb, w_sb]    # weights used to get the right ripple and attenuation
    )               

print(h)

import numpy as np
from matplotlib import pyplot as plt

# Calculate 20*log10(x) without printing an error when x=0
def dB20(array):
    with np.errstate(divide='ignore'):
        return 20 * np.log10(array)

(w,H) = signal.freqz(h)

# Find pass band ripple
Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
Rpb = 1 - (Hpb_max - Hpb_min)
    
# Find stop band attenuation
Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
Rsb = Hsb_max
    
print("Pass band ripple:      %fdB" % (-dB20(Rpb)))
print("Stop band attenuation: %fdB" % -dB20(Rsb))

# Plot impulse response/filter coefficients
plt.figure(figsize=(10,5))
plt.subplot(211)
plt.title("Impulse Response")
plt.stem(h)
plt.subplot(212)
plt.title("Frequency Reponse")
plt.grid(True)
plt.plot(w/np.pi/2*Fs,dB20(np.abs(H)), "r")
plt.plot([0, Fpb], [dB20(Hpb_max), dB20(Hpb_max)], "b--", linewidth=1.0)
plt.plot([0, Fpb], [dB20(Hpb_min), dB20(Hpb_min)], "b--", linewidth=1.0)
plt.plot([Fsb, Fs/2], [dB20(Hsb_max), dB20(Hsb_max)], "b--", linewidth=1.0)
plt.xlim(0, Fs/2)
plt.ylim(-90, 3)

plt.tight_layout()
plt.savefig("remez_example_filter.svg")


