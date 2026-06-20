# DAT File Extractor

A lightweight, standalone tool written in **Go** and **Python** to extract or carve files out of `.dat` files. 

It automatically detects and supports two modes of extraction:
1. **Outlook TNEF (`winmail.dat`) Extraction**: Decodes email attachments sent via Microsoft Outlook/Exchange.
2. **Binary File Carving**: Scans raw binary `.dat` containers (like game assets or system archives) for embedded standard formats (**PNG, JPG, GIF, PDF, ZIP, RAR, MP3, MP4, WAV**).

---

## 📦 Pre-built Releases (No Go/Python Installation Required)

You can download the pre-compiled binaries directly from the [GitHub Releases Page](https://github.com/wind7vn/unzip/releases/tag/v1.0.0):

| OS | Architecture | Download Link |
| :--- | :--- | :--- |
| **🍎 macOS** | Apple Silicon (M1/M2/M3/M4) | [extractor-mac-arm64](https://github.com/wind7vn/unzip/releases/download/v1.0.0/extractor-mac-arm64) |
| **🍎 macOS** | Intel | [extractor-mac-amd64](https://github.com/wind7vn/unzip/releases/download/v1.0.0/extractor-mac-amd64) |
| **🐧 Linux** | 64-bit | [extractor-linux-amd64](https://github.com/wind7vn/unzip/releases/download/v1.0.0/extractor-linux-amd64) |
| **🪟 Windows** | 64-bit | [extractor-windows-amd64.exe](https://github.com/wind7vn/unzip/releases/download/v1.0.0/extractor-windows-amd64.exe) |

### Quick Start with Pre-built Releases:

#### 🍎 macOS
1. Download `extractor-mac-arm64` (for M1/M2/M3/M4) or `extractor-mac-amd64` (for Intel Macs).
2. Open Terminal, make the binary executable, and register the alias:
   ```bash
   chmod +x extractor-mac-arm64
   echo "alias extractor=\"\$PWD/extractor-mac-arm64\"" >> ~/.zshrc
   source ~/.zshrc
   ```
3. Run the tool: `extractor path/to/file.dat`

#### 🐧 Linux
1. Download `extractor-linux-amd64`.
2. Open Terminal, make it executable, and register the alias:
   ```bash
   chmod +x extractor-linux-amd64
   echo "alias extractor=\"\$PWD/extractor-linux-amd64\"" >> ~/.bashrc
   source ~/.bashrc
   ```
   *(Or copy it to your path: `sudo cp extractor-linux-amd64 /usr/local/bin/extractor`)*
3. Run the tool: `extractor path/to/file.dat`

#### 🪟 Windows
1. Download `extractor-windows-amd64.exe`.
2. Copy the `.exe` file to a folder (e.g., `C:\tools`) and rename it to `extractor.exe`.
3. Add `C:\tools` to your system's **PATH** environment variable (search for "Environment Variables" in the Start menu).
4. Open Command Prompt or PowerShell and run:
   ```cmd
   extractor path\to\file.dat
   ```

---

## 🚀 Quick Start (Clone & Run from Source)

If you prefer to compile from source or run via Python, clone the repository first:
```bash
git clone https://github.com/wind7vn/unzip.git
cd unzip
```

### 🐹 Go Source Build (Prerequisites)
1. **Install Go**:
   - **macOS**: `brew install go`
   - **Linux**: `sudo apt install golang-go`
   - **Windows**: `winget install GoLang.Go`
2. **Build the Binary**:
   - macOS / Linux: `go build -o extractor main.go`
   - Windows: `go build -o extractor.exe main.go`

### 🐍 Python Execution
No installation is required besides Python 3 (uses standard library only):
* macOS / Linux: `python3 extractor.py <path_to_dat_file> [output_directory]`
* Windows: `python extractor.py <path_to_dat_file> [output_directory]`

---

## 📂 Supported Formats for Carving
If the file is not a `winmail.dat` file, the tool scans for the following embedded signatures:
- **Images**: `.png`, `.jpg`, `.gif`
- **Documents**: `.pdf`
- **Archives**: `.zip`, `.rar`
- **Audio/Video**: `.mp3`, `.mp4`, `.wav`
