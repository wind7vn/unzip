#!/usr/bin/env python3
import os
import sys
import struct

# Emojis for beautiful console output
INFO = "ℹ️ "
SUCCESS = "✅"
WARNING = "⚠️"
ERROR = "❌"
FILE_EMOJI = "📄"
DIR_EMOJI = "📁"

# Microsoft TNEF Constants (for winmail.dat)
TNEF_SIGNATURE = 0x223E9F21
LVL_MESSAGE = 1
LVL_ATTACHMENT = 2

# TNEF Attribute IDs
ATT_ATTACH_DATA = 0x800F
ATT_ATTACH_TITLE = 0x8010
ATT_ATTACH_METAFILE = 0x8011
ATT_ATTACH_PROPS = 0x9003
ATT_ATTACH_RENDDATA = 0x9002

# Standard File Magic Signatures for Carving
MAGIC_SIGNATURES = [
    {"ext": "png", "header": b"\x89PNG\r\n\x1a\n", "trailer": b"\x49\x45\x4e\x44\xae\x42\x60\x82"},
    {"ext": "jpg", "header": b"\xff\xd8\xff", "trailer": b"\xff\xd9"},
    {"ext": "gif", "header": b"GIF89a", "trailer": b"\x00\x3b"},
    {"ext": "gif", "header": b"GIF87a", "trailer": b"\x00\x3b"},
    {"ext": "pdf", "header": b"%PDF-", "trailer": b"%%EOF"},
    {"ext": "zip", "header": b"PK\x03\x04", "trailer": None},  # Zip has variable ending, will carve until next or max size
    {"ext": "rar", "header": b"Rar!\x1a\x07\x00", "trailer": None},
    {"ext": "rar", "header": b"Rar!\x1a\x07\x01\x00", "trailer": None},
    {"ext": "mp3", "header": b"ID3", "trailer": None},
    {"ext": "mp4", "header": b"\x00\x00\x00\x18ftyp", "trailer": None},
    {"ext": "mp4", "header": b"\x00\x00\x00\x20ftyp", "trailer": None},
    {"ext": "wav", "header": b"RIFF", "trailer": None}, # check for WAVE later
]

