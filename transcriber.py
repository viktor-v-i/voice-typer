from faster_whisper import WhisperModel

MODEL_SIZE = "small"  # Options: tiny, base, small, medium, large

_model = None


def load_model():
    global _model
    print(f"Loading Whisper '{MODEL_SIZE}' model (downloads ~244MB on first run)...")
    _model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    print("Model ready.")


def transcribe(audio_array):
    if _model is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    segments, _ = _model.transcribe(audio_array, beam_size=5, language="en")
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()
