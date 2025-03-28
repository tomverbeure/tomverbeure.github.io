#! /usr/bin/env python3

import sys

def xor_file_bytes(file_path):
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            if not data:
                print("File is empty.")
                return None

            result = 0
            for byte in data:
                result ^= byte

            return result

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    file_path = sys.argv[1]
    xor_result = xor_file_bytes(file_path)
    if xor_result is not None:
        print(f"XOR result of all bytes in the file '{file_path}': {xor_result:#04x}")


