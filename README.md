# Voice Typer

A lightweight Windows background utility that lets you dictate into any application using local speech-to-text. Press **Ctrl + Space** to start recording, press again to stop — the transcript is typed wherever your cursor is.

No cloud. No API key. Fully offline using [faster-whisper](https://github.com/SYSTRAN/faster-whisper).

---

## How it works

- Press **Ctrl + Space** → mic opens, tray icon turns red
- Speak
- Press **Ctrl + Space** again → audio is transcribed locally → text is typed into the active window

Works in any app: terminals, browsers, search bars, editors, chat apps.

---

## Requirements

- Windows 10 or 11
- Python 3.9+ ([download](https://www.python.org/downloads/))
- A microphone

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/voice-typer.git
cd voice-typer
install.bat
```

`install.bat` will:
1. Install all Python dependencies
2. Register the app to auto-start with Windows

---

## Running manually

```bash
python main.py
```

A mic icon appears in your system tray. The app is ready.

---

## Auto-start with Windows

```bash
python main.py --add-to-startup
```

To remove from startup:

```bash
python main.py --remove-from-startup
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
| small  | 244MB  | ~1-2s       | Good ✓   |
| medium | 769MB  | ~3-4s       | Better   |
| large  | 1.5GB  | ~6-8s       | Best     |

The model downloads automatically on first run and is cached locally.

---

## Project structure

```
voice-typer/
├── main.py           # Entry point — wires all modules together
├── hotkey.py         # Global Ctrl+Space hotkey listener (pynput)
├── recorder.py       # Microphone capture (sounddevice)
├── transcriber.py    # Local Whisper transcription (faster-whisper)
├── typer.py          # Types text into active window (pyperclip + pyautogui)
├── tray.py           # System tray icon with idle/recording states (pystray)
├── requirements.txt
└── install.bat       # One-shot setup script
```

---

## Quitting

Right-click the tray icon → **Quit**.
