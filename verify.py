#!/usr/bin/env python3
import os
import subprocess
import shutil

def create_dummy_data():
    print("Creating dummy DAT files for verification...")
    
    # 1. Create a dummy file containing an embedded PNG file and an embedded PDF file
    png_header = b"\x89PNG\r\n\x1a\n"
    png_data = b"ThisIsSomeDummyPNGData"
    png_trailer = b"\x49\x45\x4e\x44\xae\x42\x60\x82"
    
    pdf_header = b"%PDF-"
    pdf_data = b"ThisIsSomeDummyPDFData"
    pdf_trailer = b"%%EOF"
    
    # Build a combined .dat file with random bytes between files
    dat_content = (
        b"RANDOM_HEADER_BYTES_123456" +
        png_header + png_data + png_trailer +
        b"RANDOM_MID_BYTES_7890" +
        pdf_header + pdf_data + pdf_trailer +
        b"RANDOM_TRAILER_BYTES"
    )
    
    with open("dummy_carve.dat", "wb") as f:
        f.write(dat_content)
    
    # 2. Create a basic dummy TNEF file (winmail.dat)
    tnef_sig = b"\x21\x9f\x3e\x22" # 0x223E9F21 in little endian
    tnef_key = b"\xab\xcd" # random key
    
    # Message level attribute (level 1)
    msg_level = b"\x01"
    msg_attr_id = b"\x01\x00"
    msg_attr_type = b"\x01\x00"
    msg_attr_len = b"\x04\x00\x00\x00"
    msg_attr_val = b"TEST"
    msg_checksum = b"\x00\x00" # dummy checksum
    
    # Attachment level attributes (level 2)
    # Title (filename)
    att_level = b"\x02"
    att_title_id = b"\x10\x80" # ATT_ATTACH_TITLE = 0x8010
    att_title_type = b"\x02\x00" # type 2 (string)
    title_str = b"test_attachment.txt\x00"
    att_title_len = struct_len_bytes(title_str)
    
    # Data
    att_data_id = b"\x0f\x80" # ATT_ATTACH_DATA = 0x800f
    att_data_type = b"\x06\x00" # type 6 (bytes)
    att_data_val = b"Hello, this is content from the winmail.dat attachment!"
    att_data_len = struct_len_bytes(att_data_val)
    
    tnef_content = (
        tnef_sig + tnef_key +
        msg_level + msg_attr_id + msg_attr_type + msg_attr_len + msg_attr_val + msg_checksum +
        att_level + att_title_id + att_title_type + att_title_len + title_str + msg_checksum +
        att_level + att_data_id + att_data_type + att_data_len + att_data_val + msg_checksum
    )
    
    with open("dummy_tnef.dat", "wb") as f:
        f.write(tnef_content)

def struct_len_bytes(val):
    import struct
    return struct.pack("<I", len(val))

def run_tests():
    # Setup test outputs
    for path in ["out_py_carve", "out_py_tnef", "out_go_carve", "out_go_tnef"]:
        if os.path.exists(path):
            shutil.rmtree(path)
            
    print("\n--- TESTING PYTHON EXTRACTOR ---")
    
    # Test carving
    print("Testing carving...")
    subprocess.run(["python3", "extractor.py", "dummy_carve.dat", "out_py_carve"], check=True)
    assert os.path.exists("out_py_carve/extracted_1.png"), "Carved PNG file missing!"
    assert os.path.exists("out_py_carve/extracted_2.pdf"), "Carved PDF file missing!"
    print("Python Carving OK!")
    
    # Test TNEF
    print("Testing TNEF extraction...")
    subprocess.run(["python3", "extractor.py", "dummy_tnef.dat", "out_py_tnef"], check=True)
    assert os.path.exists("out_py_tnef/test_attachment.txt"), "TNEF attachment file missing!"
    with open("out_py_tnef/test_attachment.txt", "r") as f:
        content = f.read()
        assert "Hello, this is content" in content, "TNEF content mismatch!"
    print("Python TNEF OK!")
    
    print("\n--- TESTING GO EXTRACTOR ---")
    
    # Test carving
    print("Testing carving...")
    subprocess.run(["go", "run", "main.go", "dummy_carve.dat", "out_go_carve"], check=True)
    assert os.path.exists("out_go_carve/extracted_1.png"), "Carved PNG file missing in Go!"
    assert os.path.exists("out_go_carve/extracted_2.pdf"), "Carved PDF file missing in Go!"
    print("Go Carving OK!")
    
    # Test TNEF
    print("Testing TNEF extraction...")
    subprocess.run(["go", "run", "main.go", "dummy_tnef.dat", "out_go_tnef"], check=True)
    assert os.path.exists("out_go_tnef/test_attachment.txt"), "TNEF attachment file missing in Go!"
    with open("out_go_tnef/test_attachment.txt", "r") as f:
        content = f.read()
        assert "Hello, this is content" in content, "TNEF content mismatch in Go!"
    print("Go TNEF OK!")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! Both Python and Go extractors work perfectly.")

if __name__ == "__main__":
    create_dummy_data()
    run_tests()
