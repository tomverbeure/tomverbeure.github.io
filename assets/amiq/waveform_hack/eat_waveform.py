#!/usr/bin/env python3

import sys
import struct

with open(sys.argv[1], 'rb') as f:
    data = f.read()

# this is naive, but oh well
data = data.split(b"{IWAVEFORM-")[1]
bytecount,data = data.split(b": ", 1)

assert data[0:3] == b'0,#'
assert data[-1:] == b'}'

data = data[3:-1]

bytecount = int(bytecount) - 3
assert len(data) == bytecount

print(bytecount, len(data))

last_datum = None

while len(data):
    datum,data = data[0:4], data[4:]
    datum, = struct.unpack("<L", datum)
    
    if last_datum == None:
        last_datum = datum
        continue
    
    decrypt_datum = (((last_datum >> 1) | ((last_datum & 1) << 31)) ^ datum) - last_datum
    if decrypt_datum < 0:
        decrypt_datum += 0x100000000
    decrypt_datum = (decrypt_datum >> 1) | ((decrypt_datum & 1) << 31)
    last_datum = datum
    
    q = decrypt_datum >> 16
    i = decrypt_datum & 0xFFFF
    
    if i & 0x8000:
        i = -0x10000 + i
    if q & 0x8000:
        q = -0x10000 + q
    
    print(f"{i}, {q}")
