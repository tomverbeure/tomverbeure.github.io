#!/usr/bin/env python3

import argparse
import io
import pyvisa
from pyvisa.constants import StatusCode

from PIL import Image

def screendump(filename):
    rm = pyvisa.ResourceManager('')

    # Siglent SDS2304X
    scope = rm.open_resource('USB0::0xF4EC::0xEE3A::SDS2XJBD1R2754::INSTR')
    scope.read_termination = None

    scope.write('SCDP')
    data = scope.read_raw(2000000)
    image = Image.open(io.BytesIO(data))
    image.save(filename)
    scope.close()
    rm.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Grab a screenshot from a Siglent DSO.')
    parser.add_argument('--output', '-o', dest='filename', required=True,
        help='the output filename')
    
    args = parser.parse_args()
    screendump(args.filename)

