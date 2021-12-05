#! /usr/bin/env python3

import csv
import json

import pprint
pp = pprint.PrettyPrinter(indent=4)


def process_vic_aspect_ratio():
    vic_table = {}

    with open("vic_aspect_ratio_table.txt") as aspect_file:
        aspect_rows = csv.reader(aspect_file, delimiter=';')

        for row_nr, row in enumerate(aspect_rows):
            if len(row) != 6:
                continue
            row     = [ s.strip() for s in row ]
            print(row)

            vic_entry = {
                "vic"                   : int(row[0]),
                "resolution_descr"      : row[1],
                "refresh_descr"         : row[2],
                "pic_aspect_ratio"      : row[3],
                "pixel_aspect_ratio"    : row[4],
            }

            vic_table[ vic_entry["vic"] ] = vic_entry

    return vic_table
            
def process_vic_detailed_timing(vic_table):

    with open("vic_detailed_timing_table.txt") as timing_file:
        rows = csv.reader(timing_file, delimiter=';')

        for row_nr, row in enumerate(rows):
            if len(row) != 12:
                continue
            row     = [ s.strip() for s in row ]

            vics    = [ int(i) for i in row[0].split(',') ]
            for vic in vics:
                vic_entry = vic_table[vic]

                vic_entry["h_active"]       = int(row[1])
                vic_entry["v_active"]       = int(row[2])
                vic_entry["scan"]           = row[3]
                vic_entry["h_total"]        = int(row[4])
                vic_entry["h_blank"]        = int(row[5])
                vic_entry["v_total"]        = int(row[6])
                vic_entry["v_blank"]        = float(row[7])
                vic_entry["h_freq"]         = float(row[8])
                vic_entry["v_freq"]         = float(row[9])
                vic_entry["pix_clock"]      = float(row[10])

    return vic_table

def process_vic_sync_info(vic_table):

    with open("vic_detailed_sync_information.txt") as timing_file:
        rows = csv.reader(timing_file, delimiter=';')

        for row_nr, row in enumerate(rows):
            if len(row) != 13:
                continue
            row     = [ s.strip() for s in row ]

            print(len(row), row_nr, row)

            vics    = [ int(i) for i in row[0].split(',') ]
            for vic in vics:
                vic_entry = vic_table[vic]

                if row[12] == "":
                    sync_notes  = []
                else:
                    sync_notes  = [ int(i) for i in row[12].split(',') ]

                vic_entry["sync_fig"]       = int(row[1])
                vic_entry["h_front"]        = int(row[2])
                vic_entry["h_sync"]         = int(row[3])
                vic_entry["h_back"]         = int(row[4])
                vic_entry["h_pol"]          = row[5]
                vic_entry["v_front"]        = int(row[6])
                vic_entry["v_sync"]         = int(row[7])
                vic_entry["v_back"]         = int(row[8])
                vic_entry["v_pol"]          = row[9]
                vic_entry["sync_ln"]        = int(row[10])
                vic_entry["sync_ref_std"]   = row[11]
                vic_entry["sync_notes"]     = sync_notes

                pp.pprint(vic_entry)

                h_total_calc = vic_entry["h_active"] + vic_entry["h_blank"]
                h_blank_calc = vic_entry["h_front"] + vic_entry["h_sync"] + vic_entry["h_back"]
                v_total_calc = vic_entry["v_active"] + vic_entry["v_blank"]
                v_blank_calc = vic_entry["v_front"] + vic_entry["v_sync"] + vic_entry["v_back"]

                print("h_total(%f), h_total_calc(%f)" % (vic_entry["h_total"], h_total_calc))
                print("h_blank(%f), h_blank_calc(%f)" % (vic_entry["h_blank"], h_blank_calc))
                print("v_total(%f), v_total_calc(%f)" % (vic_entry["v_total"], v_total_calc))
                print("v_blank(%f), v_blank_calc(%f)" % (vic_entry["v_blank"], v_blank_calc))

                assert vic_entry["h_total"] == vic_entry["h_active"] + vic_entry["h_blank"] 
                assert vic_entry["h_blank"] == vic_entry["h_front"] + vic_entry["h_sync"] + vic_entry["h_back"]

                assert vic_entry["scan"] == "Int" or vic_entry["v_total"] == vic_entry["v_active"] + vic_entry["v_blank"]

                # Exclude timings with multiple sync values for the same VIC or non-int v_blank
                if vic not in [5,6,7,10,11,40,44,45,46,50,51,54,55,58,59,20,21,22,25,26, 8,9,12,13,23,24,27,28]:
                    assert vic_entry["v_blank"] == vic_entry["v_front"] + vic_entry["v_sync"] + vic_entry["v_back"]
    
                pix_clock_calc = vic_entry["h_total"] * vic_entry["v_total"] * vic_entry["v_freq"] / 1000000
                print(pix_clock_calc)
    
                assert vic_entry["scan"] == "Int" or abs(((pix_clock_calc - vic_entry["pix_clock"])/pix_clock_calc)) < 0.015
    

    return vic_table

vic_table = process_vic_aspect_ratio()
process_vic_detailed_timing(vic_table)
process_vic_sync_info(vic_table)

pp.pprint(vic_table[54])

with open("vic_timings.json", "w") as vic_timings_json:
    json.dump(vic_table, vic_timings_json, indent=2)
    
