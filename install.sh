#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[Voice Typer] Installing system dependencies..."
sudo apt install -y xdotool xclip python3-xlib portaudio19-dev gir1.2-appindicator3-0.1

echo "[Voice Typer] Setting up Python virtual environment..."
python3 -m venv "$SCRIPT_DIR/.venv"
"$SCRIPT_DIR/.venv/bin/pip" install faster-whisper sounddevice numpy scipy pynput pystray Pillow

echo "[Voice Typer] Adding to autostart..."
"$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/main.py" --add-to-startup

echo ""
echo "Done! Run with:"
echo "  nohup $SCRIPT_DIR/.venv/bin/python3 $SCRIPT_DIR/main.py > /dev/null 2>&1 &"
echo ""
echo "Hotkey: Ctrl+Space to start/stop recording"
