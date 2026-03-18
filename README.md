# Voice Typer

A lightweight background utility that lets you dictate into any application using local speech-to-text. Press **Ctrl + Space** to start recording, press again to stop — the transcript is typed wherever your cursor is.

No cloud. No API key. Fully offline using [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

Works on **Windows** and **Linux** (X11).

---

## How it works

- Press **Ctrl + Space** → mic opens, tray icon turns red
- Speak
- Press **Ctrl + Space** again → audio is transcribed locally → text is typed into the active window

Works in any app: terminals, browsers, search bars, editors, chat apps.

---

## Requirements

### Windows
- Windows 10 or 11
- Python 3.9+ ([download](https://www.python.org/downloads/))
- A microphone

### Linux
- Ubuntu 22.04+ / Debian 12+ (tested on Ubuntu 24.04)
- Python 3.9+
- X11 session (Wayland is not supported)
- A microphone

---

## Installation

### Windows

```bash
git clone https://github.com/YOUR_USERNAME/voice-typer.git
cd voice-typer
install.bat
```

`install.bat` will:
1. Install all Python dependencies
2. Register the app to auto-start with Windows

### Linux

```bash
git clone https://github.com/YOUR_USERNAME/voice-typer.git
cd voice-typer
chmod +x install.sh
./install.sh
```

`install.sh` will:
1. Install system dependencies (`xdotool`, `xclip`, `python3-xlib`, `portaudio19-dev`, `gir1.2-appindicator3-0.1`)
2. Create a Python virtual environment at `.venv`
3. Install Python dependencies into the venv
4. Register the app to auto-start on login

---

## Running manually

### Windows

```bash
pythonw main.py
```

Use `pythonw` (not `python`) — this runs without a console window so the global hotkey works across all windows and monitors.

### Linux

```bash
nohup .venv/bin/python3 main.py > /dev/null 2>&1 &
```

A mic icon appears in your system tray. The app is ready.

On first run, faster-whisper downloads the `small` model (~244MB) to `~/.cache/huggingface/`. This is automatic and only happens once.

---

## Auto-start

### Windows

```bash
python main.py --add-to-startup
```

Creates a Task Scheduler task that runs at logon.

### Linux

```bash
.venv/bin/python3 main.py --add-to-startup
```

Creates a desktop entry at `~/.config/autostart/voice-typer.desktop`.

### Remove from startup

```bash
python main.py --remove-from-startup       # Windows
.venv/bin/python3 main.py --remove-from-startup  # Linux
```

---

## Configuration

**Change hotkey** — edit `hotkey.py`. The combo is defined in `_on_press()`.

**Change Whisper model** — edit `transcriber.py`:

```python
MODEL_SIZE = "small"  # Options: tiny, base, small, medium, large
```

| Model  | Size   | Speed (CPU) | Accuracy |
|--------|--------|-------------|----------|
| tiny   | 39MB   | ~0.5s       | Basic    |
| base   | 74MB   | ~0.8s       | OK       |
| small  | 244MB  | ~1-2s       | Good     |
| medium | 769MB  | ~3-4s       | Better   |
| large  | 1.5GB  | ~6-8s       | Best     |

The model downloads automatically on first run and is cached locally.

---

## Linux notes

- **X11 required** — `xdotool` and `pynput` do not work under Wayland. You must be running an X11 session.
- **Virtual environment required on Ubuntu 24.04+** — PEP 668 means pip refuses to install system-wide. The install script handles this automatically.
- **Tray icon** — the system tray icon may not appear in GNOME without AppIndicator support (`gir1.2-appindicator3-0.1`). The app works fine without the tray icon.
- **Text input** — uses `xdotool type` for direct keystroke simulation. Clipboard-based paste is unreliable on Linux X11.
- **Audio quality** — on Linux, audio is captured at the mic's native sample rate and resampled to 16kHz via `soxr` for best Whisper accuracy. PulseAudio/PipeWire's built-in resampler degrades transcription quality.
- **Restarting** — kill existing instances before restarting: `pkill -f "voice-typer/main.py"`

---

## Quitting

Right-click the tray icon → **Quit**.
