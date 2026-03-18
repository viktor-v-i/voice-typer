import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper's native rate

_frames = []
_stream = None


def start_recording():
    global _frames, _stream
    _frames = []

    def callback(indata, frames, time, status):
        _frames.append(indata.copy())

    _stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32", callback=callback)
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
    return audio
