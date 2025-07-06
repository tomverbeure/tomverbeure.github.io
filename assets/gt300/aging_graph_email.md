 

Good to hear from you.  The data I have is in the attached pdf. 

The frequency was probably set a week or more before the aging test was 
started to eliminate the large warmup disturbances, although some are still 
visible in the first two months of the test.  That is a pretty normal response for a good OCXO.

Usually, people looking for highest accuracy/repeatability just leave the OCXO on all the time.  
Yes, that may diminish the lifetime of the oscillator but may not affect it that much vs many 
power-off and power-on cycles.  The heating cooling heating cooling cycles can affect mechanical 
devices like a crystal assembly.  At one time precision crystals were mounted by drilling small 
holes in the outer portion of the crystal and then running small wires from those holes to ones 
in a “holder”. I think the manufacturers have moved to simpler construction, but get similar or 
better results.

The whole crystal oscillator field is filled with black magic, experience and some theory.  
I believe they also build a bunch of units, test them and then “bin” them.  Obviously, the intent 
is to get maximum yield of maximum performance devices.  However, I think there is a good market 
for the lesser devices because the price can be set at a lower point.   

The slope of the frequency change trend line is approximately:

* Freq. shift @ 200 days   =  -0.0375 Hz
* Freq. offset at Start of test:  = -0.007 Hz
* Freq. shift over 200 days =  -0.0375 – (-0.007)  = -0.0305 Hz
* Freq. aging rate:   Delta freq / Delta time  =  -0.0305/200  = -0.0001525 Hz/Day = -1.525e-4 Hz/day
* Freq. aging rate relative to 10MHz  =   (-1.525e-4) / (10E6) = 1.525E-11
* Aging rate = 1.525E-11

If I have done my math correctly, that should be a good oscillator.  
See the comparison table in the other PDF (above)
