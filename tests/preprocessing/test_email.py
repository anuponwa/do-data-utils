import pytest
from do_data_utils.preprocessing import clean_email


@pytest.mark.parametrize(
    "input, expected", [("anuponwa@scg.com", "anuponwa@scg.com"), ("anuponwa", None)]
)
def test_email(input, expected):
    assert clean_email(input) == expected


def test_empty_email():
    assert clean_email("") is None


@pytest.mark.parametrize(
    "input, expected",
    [
        ("anuponwa@scg.com|", "anuponwa@scg.com"),
        (
            "anuponwa@scg.com|xxx@xy|someone@domain.com",
            "anuponwa@scg.com|someone@domain.com",
        ),
        ("anuponwa", None),
    ],
)
def test_multiple_emails(input, expected):
    assert clean_email(input, delimiter="|") == expected
