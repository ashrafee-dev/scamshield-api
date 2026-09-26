import os
import subprocess
import tempfile
import threading
import wave

from app.config import MAX_AUDIO_SECONDS

_model = None
_model_lock = threading.Lock()


class InvalidAudio(ValueError):
    """Audio cannot be decoded or exceeds the configured duration."""


def load_model():
    """Load lazily; health checks and text requests do not download model weights."""
    global _model  # pylint: disable=global-statement
    with _model_lock:
        if _model is None:
            import whisper  # pylint: disable=import-outside-toplevel
            _model = whisper.load_model(os.getenv("WHISPER_MODEL", "turbo"))
    return _model


def audio_transcript(audio_file: str) -> str:
    with tempfile.TemporaryDirectory(prefix="scamshield-decode-") as directory:
        output = os.path.join(directory, "audio.wav")
        try:
            subprocess.run(
                ["ffmpeg", "-nostdin", "-v", "error", "-threads", "1",
                 "-protocol_whitelist", "file,pipe", "-i", audio_file,
                 "-t", str(MAX_AUDIO_SECONDS + 1), "-vn", "-ac", "1", "-ar", "16000",
                 "-c:a", "pcm_s16le", output],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30,
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise InvalidAudio("Audio could not be decoded within the allowed time") from exc
        with wave.open(output, "rb") as audio:
            if audio.getnframes() / audio.getframerate() > MAX_AUDIO_SECONDS:
                raise InvalidAudio(f"Audio exceeds {MAX_AUDIO_SECONDS} seconds")
        text = load_model().transcribe(output, fp16=False)["text"]
        if not isinstance(text, str) or not text.strip():
            raise InvalidAudio("No speech detected")
        return text
