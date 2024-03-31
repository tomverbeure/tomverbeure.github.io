#! /usr/bin/env python3

import sys
import csv

#req_file  = "gt-8031h-rx.csv"
#resp_file = "gt-8031h-tx.csv"

req_file    = sys.argv[1]
resp_file   = sys.argv[2]

req_transactions    = {}
resp_transactions   = {}

WAIT_FIRST_0X40     = 0
WAIT_SECOND_0X40    = 1
MESSAGE_ID0         = 2
MESSAGE_ID1         = 3
MESSAGE_DATA        = 4
MESSAGE_CHECKSUM    = 5
MESSAGE_TERMINATOR0 = 6
MESSAGE_TERMINATOR1 = 7

def bytes_to_int32(data):
    return data[3] + (data[2] << 8) + (data[1] << 16)+ (data[0] << 24)

def bytes_to_int16(data):
    return data[1] + (data[0] << 8)

class Message:

    msg_len_table = {
        "Aw"    : { 'req':    8,    'resp':   8 },
        "Bp"    : { 'req':    8,                },  # Replies with Co
        "Co"    : {                 'resp':  29 },
        "Ha"    : { 'req':    8,    'resp': 154 },
        "Hn"    : { 'req':    8,    'resp':  78 },
        "Gd"    : { 'req':    8,    'resp':   8 },
        "Ge"    : { 'req':    8,    'resp':   8 },
        "Cf"    : { 'req':    7,    'resp':   7 },
        "Gf"    : { 'req':    9,    'resp':   9 },
        "Bj"    : { 'req':    8,    'resp':   8 },
        "Gj"    : { 'req':    7,    'resp':  21 },
    }

    def __init__(self, req):
        self.req        = req
        self.timestamp  = None
        self.msg_id     = ""
        self.data       = []
        self.checksum   = []
        self.terminator = []

    def exp_msg_len(self):
        if len(self.msg_id) == 2:
            if self.req:
                return Message.msg_len_table[self.msg_id]['req']
            else:
                return Message.msg_len_table[self.msg_id]['resp']
        else:
            return None


    def msg_len(self):
        return 2 + len(self.msg_id) + len(self.data) + len(self.checksum) + len(self.terminator)

    def calc_checksum(self):
        checksum    = 0

        checksum    = checksum ^ ord(self.msg_id[0])
        checksum    = checksum ^ ord(self.msg_id[1])

        for b in self.data:
            checksum    = checksum ^ b

        return checksum


    def decodeHaResp(self):
        offset = 0
        month               = self.data[0]
        day                 = self.data[1]
        year                = bytes_to_int16(self.data[2:])
        offset += 4
        hours               = self.data[offset]
        minutes             = self.data[offset+1]
        seconds             = self.data[offset+2]
        frac_seconds        = bytes_to_int32(self.data[offset+3:])
        offset += 7
        lat                 = bytes_to_int32(self.data[offset+0:])
        lon                 = bytes_to_int32(self.data[offset+4:])
        height              = bytes_to_int32(self.data[offset+8:])
        msl_height          = bytes_to_int32(self.data[offset+12:])
        offset += 16
        lat_u               = bytes_to_int32(self.data[offset+0:])
        lon_u               = bytes_to_int32(self.data[offset+4:])
        height_u            = bytes_to_int32(self.data[offset+8:])
        msl_height_u        = bytes_to_int32(self.data[offset+12:])
        offset += 16
        speed3d             = bytes_to_int16(self.data[offset+0:])
        speed2d             = bytes_to_int16(self.data[offset+2:])
        heading             = bytes_to_int16(self.data[offset+4:])
        offset += 6
        geometry            = bytes_to_int16(self.data[offset+0:])
        offset += 2
        sats_visible        = self.data[offset+0]
        sats_tracked        = self.data[offset+1]
        offset += 2

        s = f"m:{month},d:{day},y:{year}"
        s += f"\n    h:{hours},m:{minutes},s:{seconds},fs:{frac_seconds}"
        s += f"\n    lat:{lat},lon:{lon},height:{height},msl_height:{msl_height}"
        s += f"\n    lat_u:{lat_u},lon_u:{lon_u},height_u:{height_u},msl_height_u:{msl_height_u}"
        s += f"\n    speed3d:{speed3d},speed2d:{speed2d},heading:{heading}"
        s += f"\n    sats_visible:{sats_visible},sats_tracked:{sats_tracked}"

        for i in range(12):
            svid            = self.data[offset+0]
            mode            = self.data[offset+1]
            signal          = self.data[offset+2]
            iode            = self.data[offset+3]
            chan_status     = bytes_to_int16(self.data[offset+4:])

            offset += 6

            s += f"\n        svid:{svid},mode:{mode},signal:{signal},iode:{iode},status:{chan_status}"

        recv_status         = bytes_to_int16(self.data[offset+0:])
        reserved            = bytes_to_int16(self.data[offset+2:])
        clock_bias          = bytes_to_int16(self.data[offset+4:])
        osc_offset          = bytes_to_int32(self.data[offset+6:])
        osc_temp            = bytes_to_int16(self.data[offset+10:])
        utc_param           = self.data[offset+12]
        gmt_sign            = self.data[offset+13]
        gmt_h_offset        = self.data[offset+14]
        gmt_m_offset        = self.data[offset+15]
        offset += 16
        id_tag              = self.data[offset:offset+6]

        s += f"\n    recv_status:{recv_status},reserved:{reserved},clock_bias:{clock_bias},osc_offset:{osc_offset},osc_temp:{osc_temp}"
        s += f"\n    utc_param:{utc_param}:gmt_sign:{gmt_sign},gmt_h_offset:{gmt_h_offset},gmt_m_offset:{gmt_m_offset}"
        s += f"\n    id_tag:{id_tag}"

        return s

    def decodeBjResp(self):
        leap_s_status       = self.data[0]

        s = f"leap_s_status:{leap_s_status}"

        return s

    def decodeGjResp(self):
        offset = 0
        present_leap_s      = self.data[0]
        future_leap_s       = self.data[1]
        future_leap_y       = bytes_to_int16(self.data[offset+2:])
        future_leap_m       = self.data[4]
        future_leap_d       = self.data[5]
        current_utc_off_i   = self.data[6]
        current_utc_off_f   = bytes_to_int32(self.data[offset+7:])
        future_leap_h       = self.data[11]
        future_leap_m       = self.data[12]
        future_leap_s       = self.data[13]

        s = f"present_leap_s:{present_leap_s}, future_leap_s:{future_leap_s}"

        return s

    def decodeHnResp(self):
        pulse_on            = bool(self.data[0])
        pulse_sync          = ['UTC', 'GPS'][self.data[1]]
        time_raim_sol       = self.data[2]
        svids_removed       = self.data[6] + (self.data[5] << 8) + (self.data[4] << 16)+ (self.data[3] << 24)
        time_accuracy_est   = self.data[7] + (self.data[8] << 8)

        if self.data[9] >= 128:
            sawtooth_error      = 127-self.data[9]
        else:
            sawtooth_error      = self.data[9]

        s = f"pulse:{pulse_on}, pulse_sync:{pulse_sync}, time_raim_sol:{time_raim_sol}, svids_removed:{svids_removed}"
        s += f", time_accuracy_est:{time_accuracy_est}"
        s += f", sawtooth_error:{sawtooth_error}"

        offset = 10

        for i in range(12):
            sat_id                  = self.data[offset]
            offset += 1
            fract_local_time        = self.data[offset + 3] + (self.data[offset + 2] << 8) + (self.data[offset + 1] << 16)+ (self.data[offset + 0] << 24)
            offset += 4

            s += f"\n"
            s += f"       sat_id:{sat_id}"
            s += f", fract_local_time:{fract_local_time}"

        return s
        
        

    def __str__(self):
        s = ""

        s += f"{self.msg_id}: {self.data}, {self.checksum}, {self.terminator} - { self.msg_len() } - { self.timestamp }"

        if self.msg_len() == self.exp_msg_len():
            if self.req:
                pass
            else:
                if self.msg_id == "Ha":
                    s += "\n    " + self.decodeHaResp()
                elif self.msg_id == "Hn":
                    s += "\n    " + self.decodeHnResp()
                elif self.msg_id == "Gj":
                    s += "\n    " + self.decodeGjResp()
                elif self.msg_id == "Bj":
                    s += "\n    " + self.decodeBjResp()

        return s

