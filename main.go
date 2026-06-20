package main

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"os"
	"path/filepath"
)

const TNEFSignature = 0x223E9F21

type Attachment struct {
	Title string
	Data  []byte
}

type MagicSignature struct {
	Ext     string
	Header  []byte
	Trailer []byte
}

var MagicSignatures = []MagicSignature{
	{Ext: "png", Header: []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}, Trailer: []byte{0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82}},
	{Ext: "jpg", Header: []byte{0xff, 0xd8, 0xff}, Trailer: []byte{0xff, 0xd9}},
	{Ext: "gif", Header: []byte("GIF89a"), Trailer: []byte{0x00, 0x3b}},
	{Ext: "gif", Header: []byte("GIF87a"), Trailer: []byte{0x00, 0x3b}},
	{Ext: "pdf", Header: []byte("%PDF-"), Trailer: []byte("%%EOF")},
	{Ext: "zip", Header: []byte("PK\x03\x04"), Trailer: nil},
	{Ext: "rar", Header: []byte("Rar!\x1a\x07\x00"), Trailer: nil},
	{Ext: "rar", Header: []byte("Rar!\x1a\x07\x01\x00"), Trailer: nil},
	{Ext: "mp3", Header: []byte("ID3"), Trailer: nil},
	{Ext: "mp4", Header: []byte("\x00\x00\x00\x18ftyp"), Trailer: nil},
	{Ext: "mp4", Header: []byte("\x00\x00\x00\x20ftyp"), Trailer: nil},
	{Ext: "wav", Header: []byte("RIFF"), Trailer: nil},
}

func decodeString(val []byte) string {
	// Simple UTF-16LE check & conversion to string
	if len(val) >= 2 && val[1] == 0 {
		runes := make([]rune, 0, len(val)/2)
		for i := 0; i < len(val)-1; i += 2 {
			r := rune(binary.LittleEndian.Uint16(val[i : i+2]))
			if r != 0 {
				runes = append(runes, r)
			}
		}
		return string(runes)
	}
	return string(bytes.Trim(val, "\x00 "))
}

func parseTNEF(data []byte) ([]Attachment, error) {
	if len(data) < 6 {
		return nil, fmt.Errorf("dữ liệu quá ngắn")
	}

	sig := binary.LittleEndian.Uint32(data[0:4])
	if sig != TNEFSignature {
		return nil, fmt.Errorf("không phải định dạng TNEF (winmail.dat)")
	}

	key := binary.LittleEndian.Uint16(data[4:6])
	fmt.Printf("ℹ️  Phát hiện định dạng winmail.dat (TNEF). Khóa bảo mật: %d\n", key)

	var attachments []Attachment
	var currentAtt Attachment

	offset := 6
	for offset < len(data) {
		if offset+9 > len(data) {
			break
		}

		level := data[offset]
		attrID := binary.LittleEndian.Uint16(data[offset+1 : offset+3])
		_ = binary.LittleEndian.Uint16(data[offset+3 : offset+5]) // attrType
		length := binary.LittleEndian.Uint32(data[offset+5 : offset+9])

		offset += 9
		if offset+int(length)+2 > len(data) {
			fmt.Printf("⚠️  Cảnh báo: File bị cắt cụt ở offset %d\n", offset)
			break
		}

		value := data[offset : offset+int(length)]
		// checksum := binary.LittleEndian.Uint16(data[offset+int(length) : offset+int(length)+2])
		offset += int(length) + 2

		if level == 2 { // LVL_ATTACHMENT
			if attrID == 0x8010 { // ATT_ATTACH_TITLE
				currentAtt.Title = decodeString(value)
			} else if attrID == 0x800F { // ATT_ATTACH_DATA
				currentAtt.Data = make([]byte, len(value))
				copy(currentAtt.Data, value)
			}

			if currentAtt.Title != "" && len(currentAtt.Data) > 0 {
				attachments = append(attachments, currentAtt)
				currentAtt = Attachment{}
			}
		}
	}
	return attachments, nil
}

