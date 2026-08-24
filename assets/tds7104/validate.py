#! /usr/bin/env python3

import sys
from struct import pack, unpack


ASCII_TO_BIN = {
	'A':0x00, 'B':0x01, 'C':0x02, 'D':0x03, 'E':0x04, 'F':0x05, 'G':0x06, 'H':0x07,
	'J':0x08, 'K':0x09, 'L':0x0A, 'M':0x0B, 'N':0x0C, 'P':0x0D, 'Q':0x0E, 'R':0x0F,
	'S':0x10, 'T':0x11, 'U':0x12, 'V':0x13, 'W':0x14, 'X':0x15, 'Y':0x16, 'Z':0x17,
	'a':0x00, 'b':0x01, 'c':0x02, 'd':0x03, 'e':0x04, 'f':0x05, 'g':0x06, 'h':0x07,
	'j':0x08, 'k':0x09, 'l':0x0A, 'm':0x0B, 'n':0x0C, 'p':0x0D, 'q':0x0E, 'r':0x0F,
	's':0x10, 't':0x11, 'u':0x12, 'v':0x13, 'w':0x14, 'x':0x15, 'y':0x16, 'z':0x17,
	'2':0x18, '3':0x19, '4':0x1A, '5':0x1B, '6':0x1C, '7':0x1D, '8':0x1E, '9':0x1F
}

SSC_SCRAMBLE_MAP = (
	0x10000000, 0x80, 0x20, 1, 0x2000, 0x200, 0x4000, 0x20000,
	0x100, 0x80000, 0x200000, 0x100000, 0x400000, 4, 2, 0x4000000,
	0x20000000, 0x1000, 8, 0x10, 0x400, 0x10000, 0x8000, 0x800000,
	0x2000000, 0x800, 0x40000, 0x40000000, 0x1000000, 0x80000000, 0x8000000, 0x40
)


def outhex(data):
	if len(data) <= 32:
		for b in data:
			print("%02X" % b, end=' ')
	else:
		for b in data[0:16]:
			print("%02X" % b, end=' ')
		print("...", end=' ')
		for b in data[-16:]:
			print("%02X" % b, end=' ')
	print("")


def crc16(data):
	crc = 0xFFFF
	for b in data:
		crc ^= b
		for _ in range(8):
			if crc & 1:
				crc = (crc >> 1) ^ 0x8408
			else:
				crc >>= 1
			crc &= 0xFFFF
	return crc


def unscramble_bits(queue):
	result = 0
	for i in range(32):
		if queue & (1 << i):
			result |= SSC_SCRAMBLE_MAP[i]
	return result


def ssc_decrypt(src):
	result = bytearray([src[0] ^ 0xA5])
	queue = 0xEFD02100
	queue >>= 8
	queue |= src[0] << 24
	salt = unscramble_bits(queue) >> 24

	for c in src[1:]:
		result.append(c ^ salt)
		queue >>= 8
		queue |= c << 24
		salt = unscramble_bits(queue) >> 24

	return bytes(result)


def key_to_bin(key):
	result = bytearray()
	out_pos = 0
	out_val = 0

	for c in key:
		out_val |= ASCII_TO_BIN[c] << out_pos
		out_pos += 5
		if out_pos >= 8:
			result.append(out_val & 0xFF)
			out_val >>= 8
			out_pos -= 8

	if out_pos != 0:
		result.append(out_val & 0xFF)

	return bytes(result)


def generate_uid(model, sn):
	sn_int = int(sn[1:])
	mdl_int = int(model[3:].strip('B'))
	if mdl_int > 0xFFFF:
		sn_int |= (mdl_int & 0xF) << 28
		mdl_int >>= 4
	if model[-1] == 'B':
		sn_int |= 0x02000000
	if model[0:3] == "CSA":
		sn_int |= 0x10000000
	return pack("<LH", sn_int, mdl_int)


def decode(key, model=None, sn=None):
	encrypted = key_to_bin(key.replace('-', ''))
	outhex(encrypted)

	pt = ssc_decrypt(encrypted + b"\x00" * (27 - len(encrypted)))
	outhex(pt)

	if model and sn and pt[1:7] != generate_uid(model, sn):
		print("UID mismatch !")
		print("UID in key:    ", end=' ')
		outhex(pt[1:7])
		print("Calculated UID:", end=' ')
		outhex(generate_uid(model, sn))

	if not model or not sn:
		m_pfx = "TDS/DSA/DPO"
		m_sfx = ""
		s, m = unpack("<LH", pt[1:7])
		if s & 0x10000000:
			m_pfx = "CSA"
		if s & 0x02000000:
			m_sfx = "B"
		if s & 0xE0000000:
			m = (m << 4) | (s >> 28)
		print("This key is for UID %04X%08X (S/N %d, model %s%d%s):" % (m, s, s & 0x00FFFFFF, m_pfx, m, m_sfx))

	num_data_bits = pt[0]
	payload_bytes = num_data_bits // 8
	payload_bits = num_data_bits % 8
	pt_for_crc = pt[0:7] + b"\x00\x00" + pt[9:9+payload_bytes]
	if payload_bits:
		pt_for_crc += bytes([pt[9+payload_bytes] & (0xFF >> (8-payload_bits))])
	pt_for_crc += b"\x00" * (27 - len(pt_for_crc))

	crc = crc16(pt_for_crc)
	print("CRC: %04X" % crc)
	if pt[7] != crc & 0xFF or pt[8] != crc >> 8:
		print("CRC mismatch !")
		return None

	return pt_for_crc[9:]


def main(argv):
	if len(argv) not in (2, 4):
		print("Usage: validate <options key> [<model> <S/N>]", file=sys.stderr)
		return 1

	model = None
	sn = None
	if len(argv) == 4:
		model = argv[2]
		sn = argv[3]

	opts = decode(argv[1], model, sn)
	if opts:
		print("Key is valid, active options:")
		outhex(opts)

	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv))
