from unittest.mock import patch
import pytest

from app.services.risk import get_assessment, AssessmentUnavailable


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


def test_get_assessment_raises_after_bounded_attempts_fail():
    with patch(
        "app.services.risk.ask_deepseek",
        return_value=INVALID_RESPONSE,
    ) as mock_ask:
        with pytest.raises(AssessmentUnavailable):
            get_assessment("test transcription")

    assert mock_ask.call_count == 2
