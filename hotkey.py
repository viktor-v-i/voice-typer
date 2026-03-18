import keyboard
import threading

_on_start = None
_on_stop = None
_recording = False
_lock = threading.Lock()


def _toggle():
    global _recording
    with _lock:
        if not _recording:
            _recording = True
            if _on_start:
                threading.Thread(target=_on_start, daemon=True).start()
        else:
            _recording = False
            if _on_stop:
                threading.Thread(target=_on_stop, daemon=True).start()


def start(on_start_recording, on_stop_recording):
    global _on_start, _on_stop
    _on_start = on_start_recording
    _on_stop = on_stop_recording
    keyboard.add_hotkey("ctrl+space", _toggle, suppress=True)


def stop():
    keyboard.remove_all_hotkeys()
