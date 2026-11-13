import json
from unittest.mock import patch

from app.services import ai
from app.services.risk import get_assessment

VALID_ASSESSMENT = {
    "label": "Safe",
    "score": "Low",
    "certainty": 90,
    "reason": "No scam indicators found.",
}


def test_recovers_when_malformed_json_is_followed_by_valid_output():
    with patch(
        "app.services.risk.ask_deepseek",
        side_effect=[
            json.JSONDecodeError("Expecting value", "", 0),
            VALID_ASSESSMENT,
        ],
    ) as provider:
        result = get_assessment("untrusted sample text")

    assert provider.call_count == 2
    assert result.label == "Safe"
    assert result.score == "Low"
    assert result.certainty == 90
    assert result.reason == "No scam indicators found."


def test_malformed_json_retry_does_not_call_live_provider(mocker):
    """Ensure the retry path uses mocked output only (no get_ai_client)."""
    mocker.patch(
        "app.services.risk.ask_deepseek",
        side_effect=[
            ai.json.JSONDecodeError("bad", "", 0),
            VALID_ASSESSMENT,
        ],
    )
    client = mocker.patch("app.services.ai.get_ai_client")
    get_assessment("hello")
    client.assert_not_called()
