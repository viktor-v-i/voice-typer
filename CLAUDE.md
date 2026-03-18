# Voice Typer — Claude Agent Guide

This document tells a Claude agent everything needed to understand, reproduce, modify, and extend this project from scratch.

---

## What this is

A background utility that records microphone input on a global hotkey (Ctrl+Space), transcribes it locally using faster-whisper (no API key, no internet), and types the result into whatever window has keyboard focus. Runs as a system tray app. Currently implemented for Windows; Linux port is planned (see bottom of this file).

---

## Architecture

Each concern is isolated in its own module. `main.py` wires them together.

```
hotkey.py      →  detects Ctrl+Space globally via `keyboard` library
recorder.py    →  captures mic audio as float32 numpy array at 16kHz
transcriber.py →  runs faster-whisper on the audio, returns text string
typer.py       →  pastes text into active window via clipboard (pyperclip + pyautogui)
tray.py        →  pystray system tray icon, two states: idle (grey) / recording (red)
main.py        →  loads model, starts hotkey listener + tray, handles state transitions
```

---

## Key design decisions

- **faster-whisper over openai-whisper**: No PyTorch dependency (~2GB). Uses CTranslate2 backend, pip-installable, fast on CPU.
- **Clipboard paste over keystroke simulation**: `pyautogui.typewrite()` breaks on unicode/special characters. Using `pyperclip.copy()` + `Ctrl+V` is universal and reliable.
- **Toggle model (not push-to-talk)**: Press once to start, press again to stop. More natural for longer dictation than holding a key.
- **`keyboard` library over `pynput` on Windows**: `pynput` only captured keys when the terminal had focus. `keyboard` hooks globally regardless of focus.
- **`pythonw.exe` over `python.exe`**: Must be launched with `pythonw` (no console window). When a terminal window is attached, it intercepts Ctrl+Space before the global hook sees it. Running detached fixes this. The `--add-to-startup` flag handles this automatically.
- **Tray icon drawn with Pillow**: No external image files. Icon is generated programmatically as a mic shape in grey (idle) or red (recording).
- **Transcription runs on a background thread**: Keeps the hotkey listener responsive while Whisper processes audio.

---

## Reproducing from scratch (Windows)

### 1. Prerequisites
- Windows 10/11
- Python 3.9+

### 2. Install dependencies
```bash
pip install faster-whisper sounddevice numpy keyboard pyautogui pyperclip pystray Pillow
```

### 3. File creation order
1. `recorder.py` — no dependencies
2. `transcriber.py` — no dependencies
3. `typer.py` — no dependencies
4. `hotkey.py` — depends on `keyboard`
5. `tray.py` — depends on Pillow, pystray
6. `main.py` — imports all of the above

### 4. First run
```bash
pythonw main.py
```
Use `pythonw`, not `python`. On first run, faster-whisper downloads the `small` model (~244MB) to `~/.cache/huggingface/`. This is automatic and only happens once.

### 5. Auto-start
```bash
python main.py --add-to-startup
```
Writes to `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` using `winreg`. The registry entry uses `pythonw.exe` automatically.

---

## Modifying the hotkey

Edit `hotkey.py`. Uses the `keyboard` library — change the combo string in `keyboard.add_hotkey()`:

```python
keyboard.add_hotkey("ctrl+space", _toggle, suppress=True)
# Other examples: "alt+space", "ctrl+shift+r", "caps lock"
```

---

## Modifying the Whisper model

Edit `transcriber.py`:
```python
MODEL_SIZE = "small"  # tiny | base | small | medium | large
```

For GPU acceleration (Nvidia):
```python
_model = WhisperModel(MODEL_SIZE, device="cuda", compute_type="float16")
```

---

## Common issues (Windows)

**Hotkey not working globally** — make sure you're running with `pythonw.exe`, not `python.exe`. A visible terminal window intercepts Ctrl+Space.

**No audio captured** — check mic: `python -c "import sounddevice; print(sounddevice.query_devices())"`

**Text not typing** — ensure target window has focus before pressing Ctrl+Space. Elevated (admin) windows block pyautogui input.

**Whisper download slow** — set `HF_TOKEN` env var for higher rate limits (free HuggingFace account). Not required.

**App not in tray after reboot** — verify registry: `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v VoiceTyper`

---

## Linux port — what needs to change

The codebase is mostly cross-platform. These are the parts that need updating:

### 1. `hotkey.py` — swap `keyboard` for `pynput`
The `keyboard` library requires root on Linux. `pynput` works without root on X11/Wayland and is the right choice here.

```python
# Replace keyboard.add_hotkey with pynput listener
from pynput import keyboard

_ctrl_held = False
_recording = False

def _on_press(key):
    global _ctrl_held, _recording
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        _ctrl_held = True
    if key == keyboard.Key.space and _ctrl_held:
        # toggle recording

def _on_release(key):
    global _ctrl_held
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        _ctrl_held = False

listener = keyboard.Listener(on_press=_on_press, on_release=_on_release)
listener.start()
```

May need `python3-xlib` on X11: `sudo apt install python3-xlib`

### 2. `typer.py` — replace pyautogui/pyperclip with xdotool
`pyautogui` Ctrl+V paste is less reliable on Linux. `xdotool` is more robust on X11:

```bash
sudo apt install xdotool xclip
```

```python
import subprocess

def type_text_unicode(text):
    # Copy to clipboard via xclip, then paste via xdotool
    subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode(), check=True)
    subprocess.run(["xdotool", "key", "ctrl+v"], check=True)
```

For Wayland, use `wl-clipboard` + `ydotool` instead.

### 3. `main.py` — replace winreg auto-start with XDG autostart
Instead of the Windows registry, Linux uses `~/.config/autostart/`:

```python
def add_to_startup():
    import os
    autostart_dir = os.path.expanduser("~/.config/autostart")
    os.makedirs(autostart_dir, exist_ok=True)
    desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Voice Typer
Exec=python3 {os.path.abspath(__file__)}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
    with open(os.path.join(autostart_dir, "voice-typer.desktop"), "w") as f:
        f.write(desktop_entry)
```

### 4. No `pythonw` needed on Linux
On Linux, just run `python3 main.py &` or via the autostart `.desktop` entry. No console interception issue.

### 5. Add `install.sh`
```bash
#!/bin/bash
sudo apt install python3-pip xdotool xclip python3-xlib portaudio19-dev -y
pip3 install faster-whisper sounddevice numpy pynput pyautogui pyperclip pystray Pillow
python3 main.py --add-to-startup
echo "Done. Run: python3 main.py"
```

### 6. `tray.py` — may need AppIndicator
`pystray` on Linux requires either `AppIndicator3` or `gtk` backend. Install:
```bash
sudo apt install gir1.2-appindicator3-0.1
```
The pystray code itself doesn't need to change.

### Summary of Linux changes
| File | Change |
|------|--------|
| `hotkey.py` | Replace `keyboard` with `pynput` |
| `typer.py` | Replace pyperclip+pyautogui with xclip+xdotool |
| `main.py` | Replace `winreg` startup with XDG `.desktop` file |
| `install.sh` | New file — Linux setup script |
| `install.bat` | Windows only, keep as-is |
