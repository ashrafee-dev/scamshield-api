import subprocess
import wave
from pathlib import Path

import pytest

from app.services import transcription


def test_decoder_timeout_is_controlled(mocker):
    mocker.patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ffmpeg", 30))
    with pytest.raises(transcription.InvalidAudio, match="allowed time"):
        transcription.audio_transcript("audio.m4a")


def test_duration_limit_precedes_model_inference(mocker):
    paths = []

    def decode(command, **_kwargs):
        paths.append(command[-1])
        with wave.Wave_write(command[-1]) as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(16000)
            output.writeframes(b"\0\0" * 16000 * 2)

    mocker.patch.object(transcription, "MAX_AUDIO_SECONDS", 1)
    mocker.patch("subprocess.run", side_effect=decode)
    model = mocker.patch.object(transcription, "load_model")
    with pytest.raises(transcription.InvalidAudio, match="exceeds"):
        transcription.audio_transcript("audio.m4a")
    model.assert_not_called()
    assert all(not Path(path).parent.exists() for path in paths)

def _decode_wav(frames: int):
    def decode(command, **_kwargs):
        with wave.Wave_write(command[-1]) as output:
            output.setnchannels(1)
            output.setsampwidth(2)
            output.setframerate(16000)
            output.writeframes(bytes(frames * 2))

    return decode


def test_audio_exactly_at_the_duration_limit_is_accepted(mocker):
    mocker.patch.object(transcription, "MAX_AUDIO_SECONDS", 2)
    mocker.patch("subprocess.run", side_effect=_decode_wav(16000 * 2))
    model = mocker.patch.object(transcription, "load_model")
    model.return_value.transcribe.return_value = {"text": "hello"}

    assert transcription.audio_transcript("audio.m4a") == "hello"
    model.assert_called_once()


def test_audio_one_frame_over_the_duration_limit_is_rejected(mocker):
    mocker.patch.object(transcription, "MAX_AUDIO_SECONDS", 2)
    mocker.patch("subprocess.run", side_effect=_decode_wav(16000 * 2 + 1))
    model = mocker.patch.object(transcription, "load_model")

    with pytest.raises(transcription.InvalidAudio, match="exceeds"):
        transcription.audio_transcript("audio.m4a")
    model.assert_not_called()
