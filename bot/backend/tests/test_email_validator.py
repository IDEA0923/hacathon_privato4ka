import pytest

from app.utils.validators import normalize_email


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("user@example.com", "user@example.com"),
        ("  User@Example.COM  ".strip(), "User@example.com"),
    ],
)
def test_normalize_email_valid(raw: str, expected: str) -> None:
    assert normalize_email(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "not-an-email", "user@", "@example.com", "user@@example.com"],
)
def test_normalize_email_invalid(raw: str) -> None:
    with pytest.raises(ValueError):
        normalize_email(raw)
