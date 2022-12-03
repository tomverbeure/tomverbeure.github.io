#! /usr/bin/env python3

import pyvisa


# Return an array with 256 integers.
# Each integer is a value between 64 and 79, representing a nibble
# from 0 to 15.
def read_cal_data(hp3478a):
    cal_data = []

    for addr in range(0, 256):
        # To fetch one nibble: 'W<address>', where address is a raw 8-bit number.
        # 87 = 'W'
        cmd = bytes([87, addr])
    
        hp3478a.write_raw(cmd)
        rvalue = ord(hp3478a.read()[0])
        assert rvalue >= 64 and rvalue < 80
        cal_data.append(rvalue)
    print()

    return cal_data

def print_cal_data(cal_data):
    s = ""
    for addr in range(0, 256):
        if (addr % 16) == 0:
    	    print("%04x:" % addr, end='')
        print(" %02x" % cal_data[addr], end='')
        s += chr(cal_data[addr])
        if (addr % 16) == 15:
            print("  %s" % s)
            s = ""
    print()

def verify_checksum(cal_data):
    # @@@A@IADOD@MM -> hex 0 0 0 1 0 9 1 4 F 4 0 D D  Checksum = 0xDD  1+9+1+4+F+4+DD = 0xFF
    for entry in range(0,19):
        sum = 0
        for idx in range(0, 13):
            val = cal_data[entry*13 + idx + 1]-64
            if idx!=11:
                sum += val
            else:
                sum += val*16

        print("Checksum %2d: 0x%02x " % (entry,sum), end='')
        if sum==255:
            print(" PASS")
        else:
            print(" FAIL")
    print()

def write_binary_file(filename, cal_data):
    with open(filename, "wb") as f:
        f.write(bytes(cal_data))
    pass


print("Fetching calibration data...")
rm = pyvisa.ResourceManager()
hp3478a = rm.open_resource('GPIB0::7::INSTR')
cal_data = read_cal_data(hp3478a)

print("Contents of calibration RAM:")
print_cal_data(cal_data)

print("Checksum for all calibration values:")
verify_checksum(cal_data)

print("Writing calibration data to 'hp3478a_cal_data.bin'.")
write_binary_file("hp3478a_cal_data.bin", cal_data)

