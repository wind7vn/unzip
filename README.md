# Trích xuất và giải nén File `.dat` (DAT File Extractor)

Dự án này cung cấp hai công cụ độc lập viết bằng **Python** và **Go** để giải nén hoặc trích xuất dữ liệu từ các tệp tin `.dat` (bao gồm `winmail.dat` của Outlook và quét trích xuất file ẩn từ file nhị phân).

---

## 🐹 Cài đặt phiên bản Go (Khuyên dùng)

Để biên dịch và sử dụng phiên bản Go dưới dạng lệnh hệ thống `extractor` toàn cục, hãy thực hiện theo 3 bước sau:

### Bước 1: Cài đặt Go (Prerequisite)

Nếu máy tính của bạn chưa được cài đặt ngôn ngữ Go, hãy cài đặt theo các phương thức dưới đây:

*   **🍎 Trên macOS**:
    Cài đặt nhanh qua Homebrew:
    ```bash
    brew install go
    ```
    *Hoặc tải bộ cài đặt `.pkg` trực tiếp tại [go.dev/dl](https://go.dev/dl/).*

*   **🐧 Trên Linux**:
    Cài đặt qua trình quản lý gói của bản phân phối (ví dụ Ubuntu/Debian):
    ```bash
    sudo apt update
    sudo apt install golang-go
    ```
    *Hoặc làm theo hướng dẫn cài đặt thủ công tại [go.dev/doc/install](https://go.dev/doc/install).*

*   **🪟 Trên Windows**:
    Cài đặt nhanh qua winget:
    ```cmd
    winget install GoLang.Go
    ```
    *Hoặc tải bộ cài đặt `.msi` trực tiếp tại [go.dev/dl](https://go.dev/dl/).*

---

### Bước 2: Biên dịch (Build) file chạy cho hệ điều hành của bạn

Chạy lệnh tương ứng trong thư mục dự án để biên dịch ra file chạy độc lập:

*   **🍎 Trên macOS**:
    ```bash
    go build -o extractor main.go
    ```
*   **🐧 Trên Linux**:
    ```bash
    go build -o extractor main.go
    ```
*   **🪟 Trên Windows**:
    ```bash
    go build -o extractor.exe main.go
    ```
    *(Nếu biên dịch chéo từ Mac/Linux sang Windows: `GOOS=windows GOARCH=amd64 go build -o extractor.exe main.go`)*

---

### Bước 3: Thêm lệnh chạy nhanh `extractor` vào hệ thống (Add to PATH/Alias)

Sau khi đã biên dịch xong file chạy ở Bước 2, mở Terminal ngay tại thư mục dự án và thực hiện cấu hình:

#### 🍎 1. Trên macOS
Chạy lệnh sau để tự động lấy đường dẫn hiện tại và đăng ký alias:
```bash
echo "alias extractor=\"\$PWD/extractor\"" >> ~/.zshrc
source ~/.zshrc
```
*(Bây giờ bạn có thể đứng ở bất kỳ đâu và chạy: `extractor file.dat`)*

#### 🐧 2. Trên Linux
Chạy lệnh sau để đăng ký alias cho shell Bash:
```bash
echo "alias extractor=\"\$PWD/extractor\"" >> ~/.bashrc
source ~/.bashrc
```
Hoặc sao chép file chạy trực tiếp vào thư mục hệ thống:
```bash
sudo cp extractor /usr/local/bin/extractor
```

#### 🪟 3. Trên Windows
1. Di chuyển file `extractor.exe` (đã build ở Bước 2) vào một thư mục cố định (ví dụ: `C:\tools`).
2. Thêm đường dẫn `C:\tools` vào biến môi trường **PATH** của hệ thống (Environment Variables):
   - Nhấn phím Windows, gõ "env" và chọn **Edit the system environment variables**.
   - Nhấp vào nút **Environment Variables**.
   - Tại mục **System variables**, chọn dòng **Path** và nhấn **Edit**.
   - Nhấn **New** và dán `C:\tools` vào. Nhấn **OK** để lưu lại.
3. Mở Command Prompt hoặc PowerShell mới và sử dụng:
   ```cmd
   extractor đường_dẫn_file.dat
   ```

---

## 🐍 Cách chạy bằng Python (`extractor.py`)

Nếu máy bạn đã có sẵn Python 3 và không muốn cài đặt Go:

*   **macOS / Linux**:
    ```bash
    python3 extractor.py <đường_dẫn_file_dat> [thư_mục_đầu_ra]
    ```
*   **Windows**:
    ```cmd
    python extractor.py <đường_dẫn_file_dat> [thư_mục_đầu_ra]
    ```

---

## 📂 Các tính năng chính được hỗ trợ

1. **Giải mã tự động `winmail.dat` (TNEF)**:
   - Tự động nhận diện cấu trúc file đính kèm gửi từ Outlook.
   - Hỗ trợ giải mã tên file định dạng UTF-16LE và UTF-8/ASCII.
2. **Quét dữ liệu nhị phân (File Carving)**:
   - Quét cấu trúc nhị phân của file `.dat` không rõ nguồn gốc.
   - Tự động trích xuất các file định dạng chuẩn nếu tìm thấy: **PNG, JPG, GIF, PDF, ZIP, RAR, MP3, MP4, WAV**.
