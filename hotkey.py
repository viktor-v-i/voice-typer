import sys
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


if sys.platform == "win32":
    import keyboard

    def start(on_start_recording, on_stop_recording):
        global _on_start, _on_stop
        _on_start = on_start_recording
        _on_stop = on_stop_recording
        keyboard.add_hotkey("ctrl+space", _toggle, suppress=True)

    def stop():
        keyboard.remove_all_hotkeys()

else:
    from pynput import keyboard as pynput_kb

    _ctrl_held = False
    _listener = None

    def _on_press(key):
        global _ctrl_held
        if key in (pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r):
            _ctrl_held = True
        if key == pynput_kb.Key.space and _ctrl_held:
            _toggle()

    def _on_release(key):
        global _ctrl_held
        if key in (pynput_kb.Key.ctrl_l, pynput_kb.Key.ctrl_r):
            _ctrl_held = False

    def start(on_start_recording, on_stop_recording):
        global _on_start, _on_stop, _listener
        _on_start = on_start_recording
        _on_stop = on_stop_recording
        _listener = pynput_kb.Listener(on_press=_on_press, on_release=_on_release)
        _listener.start()

    def stop():
        global _listener
        if _listener:
            _listener.stop()
            _listener = None