class TNEFParser:
    """A pure Python parser for Outlook's winmail.dat (TNEF) files."""
    def __init__(self, filepath):
        self.filepath = filepath
        self.attachments = []

    def parse(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Không tìm thấy file: {self.filepath}")

        with open(self.filepath, "rb") as f:
            data = f.read()

        if len(data) < 6:
            return False

        # Read signature (4 bytes) and key (2 bytes)
        sig, key = struct.unpack("<IH", data[:6])
        if sig != TNEF_SIGNATURE:
            return False

        print(f"{INFO} Phát hiện định dạng winmail.dat (TNEF). Khóa bảo mật: {key}")
        
        offset = 6
        current_attachment = {}

        while offset < len(data):
            if offset + 9 > len(data):
                break
            
            # Read Attribute Header: Level (1), ID (2), Type (2), Length (4)
            level, attr_id, attr_type, length = struct.unpack("<BHHI", data[offset:offset+9])
            offset += 9
            
            if offset + length + 2 > len(data):
                print(f"{WARNING} File bị cắt cụt ở offset {offset}")
                break
            
            attr_value = data[offset:offset+length]
            checksum = struct.unpack("<H", data[offset+length:offset+length+2])[0]
            offset += length + 2

            # Process attributes
            if level == LVL_ATTACHMENT:
                if attr_id == ATT_ATTACH_TITLE:
                    # Clean filename (it is null-terminated string)
                    if len(attr_value) >= 2 and attr_value[1] == 0:
                        filename = attr_value.decode("utf-16", errors="ignore").strip("\x00")
                    else:
                        filename = attr_value.decode("utf-8", errors="ignore").strip("\x00")
                    current_attachment["filename"] = os.path.basename(filename)
                elif attr_id == ATT_ATTACH_DATA:
                    current_attachment["data"] = attr_value
                
                # If we have both filename and data, save them
                if "filename" in current_attachment and "data" in current_attachment:
                    self.attachments.append(current_attachment)
                    current_attachment = {}
                    
        return True

    def extract_to(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        extracted_count = 0
        for att in self.attachments:
            filename = att.get("filename", f"attachment_{extracted_count+1}.dat")
            filepath = os.path.join(output_dir, filename)
            
            # Avoid overwriting existing files
            base, ext = os.path.splitext(filepath)
            counter = 1
            while os.path.exists(filepath):
                filepath = f"{base}_{counter}{ext}"
                counter += 1
                
            with open(filepath, "wb") as f:
                f.write(att["data"])
            print(f"{SUCCESS} Đã trích xuất: {os.path.basename(filepath)} ({len(att['data'])} bytes)")
            extracted_count += 1
        return extracted_count


def carve_files(filepath, output_dir):
    """Carves standard files out of an unknown binary .dat file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Không tìm thấy file: {filepath}")

    with open(filepath, "rb") as f:
        data = f.read()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"{INFO} Bắt đầu quét nhị phân để trích xuất file (File Carving)...")
    extracted_count = 0

    for sig_info in MAGIC_SIGNATURES:
        ext = sig_info["ext"]
        header = sig_info["header"]
        trailer = sig_info["trailer"]

        start_idx = 0
        while True:
            # Find the header
            idx = data.find(header, start_idx)
            if idx == -1:
                break
            
            # Determine end of file
            end_idx = -1
            if trailer:
                end_idx = data.find(trailer, idx + len(header))
                if end_idx != -1:
                    end_idx += len(trailer)
            
            # If no trailer found or not applicable, default to a reasonable max size (e.g. 10MB) or next header
            if end_idx == -1:
                # Find next occurrence of any header, or end of data
                next_header_idx = len(data)
                for other_sig in MAGIC_SIGNATURES:
                    oh = other_sig["header"]
                    h_idx = data.find(oh, idx + len(header))
                    if h_idx != -1 and h_idx < next_header_idx:
                        next_header_idx = h_idx
                
                # Limit size to 15MB max if no other header is found
                max_size = 15 * 1024 * 1024
                end_idx = min(next_header_idx, idx + max_size)

            # Extract the chunk
            file_data = data[idx:end_idx]
            if len(file_data) > 0:
                filename = f"extracted_{extracted_count + 1}.{ext}"
                out_path = os.path.join(output_dir, filename)
                with open(out_path, "wb") as out_f:
                    out_f.write(file_data)
                print(f"{SUCCESS} Đã trích xuất bằng quét nhị phân: {filename} ({len(file_data)} bytes, offset: {hex(idx)})")
                extracted_count += 1

            start_idx = idx + len(header)

    return extracted_count


def main():
    if len(sys.argv) < 2:
        print(f"Sử dụng: python3 {sys.argv[0]} <đường_dẫn_file_dat> [thư_mục_đầu_ra]")
        sys.exit(1)

    dat_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_files"

    if not os.path.isfile(dat_file):
        print(f"{ERROR} File '{dat_file}' không tồn tại hoặc không phải là file hợp lệ.")
        sys.exit(1)

    print(f"{INFO} Đang xử lý file: {dat_file}")
    
    # 1. Thử giải nén theo định dạng winmail.dat (TNEF)
    try:
        parser = TNEFParser(dat_file)
        is_tnef = parser.parse()
        if is_tnef:
            count = parser.extract_to(output_dir)
            print(f"{SUCCESS} Hoàn thành! Đã giải nén {count} file đính kèm vào thư mục '{output_dir}'.")
            sys.exit(0)
    except Exception as e:
        print(f"{WARNING} Lỗi khi thử phân tích winmail.dat: {e}")

    # 2. Nếu không phải winmail.dat, chuyển sang chế độ quét nhị phân tự động (File Carving)
    print(f"{WARNING} File không phải là winmail.dat hoặc bị lỗi cấu trúc. Chuyển sang quét nhị phân tổng quát...")
    try:
        count = carve_files(dat_file, output_dir)
        if count > 0:
            print(f"{SUCCESS} Hoàn thành! Đã trích xuất {count} file vào thư mục '{output_dir}'.")
        else:
            print(f"{WARNING} Không tìm thấy file hợp lệ nào thông qua quét chữ ký nhị phân.")
    except Exception as e:
        print(f"{ERROR} Đã xảy ra lỗi khi quét nhị phân: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
