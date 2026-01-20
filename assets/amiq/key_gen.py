#! /usr/bin/env python3

import sys
import hashlib

feature_list = [ 
    "B1  - BER measurement", 
    "B19 - Rear I/Q outputs", 
    "B2  - Differential I/Q outputs", 
    "K11 - IS-95 CDMA", 
    "B3  - Digital I/Q output", 
    "K12 - Digital Standard CDMA2000", 
    "K13 - Digital Standard WCDMA TDD mode (3GPP)", 
    "K14 - Digital Standard TD-SCDMA", 
    "K15 - OFDM Signal Generation HIPERLAN/2", 
    "K16 - Digital Standard 802.11b", 
    "K17 - Digital Standard 1XEV-DO",
    "K18 - ",
    "K19 - Digital Standard 802.11",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    "K20 - ",
    ]

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} <serial_number> <feature nr: [0-13]>")
    print(f"e.g {sys.argv[0]} 830306/008 3")
    sys.exit(-1)

serial_number = sys.argv[1]
feature_nr    = sys.argv[2]

print(f"serial number: {serial_number}")
print(f"feature      : AMIQ-{feature_list[int(feature_nr)]}")

input_str = f"{serial_number}{feature_nr}"
md5_hash = hashlib.md5(input_str.encode('ascii')).digest()

key = 0
for i in range(8):
    key = (key * 10) + md5_hash[i*2] + md5_hash[i*2 +1]

key &= 0xFFFFFFFF
if key > 0x7FFFFFFF:
    key = (key - 0x100000000) * -1

print(f"key          : {key}")

