
# Inside an OCXO 

The crystal oscillator inside an OCXO isn't perfect, so your typical OCXO comes
with a way to tune the output frequency to the perfect value, or to use the OCXO
as an element in PLL.  The tuning range is usually quite narrow. I don't have the 
specification of the Vectron 318Y0839 that's used in the GT300, but the famous 
HP 10811A/B has a 
[service manual](http://hparchive.com/Manuals/HP-10811AB-Manual.pdf)
with full schematics (and much more!), so let's use that for the discussion here.

The 10811A has an output frequency of 10MHz and an electrical tuning range of &plusmn;1Hz, 
or a relative range of just of 10<sup>-7</sup>.
Most OCXOs have only 1 way to control the output frequency by applying a voltage
on their frequency adjust input. The 10811A has two options:
through its EFC, electronic frequency adjust, input, or by changing the value of a 
trimmable capacitor. The trimmable capacitor is used for coarse tuning and
 can change the output frequency by &plusmn;20Hz.

Both tuning methods are highlighted in the schematic below:

[![HP 10811A OCXO schematic](/assets/gt300/hp10811_schematic.png)](/assets/gt300/hp10811_schematic.png)
*(Click to enlarge)*

The trim capacitor is circled in green. The EFC circuit is marked in red.

Fundamentally, the EFC circuit and the trim capacitor achieve their goal
the same way: they change the resonance frequency of a Colpitts oscillator by adjusting 
the capacitance of the oscillation loop. 

In the case of EFC, the variable capacitance is a 
[varicap diode](https://en.wikipedia.org/wiki/Varicap), a diode with a capacitance
that depends on the reverse bias voltage. Check out section 8-13 and 8-20
of the service manual for an in-depth explanation of the oscillator theory
of operation.

For the 10811A, the EFC input accepts a voltage from -5V to 5V. If you want to
control the OCXO with a relative precision of, say, 10<sup>-10</sup>, and the 
EFC input has a 10<sup>-7</sup> frequency range, then you need to be
able to control the EFC voltage with a 4 digit accuracy, which requires 
a pretty stable voltage reference. The exact output voltage doesn't matter too
much, you'll need to calibrate the thing anyway, but the stability over
temperature and power supply, and the noise is imporant.

TODO

