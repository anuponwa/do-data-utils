import pytest
from do_data_utils.preprocessing import clean_email

@pytest.mark.parametrize(
    'input, expected', [
        ('anuponwa@scg.com', 'anuponwa@scg.com'),
        ('anuponwa', None)
    ]
)
def test_email(input, expected):
    assert clean_email(input) == expected
