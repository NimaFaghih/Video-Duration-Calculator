# Video Duration Calculator 

A simple desktop utility to calculate total durations of video files inside folders and optionally rename folders to include their durations. The project separates business logic (video traversal, FFprobe calls, renaming) from the UI, making it easy to test and reuse.

---

## Features

- Scan a selected folder recursively for video files (configurable extensions)
- Use `ffprobe` (FFmpeg) to get accurate video durations (fast and robust)
- Summarize durations per-folder, and a final report with totals
- Optional: Rename folders by appending the duration in minutes (e.g., `Chapter 01 (33 min)`)
- Clean separation between UI and logic:
  - `calculator/core.py` — traversal and duration calculation
  - `calculator/renamer.py` — rename & revert functionality
  - `gui.py` — Tkinter-based GUI
  - `main.py` — launcher entrypoint

---

## Requirements

- Python 3.8+
- FFmpeg (ffprobe must be in your PATH)
  - Windows: Download from https://ffmpeg.org/download.html and add to PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg` (or your distro's package manager)

Optional (for building a bundled exe):

- PyInstaller

---

## Quick Start

1. Clone the repo and open a terminal in the project root.
  ```bash
  git clone https://github.com/NimaFaghih/Video-Duration-Calculator.git
  ```
2. Run the GUI directly:

  ```bash
  python main.py
  ```

3. Select the folder containing videos and click "Calculate Duration".

4. To rename folders (optional), click "Rename Folders" and confirm.

## Download

Download the latest version of **Video Duration Calculator** here:

[Download Video Duration Calculator v1.0](https://github.com/NimaFaghih/Video-Duration-Calculator/releases/download/v1.0/VidDurationCalculator.exe)
