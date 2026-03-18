import pyautogui
import time

# Small delay between keystrokes (seconds). Lower = faster but less reliable.
TYPING_INTERVAL = 0.01


def type_text(text):
    if not text:
        return
    # Give focus a moment to settle before typing
    time.sleep(0.1)
    pyautogui.typewrite(text, interval=TYPING_INTERVAL)
    # typewrite doesn't handle unicode well — fall back to clipboard paste for non-ASCII
    # (handled in type_text_unicode below)


def type_text_unicode(text):
    """Use clipboard paste for text with special/unicode characters."""
    import pyperclip
    import pyautogui
    if not text:
        return
    time.sleep(0.1)
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
