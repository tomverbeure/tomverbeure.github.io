#!/usr/bin/env python3
import argparse
import hashlib
import os
import struct
import subprocess
import sys
import tempfile
import zipfile

# Default paths
DEFAULT_INPUT_ZIP = "../tds3000_3.41_063354011.zip"

# Expected SHA256 hashes for the decompressed main oscilloscope application binary (3,407,640 bytes)
EXPECTED_ORIG_SHA256 = "a97816712bbae5f730e58363029847ac8102a626abcdafce829d28b59dbb0534"
EXPECTED_PATCHED_SHA256 = "c8c326aca73dd6be01f0303199c80d12fc664915c02d1a40d79c05656b8a05a4"

# Primary Patch: Master Engineering Option Predicate (isTDS3ENGInstalled / FUN_001c45dc)
# RAM Address: 0x001C45DC | File Offset: 0x001BE5DC
# Patching this function to unconditionally return 1 (TRUE) unlocks ALL options
# (TDS3FFT, TDS3TRG, TDS3AAM, TDS3LIM, TDS3VID, etc.) even when NO I2C PROMs are installed!
PATCH_OFFSET = 0x1BE5DC
EXPECTED_BYTES = b"\x94\x21\xFF\xF8\x7C\x08\x02\xA6"  # stwu r1, -8(r1); mflr r0
REPLACEMENT_BYTES = b"\x38\x60\x00\x01\x4E\x80\x00\x20"  # li r3, 1; blr

# Secondary I2C Decoder Patch (optional fallback): File Offset 0x1BEE54 (RAM 0x001C4E54)
I2C_DECODER_OFFSET = 0x1BEE54
I2C_DECODER_EXPECTED = b"\x94\x21\xFF\xE0\x7C\x08\x02\xA6"  # stwu r1, -0x20(r1); mflr r0
I2C_DECODER_REPLACEMENT = b"\x38\x60\x00\x05\x4E\x80\x00\x20"  # li r3, 5 (TDS3ENG); blr

# Original payload capacity bounds per floppy disk
DISK3_PAYLOAD_CAPACITY = 1454064
DISK4_PAYLOAD_CAPACITY = 807652


def calc_checksum(data: bytes) -> int:
    """Calculates the 32-bit big-endian additive checksum used in TDS3000 firmware headers."""
    total_sum = 0
    num_words = len(data) // 4
    for i in range(num_words):
        word = struct.unpack(">I", data[i * 4 : i * 4 + 4])[0]
        total_sum = (total_sum + word) & 0xFFFFFFFF

    # Process remaining trailing bytes (up to 3 bytes)
    for i in range(num_words * 4, len(data)):
        total_sum = (total_sum + data[i]) & 0xFFFFFFFF

    return (total_sum + 0x1234) & 0xFFFFFFFF


