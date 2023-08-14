#! /usr/bin/env python3

import sys
import re

re_phase = re.compile('^OT-21.*Phase: (T.*?) (.) dT: *([+-.0-9E]*)')
re_freq  = re.compile('^Freq: (\w+), (T.*?) Tau: *(\d+) dT: ')

with open(sys.argv[1]) as file:
    lines = [line.rstrip() for line in file]
    for line in lines:
        p = re_phase.match(line)
        if p is not None and False:
            timestamp   = p.group(1)
            unknown     = p.group(2)
            dT          = p.group(3)
            print(timestamp, unknown, dT)

        f = re_freq.match(line)
        if f is not None:
            status      = f.group(1)
            timestamp   = f.group(2)
            tau         = f.group(3)
            print(status, timestamp, tau)