def process_trace(filename, transactions, req=True):
    with open(filename) as csv_file: 
        resp_reader = csv.reader(csv_file, delimiter=",")
    
        state = WAIT_FIRST_0X40
    
        cur_msg     = None
        exp_msg_len = None
    
        for line_nr,row in enumerate(resp_reader):
            #print(">", line_nr, len(row), '|'.join(row))
            if int(line_nr) == 0:
                continue
    
            trans_nr    = int(row[0])
            timestamp   = float(row[1])
            data_byte   = int(row[2],16)
            data_char   = chr(data_byte)
    
            #print(state, line_nr, "0x%02x/%c" % (data_byte,data_byte), cur_msg, exp_msg_len)
    
            if state == WAIT_FIRST_0X40:
                if data_byte == 0x40:
                    cur_msg     = Message(req)
                    cur_msg.timestamp   = timestamp

                    state = WAIT_SECOND_0X40
                else:
                    print("Unexpected byte...")
    
            elif state == WAIT_SECOND_0X40:
                if data_byte == 0x40:
                    state = MESSAGE_ID0
                else:
                    state = WAIT_FIRST_0x40
    
            elif state == MESSAGE_ID0:
                cur_msg.msg_id += data_char
                state = MESSAGE_ID1
    
            elif state == MESSAGE_ID1:
                cur_msg.msg_id += data_char
                exp_msg_len = cur_msg.exp_msg_len()
    
                if exp_msg_len == 7:
                    state = MESSAGE_CHECKSUM
                else:
                    state = MESSAGE_DATA
    
            elif state == MESSAGE_DATA:
                cur_msg.data.append(data_byte)
    
                if cur_msg.msg_len() == exp_msg_len-3:
                    state = MESSAGE_CHECKSUM
    
            elif state == MESSAGE_CHECKSUM:
                cur_msg.checksum.append(data_byte)
    
                if cur_msg.calc_checksum() != data_byte:
                    print(f"Received checksum ({data_byte}) != expected checksum ({cur_msg.calc_checksum()})")
                    #assert(False)
                else:
                    #print(f"Checksum matched!")
                    pass
    
    
                state = MESSAGE_TERMINATOR0
    
            elif state == MESSAGE_TERMINATOR0:
                cur_msg.terminator.append(data_byte)
                state = MESSAGE_TERMINATOR1
    
            elif state == MESSAGE_TERMINATOR1:
                cur_msg.terminator.append(data_byte)
                print(cur_msg)
                cur_msg     = None
    
                state = WAIT_FIRST_0X40
    

print(f"Processing req file: {req_file}")
process_trace(req_file, req_transactions, req=True)
print(f"Processing resp file: {resp_file}")
process_trace(resp_file, resp_transactions, req=False)