def process_patch(input_zip: str, output_zip: str) -> bool:
    print("=== Tektronix TDS3000 Firmware Patcher ===")
    print(f"Input ZIP:  {input_zip}")
    print(f"Output ZIP: {output_zip}\n")

    if not os.path.exists(input_zip):
        print(f"Error: Input ZIP file not found at '{input_zip}'")
        return False

    with tempfile.TemporaryDirectory() as temp_dir:
        print("1. Extracting firmware archive to temporary directory...")
        with zipfile.ZipFile(input_zip, "r") as z:
            z.extractall(temp_dir)

        disk3_path = os.path.join(temp_dir, "disk3/fwdisk3.dat")
        disk4_path = os.path.join(temp_dir, "disk4/fwdisk4.dat")

        if not os.path.exists(disk3_path) or not os.path.exists(disk4_path):
            print("Error: Required firmware files ('disk3/fwdisk3.dat', 'disk4/fwdisk4.dat') not found in archive.")
            return False

        print("2. Reading headers and payloads from disk3 and disk4...")
        with open(disk3_path, "rb") as f3:
            full_d3 = f3.read()
        with open(disk4_path, "rb") as f4:
            full_d4 = f4.read()

        header3 = full_d3[:96]
        header4 = full_d4[:96]
        payload3 = full_d3[96:]
        payload4 = full_d4[96:]

        # Read the compressed payload size from header offset 0x5C (92)
        comp_size = struct.unpack(">I", header3[92:96])[0]
        print(f"   Original compressed payload size: {comp_size} bytes (0x{comp_size:X})")

        # Concatenate and trim payload to exact size
        combined_payload = payload3 + payload4
        clean_payload = combined_payload[:comp_size]

        # Write to temporary file for decompression
        temp_z_path = os.path.join(temp_dir, "app_temp.Z")
        temp_bin_path = os.path.join(temp_dir, "app_temp.bin")

        with open(temp_z_path, "wb") as f_z:
            f_z.write(clean_payload)

        print("3. Decompressing main application payload (15-bit UNIX LZW)...")
        try:
            with open(temp_bin_path, "wb") as f_bin:
                subprocess.run(["gunzip", "-c", temp_z_path], stdout=f_bin, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: gunzip failed during decompression: {e}")
            return False

        # Read decompressed binary and verify checksums
        with open(temp_bin_path, "rb") as f_bin:
            bin_data = bytearray(f_bin.read())

        orig_sha = hashlib.sha256(bin_data).hexdigest()
        print(f"   Decompressed binary size: {len(bin_data)} bytes")
        print(f"   Original Binary SHA256:   {orig_sha}")

        if orig_sha == EXPECTED_ORIG_SHA256:
            print("   [✓] Original binary SHA256 matches official v3.41 firmware!")
        else:
            print("   [!] Notice: Original binary SHA256 differs from standard v3.41 reference.")

        # Verify bytes at patch offsets
        if len(bin_data) < PATCH_OFFSET + len(EXPECTED_BYTES):
            print(f"Error: Decompressed binary size ({len(bin_data)}) is smaller than patch offset.")
            return False

        current_bytes = bin_data[PATCH_OFFSET : PATCH_OFFSET + len(EXPECTED_BYTES)]
        if current_bytes != EXPECTED_BYTES:
            print(f"Error: Unexpected byte sequence at offset 0x{PATCH_OFFSET:X}.")
            print(f"       Expected: {' '.join(f'{b:02X}' for b in EXPECTED_BYTES)}")
            print(f"       Found:    {' '.join(f'{b:02X}' for b in current_bytes)}")
            return False

        print("4. Applying TDS3ENG master firmware patches (Zero-Hardware Unlocking)...")
        # 1. Patch runtime master predicate (RAM 0x001C45DC / File 0x001BE5DC) -> li r3, 1; blr
        bin_data[PATCH_OFFSET : PATCH_OFFSET + len(REPLACEMENT_BYTES)] = REPLACEMENT_BYTES
        print(f"   [+] Patched runtime option predicate at offset 0x{PATCH_OFFSET:X} (RAM 0x001C45DC)")
        print("       -> Unconditionally returns 1 (TRUE): Unlocks ALL features with 0 PROMs installed!")

        # 2. Patch I2C decoder (RAM 0x001C4E54 / File 0x001BEE54) -> li r3, 5 (TDS3ENG); blr
        if len(bin_data) >= I2C_DECODER_OFFSET + len(I2C_DECODER_EXPECTED):
            if bin_data[I2C_DECODER_OFFSET : I2C_DECODER_OFFSET + len(I2C_DECODER_EXPECTED)] == I2C_DECODER_EXPECTED:
                bin_data[I2C_DECODER_OFFSET : I2C_DECODER_OFFSET + len(I2C_DECODER_REPLACEMENT)] = (
                    I2C_DECODER_REPLACEMENT
                )
                print(f"   [+] Patched I2C appkey decoder at offset 0x{I2C_DECODER_OFFSET:X} (RAM 0x001C4E54)")
                print("       -> Automatically maps any inserted I2C PROM to TDS3ENG (Option ID 5)!")

        # Calculate SHA256 over the patched binary
        patched_sha = hashlib.sha256(bin_data).hexdigest()
        print(f"   Patched Binary SHA256:    {patched_sha}")

        if patched_sha == EXPECTED_PATCHED_SHA256:
            print("   [✓] Patched binary SHA256 verified exactly as expected!")
        else:
            print("   [!] Notice: Patched binary SHA256 differs from reference expectation.")

        # Save patched binary
        with open(temp_bin_path, "wb") as f_bin:
            f_bin.write(bin_data)

        print("5. Re-compressing main application payload (15-bit UNIX LZW)...")
        temp_patched_z_path = os.path.join(temp_dir, "app_patched.Z")
        try:
            with open(temp_patched_z_path, "wb") as f_z_out:
                subprocess.run(["compress", "-b", "15", "-c", temp_bin_path], stdout=f_z_out, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: compress failed during re-compression: {e}")
            return False

        with open(temp_patched_z_path, "rb") as f_z_out:
            new_compressed_payload = f_z_out.read()

        new_comp_size = len(new_compressed_payload)
        print(f"   New compressed size: {new_comp_size} bytes (0x{new_comp_size:X})")

        print("6. Splitting payload and recalculating additive header checksums...")
        if new_comp_size > DISK3_PAYLOAD_CAPACITY + DISK4_PAYLOAD_CAPACITY:
            print("Error: Patched and compressed payload exceeds floppy disk set storage capacity.")
            return False

        # Split payload
        new_payload3 = new_compressed_payload[:DISK3_PAYLOAD_CAPACITY]
        new_payload4 = new_compressed_payload[DISK3_PAYLOAD_CAPACITY:]

        # Pad payload 4 to original capacity
        new_payload4_padded = new_payload4.ljust(DISK4_PAYLOAD_CAPACITY, b"\x00")

        # Calculate new checksums
        new_checksum3 = calc_checksum(new_payload3)
        new_checksum4 = calc_checksum(new_payload4_padded)

        # Calculate Set ID (checksum of concatenated payload trimmed to exact size)
        new_set_id = calc_checksum(new_payload3 + new_payload4)

        print(f"   Disk 3 Checksum (0x08): 0x{new_checksum3:08X}")
        print(f"   Disk 4 Checksum (0x08): 0x{new_checksum4:08X}")
        print(f"   Set ID / Hash   (0x0C): 0x{new_set_id:08X}")

        # Update headers
        new_header3 = bytearray(header3)
        new_header3[8:12] = struct.pack(">I", new_checksum3)
        new_header3[12:16] = struct.pack(">I", new_set_id)
        new_header3[92:96] = struct.pack(">I", new_comp_size)

        new_header4 = bytearray(header4)
        new_header4[8:12] = struct.pack(">I", new_checksum4)
        new_header4[12:16] = struct.pack(">I", new_set_id)
        new_header4[92:96] = struct.pack(">I", new_comp_size)

        # Save updated dat files
        with open(disk3_path, "wb") as f3:
            f3.write(new_header3 + new_payload3)
        with open(disk4_path, "wb") as f4:
            f4.write(new_header4 + new_payload4_padded)

        print(f"7. Creating output archive '{output_zip}'...")
        out_dir = os.path.dirname(output_zip)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as z_out:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Exclude temp files used for patching
                    if file in ["app_temp.Z", "app_temp.bin", "app_patched.Z"]:
                        continue
                    # Keep relative path structure in ZIP
                    arcname = os.path.relpath(file_path, temp_dir)
                    z_out.write(file_path, arcname)

        print(f"\n=== Success! Patched ZIP created at '{output_zip}' ===")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Tektronix TDS3000 / TDS3052 Firmware Patcher (TDS3ENG Zero-Hardware Option Unlocker)"
    )
    parser.add_argument(
        "input_zip",
        nargs="?",
        default=DEFAULT_INPUT_ZIP,
        help=f"Path to input firmware ZIP archive (default: '{DEFAULT_INPUT_ZIP}')",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="output_zip",
        default=None,
        help="Path to output patched ZIP archive (default: '<input_name>_patched.zip')",
    )

    args = parser.parse_args()

    input_path = os.path.abspath(args.input_zip)
    if args.output_zip:
        output_path = os.path.abspath(args.output_zip)
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_patched{ext}"

    success = process_patch(input_path, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
