import pytest

from app.services.filter import filter_sensitive


@pytest.mark.parametrize(
    "text",
    [
        "The morning market was quiet, bright, and welcoming.",
        "Please leave the blue notebook beside the window.",
        "A careful description can include commas, dashes, and parentheses.",
        "Nothing unusual happened during the short walk through the garden.",
    ],
)
def test_benign_prose_is_preserved(text):
    assert filter_sensitive(text) == text
