import pytest
from do_data_utils.preprocessing import clean_phone


def test_valid_phone():
    phone = '090-123-4567|0912345678|0901234567-9'
    expected_all_nums = '0901234567|0912345678|0901234567|0901234568|0901234569'
    phone_str_clean = clean_phone(phone, exclude_numbers=[])
    cleaned_phones = set(phone_str_clean.split('|'))
    expected_phones = set(expected_all_nums.split('|'))
    assert cleaned_phones == expected_phones


@pytest.mark.parametrize('input, expected', [
    ('', None),
    (0, None),
    ([], None),
    ('000', None)
])
def test_none_phones(input, expected):
    assert clean_phone(input) == expected


def test_invalid_exclude_phones():
    with pytest.raises(ValueError):
        _ = clean_phone('0123141', exclude_numbers='0123141')
