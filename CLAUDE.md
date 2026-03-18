# Voice Typer - Claude Agent Guide

This document tells a Claude agent everything needed to understand, reproduce, modify, and extend this project from scratch.

---

## What this is

A background utility that records microphone input on a global hotkey (Ctrl+Space), transcribes it locally using faster-whisper (no API key, no internet), and types the result into whatever window has keyboard focus. Runs as a system tray app. Cross-platform: works on Windows and Linux (X11).

---

## Architecture

Each concern is isolated in its own module. `main.py` wires them together. Platform-specific code uses `sys.platform == "win32"` branching within each module.

```
hotkey.py      ->  detects Ctrl+Space globally
                   Windows: `keyboard` library (hooks globally without needing focus)
                   Linux: `pynput` (keyboard lib requires root on Linux)
recorder.py    ->  captures mic audio as float32 numpy array
                   Windows: records directly at 16kHz (driver handles it well)
                   Linux: records at mic's native rate, resamples to 16kHz via scipy
transcriber.py ->  runs faster-whisper on the audio, returns text string (cross-platform)
typer.py       ->  types text into active window
                   Windows: pyperclip + pyautogui (clipboard paste via Ctrl+V)
                   Linux: xdotool type (direct keystroke simulation, no clipboard)
tray.py        ->  pystray system tray icon, two states: idle (grey) / recording (red) (cross-platform)
main.py        ->  loads model, starts hotkey listener + tray, handles state transitions
                   Windows: winreg for auto-start
                   Linux: XDG ~/.config/autostart/ desktop entry
```

---

## Key design decisions

- **faster-whisper over openai-whisper**: No PyTorch dependency (~2GB). Uses CTranslate2 backend, pip-installable, fast on CPU.
- **Toggle model (not push-to-talk)**: Press once to start, press again to stop. More natural for longer dictation than holding a key.
- **Tray icon drawn with Pillow**: No external image files. Icon is generated programmatically as a mic shape in grey (idle) or red (recording).
- **Transcription runs on a background thread**: Keeps the hotkey listener responsive while Whisper processes audio.
- **No em dashes or unicode in tray tooltips**: pystray's X11 backend uses Latin-1 encoding for WM_NAME. Unicode characters like em dashes cause UnicodeEncodeError. Use plain ASCII only in tooltip strings.

### Windows-specific decisions
- **`keyboard` library over `pynput`**: `pynput` only captured keys when the terminal had focus. `keyboard` hooks globally regardless of focus.
- **Clipboard paste (pyperclip + pyautogui)**: `pyautogui.typewrite()` breaks on unicode/special characters. Using `pyperclip.copy()` + `Ctrl+V` is universal and reliable on Windows.
- **`pythonw.exe` over `python.exe`**: Must be launched with `pythonw` (no console window). When a terminal window is attached, it intercepts Ctrl+Space before the global hook sees it.

### Linux-specific decisions
- **`pynput` over `keyboard`**: The `keyboard` library requires root on Linux. `pynput` works without root on X11.
- **`xdotool type` over clipboard paste**: Clipboard-based paste (xclip + xdotool key ctrl+v) does NOT work reliably on Linux. The xdotool keystroke fires but the paste never actually happens in the target window. `xdotool type --clearmodifiers --delay 12` simulates keystrokes directly and works in both terminals and browsers.
- **Native sample rate + scipy resampling**: On Linux, PulseAudio/PipeWire resamples audio to 16kHz using a fast but low-quality algorithm, degrading Whisper accuracy (~50-60% vs ~80% on Windows with same model). Fix: capture at the mic's native rate (usually 44.1kHz or 48kHz) and resample to 16kHz in Python with `scipy.signal.resample`. The resample step adds ~1-5ms of latency.
- **No `pythonw` needed**: On Linux, run `python3 main.py &` or `nohup ... &`. No console interception issue.
- **Virtual environment required on Ubuntu 24.04+**: PEP 668 means pip refuses to install system-wide. Must use a venv.

---

## Setup - Windows

### 1. Prerequisites
- Windows 10/11
- Python 3.9+

### 2. Install dependencies
```bash
pip install faster-whisper sounddevice numpy keyboard pyautogui pyperclip pystray Pillow
```

### 3. First run
```bash
pythonw main.py
```
Use `pythonw`, not `python`. On first run, faster-whisper downloads the `small` model (~244MB) to `~/.cache/huggingface/`. This is automatic and only happens once.

### 4. Auto-start
```bash
python main.py --add-to-startup
```
Writes to `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` using `winreg`. The registry entry uses `pythonw.exe` automatically.

---

## Setup - Linux (Ubuntu/Debian, X11)

