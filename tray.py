from PIL import Image, ImageDraw
import pystray
import threading

_tray_icon = None
_recording = False


def _make_icon(recording=False):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    color = (220, 50, 50) if recording else (120, 120, 120)

    # Mic body (rounded rectangle)
    draw.rounded_rectangle([22, 4, 42, 38], radius=10, fill=color)

    # Mic stand arc
    draw.arc([14, 24, 50, 52], start=0, end=180, fill=color, width=4)

    # Mic stand stem
    draw.line([32, 52, 32, 60], fill=color, width=4)

    # Mic base
    draw.line([22, 60, 42, 60], fill=color, width=4)

    return img


def _build_menu(quit_callback):
    return pystray.Menu(
        pystray.MenuItem("Voice Typer", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_callback),
    )


def start(quit_callback):
    global _tray_icon
    icon_img = _make_icon(recording=False)
    _tray_icon = pystray.Icon(
        "voice-typer",
        icon_img,
        "Voice Typer - idle (Ctrl+Space to record)",
        menu=_build_menu(quit_callback),
    )
    # Run in a background thread so it doesn't block main
    t = threading.Thread(target=_tray_icon.run, daemon=True)
    t.start()


def set_recording(recording: bool):
    global _recording
    _recording = recording
    if _tray_icon:
        _tray_icon.icon = _make_icon(recording=recording)
        _tray_icon.title = (
            "Voice Typer - RECORDING (press Ctrl+Space to stop)"
            if recording
            else "Voice Typer - idle (Ctrl+Space to record)"
        )


def stop():
    if _tray_icon:
        _tray_icon.stop()
