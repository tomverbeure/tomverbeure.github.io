#! /usr/bin/env python3
import pyvisa

rm = pyvisa. ResourceManager()
instr = rm.open_resource("GPIB::8")

idn = instr.query("*IDN?")
assert idn.split(",")[1] == "R3273"

instr.write("HCOPY")
instr.query("BMP?")



