import sys
import numpy as np
import sounddevice as sd

WHISPER_RATE = 16000  # Whisper's native rate

_frames = []
_stream = None
_native_rate = None


def _get_native_rate():
    device_info = sd.query_devices(kind="input")
    return int(device_info["default_samplerate"])


def start_recording():
    global _frames, _stream, _native_rate
    _frames = []

    if sys.platform == "win32":
        _native_rate = WHISPER_RATE
    else:
        _native_rate = _get_native_rate()

    def callback(indata, frames, time, status):
        _frames.append(indata.copy())

    _stream = sd.InputStream(samplerate=_native_rate, channels=1, dtype="float32", callback=callback)
    _stream.start()


def stop_recording():
    global _stream
    if _stream is not None:
        _stream.stop()
        _stream.close()
        _stream = None

    if not _frames:
        return None

    audio = np.concatenate(_frames, axis=0).flatten()

    if _native_rate != WHISPER_RATE:
        from scipy.signal import resample
        num_samples = int(len(audio) * WHISPER_RATE / _native_rate)
        audio = resample(audio, num_samples).astype(np.float32)

    return audio
