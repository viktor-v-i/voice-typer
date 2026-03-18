from pynput import keyboard

_listener = None
_on_start = None
_on_stop = None
_recording = False
_ctrl_held = False


def _on_press(key):
    global _recording, _ctrl_held
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        _ctrl_held = True
    if key == keyboard.Key.space and _ctrl_held:
        if not _recording:
            _recording = True
            if _on_start:
                _on_start()
        else:
            _recording = False
            if _on_stop:
                _on_stop()


def _on_release(key):
    global _ctrl_held
    if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
        _ctrl_held = False


def start(on_start_recording, on_stop_recording):
    global _listener, _on_start, _on_stop
    _on_start = on_start_recording
    _on_stop = on_stop_recording

    _listener = keyboard.Listener(on_press=_on_press, on_release=_on_release, suppress=False)
    _listener.start()


def stop():
    global _listener
    if _listener:
        _listener.stop()
        _listener = None
