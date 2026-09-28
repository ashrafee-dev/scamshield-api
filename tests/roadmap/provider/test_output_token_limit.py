from unittest.mock import MagicMock

from app.services import ai


def _mock_client(mocker):
    client = MagicMock()
    client.chat.completions.create.return_value.choices[0].message.content = '{"label":"Safe"}'
    mocker.patch("app.services.ai.get_ai_client", return_value=client)
    return client


def test_requests_a_bounded_positive_output_budget(mocker):
    client = _mock_client(mocker)

    ai.ask_deepseek("some untrusted text")

    max_tokens = client.chat.completions.create.call_args.kwargs["max_tokens"]
    assert isinstance(max_tokens, int)
    assert 0 < max_tokens <= 4096


def test_requests_json_object_response_format(mocker):
    client = _mock_client(mocker)

    ai.ask_deepseek("some untrusted text")

    response_format = client.chat.completions.create.call_args.kwargs["response_format"]
    assert response_format == {"type": "json_object"}
