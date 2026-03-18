# Voice Typer — Claude Agent Guide

This document tells a Claude agent everything needed to understand, reproduce, modify, and extend this project from scratch.

---

## What this is

A Windows background utility that records microphone input on a global hotkey (Ctrl+Space), transcribes it locally using faster-whisper (no API key, no internet), and types the result into whatever window has keyboard focus. Runs as a system tray app.

---

## Architecture

Each concern is isolated in its own module. `main.py` wires them together.

```
hotkey.py    →  detects Ctrl+Space globally via pynput
recorder.py  →  captures mic audio as float32 numpy array at 16kHz
transcriber.py → runs faster-whisper on the audio, returns text string
typer.py     →  pastes text into active window via clipboard (pyperclip + pyautogui)
tray.py      →  pystray system tray icon, two states: idle (grey) / recording (red)
main.py      →  loads model, starts hotkey listener + tray, handles state transitions
```

---

## Key design decisions

- **faster-whisper over openai-whisper**: No PyTorch dependency (~2GB). Uses CTranslate2 backend, pip-installable, fast on CPU.
- **Clipboard paste over keystroke simulation**: `pyautogui.typewrite()` breaks on unicode/special characters. Using `pyperclip.copy()` + `Ctrl+V` is universal and reliable.
- **Toggle model (not push-to-talk)**: Press once to start, press again to stop. More natural for longer dictation than holding a key.
- **Suppress=False on listener**: We don't suppress Ctrl+Space to avoid breaking normal Ctrl+Space behavior in apps (e.g. IDEs). Accepted tradeoff.
- **Tray icon drawn with Pillow**: No external image files. Icon is generated programmatically as a mic shape in grey (idle) or red (recording).
- **Transcription runs on a background thread**: Keeps the hotkey listener responsive while Whisper processes audio.

---

## Reproducing from scratch

### 1. Prerequisites
- Windows 10/11
- Python 3.9+

### 2. Install dependencies
```bash
pip install faster-whisper sounddevice numpy pynput pyautogui pyperclip pystray Pillow
```

### 3. File creation order
Create these files in order (each depends on the previous):
1. `recorder.py` — no dependencies
2. `transcriber.py` — no dependencies
3. `typer.py` — no dependencies
4. `hotkey.py` — no dependencies
5. `tray.py` — depends on Pillow, pystray
6. `main.py` — imports all of the above

### 4. First run
```bash
python main.py
```
On first run, faster-whisper downloads the `small` model (~244MB) to `~/.cache/huggingface/`. This is automatic and only happens once.

### 5. Auto-start
```bash
python main.py --add-to-startup
```
Writes to `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` using `winreg`.

---

## Modifying the hotkey

Edit `hotkey.py`. The combo logic is in `_on_press()` and `_on_release()`. Currently tracks `_ctrl_held` state and fires on Space when Ctrl is held.

To change to a single key (e.g. Caps Lock):
```python
if key == keyboard.Key.caps_lock:
    # toggle recording
```

To change to a different combo (e.g. Alt+Space):
```python
if key in (keyboard.Key.alt_l, keyboard.Key.alt_r):
    _alt_held = True
if key == keyboard.Key.space and _alt_held:
    # toggle recording
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

## Common issues

**No audio captured** — check that `sounddevice` can see your mic: `python -c "import sounddevice; print(sounddevice.query_devices())"`

**Text not typing** — ensure the target window has focus before pressing Ctrl+Space. Some apps (elevated/admin windows) block `pyautogui` input.

**Whisper download slow** — set `HF_TOKEN` env var for higher rate limits (free HuggingFace account). Not required.

**App not in tray after startup reboot** — verify registry entry: `reg query HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v VoiceTyper`
