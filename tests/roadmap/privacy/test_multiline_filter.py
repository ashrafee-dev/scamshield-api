from app.services.filter import filter_sensitive


def test_multiline_redaction_preserves_newlines_and_input():
    text = (
        "Email: alice@example.com\n"
        "Phone: 555-123-4567\n"
        "SSN: 123-45-6789\n"
        "Account: 12345\n"
    )

    expected = (
        "Email: [EMAIL]\n"
        "Phone: [PHONE]\n"
        "SSN: [SSN]\n"
        "Account: [NUMBER]\n"
    )

    result = filter_sensitive(text)

    assert result == expected
    assert "\n" in result
    assert text == (
        "Email: alice@example.com\n"
        "Phone: 555-123-4567\n"
        "SSN: 123-45-6789\n"
        "Account: 12345\n"
    )


def test_repeated_sensitive_values_are_redacted():
    text = (
        "First contact: alice@example.com\n"
        "Second contact: alice@example.com\n"
        "Backup contact: bob@example.com\n"
        "Call alice@example.com again.\n"
    )

    expected = (
        "First contact: [EMAIL]\n"
        "Second contact: [EMAIL]\n"
        "Backup contact: [EMAIL]\n"
        "Call [EMAIL] again.\n"
    )

    result = filter_sensitive(text)

    assert result == expected
