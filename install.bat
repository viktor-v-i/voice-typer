@echo off
echo [Voice Typer] Installing dependencies...
pip install -r requirements.txt

echo.
echo [Voice Typer] Adding to Windows startup...
python main.py --add-to-startup

echo.
echo [Voice Typer] Done! Run "python main.py" to start now.
echo Press Caps Lock to record, Caps Lock again to stop and type.
pause
