#! /usr/bin/env python3

import sys
from struct import pack


BIN_TO_ASCII = [
	'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R',
	'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '2', '3', '4', '5', '6', '7', '8', '9'
]

SSC_UNSCRAMBLE_MAP = (
	8, 0x4000, 0x2000, 0x40000, 0x80000, 4, 0x80000000, 2,
	0x100, 0x20, 0x100000, 0x2000000, 0x20000, 0x10, 0x40, 0x400000,
	0x200000, 0x80, 0x4000000, 0x200, 0x800, 0x400, 0x1000, 0x800000,
	0x10000000, 0x1000000, 0x8000, 0x40000000, 1, 0x10000, 0x8000000, 0x20000000
)


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


def scramble_bits(queue):
	result = 0
	for i in range(32):
		if queue & SSC_UNSCRAMBLE_MAP[i]:
			result |= 1 << i
	return result


def ssc_encrypt(src):
	queue = 0xEFD02100
	result = bytearray([src[0] ^ 0xA5])
	queue >>= 8
	queue |= result[0] << 24
	salt = scramble_bits(queue) >> 24

	for c in src[1:]:
		encrypted = c ^ salt
		result.append(encrypted)
		queue >>= 8
		queue |= encrypted << 24
		salt = scramble_bits(queue) >> 24

	return bytes(result)


def bin_to_key(data):
	out_len = len(data) * 8 // 5
	if len(data) * 8 % 5 != 0:
		out_len += 1

	result = ''
	in_val = 0
	in_bits = 0
	in_pos = 0
	out_cnt = 0

	for _ in range(out_len):
		if in_bits < 5:
			if in_pos < len(data):
				in_val |= data[in_pos] << in_bits
			in_bits += 8
			in_pos += 1

		result += BIN_TO_ASCII[in_val & 0x1F]
		out_cnt += 1
		if (out_cnt % 5) == 0:
			result += '-'
		in_val >>= 5
		in_bits -= 5

	return result.strip('-')


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


def encode_for_uid(uid, mask):
	num_data_bits = len(mask) * 8
	pt_for_crc = bytes([num_data_bits]) + uid + b"\x00\x00" + mask + b"\x00" * (27 - len(mask) - 9)
	crc = crc16(pt_for_crc)
	pt_for_enc = bytes([num_data_bits]) + uid + pack("<H", crc) + mask
	return bin_to_key(ssc_encrypt(pt_for_enc))


def encode(model, sn, mask):
	return encode_for_uid(generate_uid(model, sn), mask)


def main(argv):
	if len(argv) != 4:
		print("Usage:\tkeygen <model> <S/N> <option mask> - generate options key")
		return 1

	print(encode(argv[1], argv[2], bytes.fromhex(argv[3])))
	return 0


if __name__ == "__main__":
	sys.exit(main(sys.argv))