### 1. Prerequisites
- Ubuntu 22.04+ / Debian 12+ (tested on Ubuntu 24.04)
- Python 3.9+
- X11 session (Wayland not yet supported)
- A microphone

### 2. Install system dependencies
```bash
sudo apt install -y xdotool xclip python3-xlib portaudio19-dev gir1.2-appindicator3-0.1
```

### 3. Create virtual environment and install Python dependencies
```bash
cd voice-typer
python3 -m venv .venv
.venv/bin/pip install faster-whisper sounddevice numpy scipy pynput pystray Pillow
```

### 4. First run
```bash
nohup .venv/bin/python3 main.py > /dev/null 2>&1 &
```
On first run, faster-whisper downloads the `small` model (~244MB) to `~/.cache/huggingface/`.

The HF Hub "unauthenticated request" warning is normal and can be ignored - the model is public.

### 5. Restart
```bash
pkill -f "voice-typer/main.py"; nohup ~/voice-typer/.venv/bin/python3 ~/voice-typer/main.py > /dev/null 2>&1 &
```

### 6. Auto-start
```bash
.venv/bin/python3 main.py --add-to-startup
```
Creates `~/.config/autostart/voice-typer.desktop`. The desktop entry points to the venv python if available.

### 7. Tray icon
pystray falls back to the Xorg backend (raw X11 window) if AppIndicator/Ayatana is not available. The Xorg backend works but the icon may not appear in modern GNOME panels. Installing `gir1.2-appindicator3-0.1` helps but also requires PyGObject (`pip install PyGObject`) which needs dev libraries (`libcairo2-dev`, `libgirepository-2.0-dev`). The app works fine without the tray icon.

---

## Modifying the hotkey

Edit `hotkey.py`. The hotkey is Ctrl+Space on both platforms.

Windows uses `keyboard.add_hotkey("ctrl+space", ...)`.
Linux uses `pynput.keyboard.Listener` checking for Ctrl + Space.

---

## Modifying the Whisper model

Edit `transcriber.py`:
```python
MODEL_SIZE = "small"  # tiny | base | small | medium | large
```

| Model  | Size   | Speed (CPU) | Accuracy |
|--------|--------|-------------|----------|
| tiny   | 39MB   | ~0.5s       | Basic    |
| base   | 74MB   | ~0.8s       | OK       |
| small  | 244MB  | ~1-2s       | Good     |
| medium | 769MB  | ~3-4s       | Better   |
| large  | 1.5GB  | ~6-8s       | Best     |

For GPU acceleration (Nvidia):
```python
_model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
```

---

## Common issues

### Windows
- **Hotkey not working globally** - make sure you're running with `pythonw.exe`, not `python.exe`.
- **Text not typing** - ensure target window has focus. Elevated (admin) windows block pyautogui input.
- **App not in tray after reboot** - verify registry: `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v VoiceTyper`

### Linux
- **UnicodeEncodeError on startup** - tray tooltip contains non-ASCII characters (em dashes etc). Use only plain ASCII in `tray.py` tooltip strings.
- **xdotool clipboard paste not working** - do NOT use `xdotool key ctrl+v` or `xdotool key ctrl+shift+v` for pasting. It fires the keystroke but the paste doesn't happen. Use `xdotool type --clearmodifiers` instead.
- **Low transcription accuracy** - check that `recorder.py` captures at native sample rate and resamples via scipy. If recording directly at 16kHz, PulseAudio/PipeWire's internal resampler degrades audio quality significantly.
- **pip refuses to install** - Ubuntu 24.04+ requires a virtual environment (PEP 668). Use `python3 -m venv .venv`.
- **Multiple instances running** - kill all before restarting: `pkill -f "voice-typer/main.py"`

### Both platforms
- **No audio captured** - check mic: `python -c "import sounddevice; print(sounddevice.query_devices())"`
- **Whisper download slow** - set `HF_TOKEN` env var for higher rate limits (free HuggingFace account). Not required.

---

## Project structure

```
voice-typer/
├── main.py           # Entry point - wires all modules, handles auto-start
├── hotkey.py         # Global Ctrl+Space hotkey (keyboard on Windows, pynput on Linux)
├── recorder.py       # Microphone capture (sounddevice, scipy resampling on Linux)
├── transcriber.py    # Local Whisper transcription (faster-whisper)
├── typer.py          # Types text into active window (pyautogui on Windows, xdotool on Linux)
├── tray.py           # System tray icon with idle/recording states (pystray)
├── requirements.txt  # Python dependencies
├── install.bat       # Windows one-shot setup
├── install.sh        # Linux one-shot setup (Ubuntu/Debian)
└── CLAUDE.md         # This file
```
