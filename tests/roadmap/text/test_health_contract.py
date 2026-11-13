"""Contract test for the public /health liveness endpoint (issue #34)."""


def test_health_is_public_and_cheap(client, mocker):
    client.headers.pop("Authorization")
    rate_limit_check = mocker.patch("app.services.rate_limit.check_rate_limit")
    redis_ping = mocker.patch("app.services.rate_limit.r.ping")
    provider_call = mocker.patch("app.services.risk.ask_deepseek")
    assessment = mocker.patch("app.api.analyze.get_assessment")

    response = client.get("/health")

    assert "Authorization" not in response.request.headers
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    rate_limit_check.assert_not_called()
    redis_ping.assert_not_called()
    provider_call.assert_not_called()
    assessment.assert_not_called()
