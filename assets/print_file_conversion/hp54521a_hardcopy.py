#! /usr/bin/env python3

import sys
import pyvisa

if len(sys.argv) != 3:
    print("Usage: hp5421a_hardcopy.py <GPIB address> <output filename>")
    sys.exit(1)

gpib_addr       = int(sys.argv[1])
output_filename = sys.argv[2]

rm = pyvisa.ResourceManager()

# Replace 'GPIB::ADDRESS' with the GPIB address of your device
inst = rm.open_resource(f'GPIB::{gpib_addr}')

try:
    inst.write(":HARDcopy:mode DJ5XBW75DPI")
    data = inst.query(":HARDcopy:PRINT?")

    # Read data from the device
    #data = inst.read_raw()

    with open(output_filename, 'wb') as file:
        file.write(data)

except pyvisa.VisaIOError as e:
    print(f"Error: {e}")
