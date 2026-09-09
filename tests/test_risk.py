import os

os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

from unittest.mock import patch

from app.services.risk import get_assessment


VALID_RESPONSE = {
    "label": "Safe",
    "score": "Low",
    "certainty": 90,
    "reason": "No scam indicators found.",
}

INVALID_RESPONSE = {
    "label": "Invalid Label",
}


def test_get_assessment_retries_after_invalid_response():
    with patch(
        "app.services.risk.ask_deepseek",
        side_effect=[INVALID_RESPONSE, VALID_RESPONSE],
    ) as mock_ask:
        result = get_assessment("test transcription")

    assert result is not None
    assert result.label == "Safe"
    assert result.score == "Low"
    assert result.certainty == 90
    assert result.reason == "No scam indicators found."
    assert mock_ask.call_count == 2


def test_get_assessment_returns_none_after_all_attempts_fail():
    with patch(
        "app.services.risk.ask_deepseek",
        return_value=INVALID_RESPONSE,
    ) as mock_ask:
        result = get_assessment("test transcription")

    assert result is None
    assert mock_ask.call_count == 5