# ScreenQR

ScreenQR is a lightweight, background desktop application that allows you to scan QR codes directly from any place on your screen without having to save screenshots or upload them online.

It operates similarly to the Windows Snipping Tool. Just press a global hotkey, select the area of your screen containing the QR code(s), and instantly get the results in a popup with options to copy or open links.

## Features
- **Global Hotkey**: Press `Ctrl + Shift + Q` to instantly trigger a scan.
- **Multi-Monitor Support**: Select regions across all connected displays.
- **Fast Decoding**: Uses OpenCV and runs on a background thread to prevent UI freezing.
- **Modern UI**: Dark mode popup with one-click copy and link opening.
- **System Tray**: Runs unobtrusively in the background.

## Requirements
- Python 3.12+
- Windows (Tested), Linux, macOS

## Installation

1. Clone or download this repository.
2. Navigate to the project directory:
   ```bash
   cd ScreenQR
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. You will see a notification in your system tray that ScreenQR has started.
3. Whenever you see a QR code on your screen, press **Ctrl + Shift + Q**.
4. Your screen will dim. Click and drag your mouse over the QR code to select it.
5. Release the mouse button. If a QR code is detected, a popup will appear with the decoded text!

## Notes on Global Hotkeys
This application uses the `keyboard` module for registering global shortcuts. On some systems (especially Linux/macOS), this may require administrator/root privileges or specific accessibility permissions.

## Building an Executable
You can bundle ScreenQR into a standalone `.exe` using PyInstaller.

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Build the project:
   ```bash
   python -m PyInstaller --noconsole --onefile --windowed main.py -n ScreenQR --clean -y --exclude PyQt5 --exclude PySide2 --exclude PySide6
   ```
3. You will find your standalone `ScreenQR.exe` in the generated `dist` folder.
