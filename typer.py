import sys
import time


if sys.platform == "win32":
    import pyperclip
    import pyautogui

    def type_text_unicode(text):
        """Use clipboard paste for text with special/unicode characters."""
        if not text:
            return
        time.sleep(0.1)
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")

else:
    import subprocess

    def type_text_unicode(text):
        """Type text into the active window using xdotool."""
        if not text:
            return
        time.sleep(0.3)
        subprocess.run(["xdotool", "type", "--clearmodifiers", "--delay", "12", text], check=True)
