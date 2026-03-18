import sys
import os
import threading
import time

import recorder
import transcriber
import typer as typer_mod
import hotkey
import tray


def on_start_recording():
    print("[Voice Typer] Recording started...")
    tray.set_recording(True)
    recorder.start_recording()


def on_stop_recording():
    print("[Voice Typer] Recording stopped. Transcribing...")
    tray.set_recording(False)
    audio = recorder.stop_recording()

    if audio is None or len(audio) < 1600:  # less than 0.1s of audio
        print("[Voice Typer] No audio captured.")
        return

    def transcribe_and_type():
        text = transcriber.transcribe(audio)
        print(f"[Voice Typer] Transcribed: {text!r}")
        if text:
            typer_mod.type_text_unicode(text)

    threading.Thread(target=transcribe_and_type, daemon=True).start()


def quit_app(icon=None, item=None):
    print("[Voice Typer] Quitting...")
    hotkey.stop()
    tray.stop()
    sys.exit(0)


def add_to_startup():
    if sys.platform == "win32":
        import winreg
        script_path = os.path.abspath(__file__)
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        cmd = f'"{pythonw}" "{script_path}"'
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "VoiceTyper", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)
        print(f"[Voice Typer] Added to Windows startup: {cmd}")
    else:
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        script_path = os.path.abspath(__file__)
        venv_python = os.path.join(os.path.dirname(script_path), ".venv", "bin", "python3")
        python_exec = venv_python if os.path.exists(venv_python) else "python3"
        desktop_entry = f"""[Desktop Entry]
Type=Application
Name=Voice Typer
Exec={python_exec} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        path = os.path.join(autostart_dir, "voice-typer.desktop")
        with open(path, "w") as f:
            f.write(desktop_entry)
        print(f"[Voice Typer] Added to autostart: {path}")


def remove_from_startup():
    if sys.platform == "win32":
        import winreg
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            winreg.DeleteValue(key, "VoiceTyper")
            winreg.CloseKey(key)
            print("[Voice Typer] Removed from Windows startup.")
        except FileNotFoundError:
            print("[Voice Typer] Not in startup registry.")
    else:
        path = os.path.expanduser("~/.config/autostart/voice-typer.desktop")
        if os.path.exists(path):
            os.remove(path)
            print(f"[Voice Typer] Removed from autostart: {path}")
        else:
            print("[Voice Typer] Not in autostart.")


if __name__ == "__main__":
    if "--add-to-startup" in sys.argv:
        add_to_startup()
        sys.exit(0)

    if "--remove-from-startup" in sys.argv:
        remove_from_startup()
        sys.exit(0)

    print("[Voice Typer] Loading Whisper model...")
    transcriber.load_model()

    print("[Voice Typer] Starting. Press Ctrl+Space to record, Ctrl+Space again to stop.")
    tray.start(quit_callback=quit_app)
    hotkey.start(on_start_recording, on_stop_recording)

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        quit_app()
