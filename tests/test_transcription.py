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
