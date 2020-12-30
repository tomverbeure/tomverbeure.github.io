#! /usr/bin/env python3

import csv

import pprint
pp = pprint.PrettyPrinter(indent=4)

dmt_table = []

with open('DMT_spreadsheet.csv', newline='') as csv_file:
    dmt_rows = csv.reader(csv_file, delimiter=',', quotechar='"')
    for row_nr, row in enumerate(dmt_rows):
        if row_nr < 2:
            continue

        if row_nr >= 90:
            break

        assert len(row) == 31
        print
        print(row_nr, '|, |'.join(row))

        if row[6] == "":
            byte_code_2     = None
        else:
            byte_code_2     = [ int(byte_str, 16) for byte_str in row[6].split(',') ]

        if row[7] == "":
            byte_code_3     = None
        else:
            byte_code_3     = [ int(byte_str, 16) for byte_str in row[7].split(',') ]

        assert row[8] in ["non-cvt", "cvt", "cvt-rb", "CEA-861"]

        dmt_entry =  {
                "h_active"      : int(row[0]),
                "v_pixels"      : int(row[1]),
                "v_freq"        : float(row[2]),
                "interlaced"    : (row[3] == "Interlaced"),
                "adopted"       : row[4],
                "dmt_id"        : int(row[5], 16),
                "2_byte_code"   : byte_code_2,
                "3_byte_code"   : byte_code_3,
                "type"          : row[8], 
        }

        if row[8] == "non-cvt":
            dmt_entry["pix_clock"]      = float(row[9])
            dmt_entry["hsync_pol"]      = row[10]
            dmt_entry["vsync_pol"]      = row[11]
            dmt_entry["h_total"]        = int(row[12])
            dmt_entry["h_addr"]         = int(row[13])
            dmt_entry["h_blank"]        = int(row[14])
            dmt_entry["h_right"]        = int(row[15])
            dmt_entry["h_front"]        = int(row[16])
            dmt_entry["h_sync"]         = int(row[17])
            dmt_entry["h_back"]         = int(row[18])
            dmt_entry["h_left"]         = int(row[19])

        if row[8] == "non-cvt" and not(dmt_entry["interlaced"]):
            dmt_entry["v_total"]        = int(row[20])
            dmt_entry["v_addr"]         = int(row[21])
            dmt_entry["v_blank"]        = int(row[22])
            dmt_entry["v_bottom"]       = int(row[23])
            dmt_entry["v_front"]        = int(row[24])
            dmt_entry["v_sync"]         = int(row[25])
            dmt_entry["v_back"]         = int(row[26])
            dmt_entry["v_top"]          = int(row[27])

            assert dmt_entry["h_total"] == dmt_entry["h_addr"] + dmt_entry["h_blank"] + dmt_entry["h_right"] + dmt_entry["h_left"]
            assert dmt_entry["h_blank"] == dmt_entry["h_front"] + dmt_entry["h_sync"] + dmt_entry["h_back"]

            assert dmt_entry["v_total"] == dmt_entry["v_addr"] + dmt_entry["v_blank"] + dmt_entry["v_bottom"] + dmt_entry["v_top"]
            assert dmt_entry["v_blank"] == dmt_entry["v_front"] + dmt_entry["v_sync"] + dmt_entry["v_back"]

            pix_clock_calc = dmt_entry["h_total"] * dmt_entry["v_total"] * dmt_entry["v_freq"] / 1000000
            print(pix_clock_calc)

            assert abs(((pix_clock_calc - dmt_entry["pix_clock"])/pix_clock_calc)) < 0.015

        dmt_table.append(dmt_entry)

pp.pprint(dmt_table)
