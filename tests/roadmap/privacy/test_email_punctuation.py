import pytest

from app.services.filter import filter_sensitive


def test_plus_alias_email_is_redacted():
    assert filter_sensitive("john+work@gmail.com") == "[EMAIL]"


def test_subdomain_email_is_redacted():
    assert filter_sensitive("john@mail.company.com") == "[EMAIL]"


def test_uppercase_email_is_redacted():
    assert filter_sensitive("JOHN@GMAIL.COM") == "[EMAIL]"


@pytest.mark.parametrize("punctuation", [",", ".", "!"])
def test_email_followed_by_punctuation_is_redacted(punctuation):
    text = f"john@gmail.com{punctuation}"

    assert filter_sensitive(text) == f"[EMAIL]{punctuation}"


def test_email_redaction_preserves_surrounding_prose():
    text = "Contact john@gmail.com for help."

    assert filter_sensitive(text) == "Contact [EMAIL] for help."