func carveFiles(data []byte, outputDir string) (int, error) {
	if err := os.MkdirAll(outputDir, 0755); err != nil {
		return 0, err
	}

	fmt.Println("ℹ️  Bắt đầu quét nhị phân để trích xuất file (File Carving)...")
	count := 0

	for _, sig := range MagicSignatures {
		startIdx := 0
		for {
			idx := bytes.Index(data[startIdx:], sig.Header)
			if idx == -1 {
				break
			}
			absoluteIdx := startIdx + idx

			endIdx := -1
			if sig.Trailer != nil {
				trailerIdx := bytes.Index(data[absoluteIdx+len(sig.Header):], sig.Trailer)
				if trailerIdx != -1 {
					endIdx = absoluteIdx + len(sig.Header) + trailerIdx + len(sig.Trailer)
				}
			}

			if endIdx == -1 {
				nextHeaderIdx := len(data)
				for _, otherSig := range MagicSignatures {
					ohIdx := bytes.Index(data[absoluteIdx+len(sig.Header):], otherSig.Header)
					if ohIdx != -1 {
						candidate := absoluteIdx + len(sig.Header) + ohIdx
						if candidate < nextHeaderIdx {
							nextHeaderIdx = candidate
						}
					}
				}
				maxSize := 15 * 1024 * 1024 // 15MB max limit per carved file
				if absoluteIdx+maxSize < nextHeaderIdx {
					endIdx = absoluteIdx + maxSize
				} else {
					endIdx = nextHeaderIdx
				}
			}

			fileData := data[absoluteIdx:endIdx]
			if len(fileData) > 0 {
				filename := fmt.Sprintf("extracted_%d.%s", count+1, sig.Ext)
				outPath := filepath.Join(outputDir, filename)
				if err := os.WriteFile(outPath, fileData, 0644); err != nil {
					return count, err
				}
				fmt.Printf("✅ Đã trích xuất bằng quét nhị phân: %s (%d bytes, offset: 0x%x)\n", filename, len(fileData), absoluteIdx)
				count++
			}

			startIdx = absoluteIdx + len(sig.Header)
		}
	}

	return count, nil
}

func main() {
	if len(os.Args) < 2 {
		fmt.Printf("Sử dụng: go run main.go <đường_dẫn_file_dat> [thư_mục_đầu_ra]\n")
		os.Exit(1)
	}

	datFile := os.Args[1]
	outputDir := "extracted_files"
	if len(os.Args) > 2 {
		outputDir = os.Args[2]
	}

	data, err := os.ReadFile(datFile)
	if err != nil {
		fmt.Printf("❌ Lỗi không thể đọc file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("ℹ️  Đang xử lý file: %s\n", datFile)

	// 1. Thử giải nén TNEF (winmail.dat)
	attachments, err := parseTNEF(data)
	if err == nil && len(attachments) > 0 {
		if err := os.MkdirAll(outputDir, 0755); err != nil {
			fmt.Printf("❌ Không thể tạo thư mục đầu ra: %v\n", err)
			os.Exit(1)
		}

		for _, att := range attachments {
			outPath := filepath.Join(outputDir, att.Title)
			// Avoid overwriting
			base := outPath
			ext := filepath.Ext(outPath)
			baseNoExt := base[:len(base)-len(ext)]
			counter := 1
			for {
				if _, err := os.Stat(outPath); os.IsNotExist(err) {
					break
				}
				outPath = fmt.Sprintf("%s_%d%s", baseNoExt, counter, ext)
				counter++
			}

			if err := os.WriteFile(outPath, att.Data, 0644); err != nil {
				fmt.Printf("❌ Lỗi ghi file %s: %v\n", att.Title, err)
				continue
			}
			fmt.Printf("✅ Đã trích xuất: %s (%d bytes)\n", filepath.Base(outPath), len(att.Data))
		}
		fmt.Printf("✅ Hoàn thành! Đã giải nén %d file đính kèm vào thư mục '%s'.\n", len(attachments), outputDir)
		os.Exit(0)
	}

	// 2. Chuyển sang quét nhị phân tổng quát
	fmt.Println("⚠️  File không phải là winmail.dat hoặc bị lỗi cấu trúc. Chuyển sang quét nhị phân tổng quát...")
	count, err := carveFiles(data, outputDir)
	if err != nil {
		fmt.Printf("❌ Lỗi khi quét nhị phân: %v\n", err)
		os.Exit(1)
	}

	if count > 0 {
		fmt.Printf("✅ Hoàn thành! Đã trích xuất %d file vào thư mục '%s'.\n", count, outputDir)
	} else {
		fmt.Println("⚠️  Không tìm thấy file hợp lệ nào thông qua quét chữ ký nhị phân.")
	}
}
