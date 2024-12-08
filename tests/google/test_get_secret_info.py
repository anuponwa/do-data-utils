import pytest
from unittest.mock import mock_open, patch
from do_data_utils.google.common import get_secret_info



def test_read_json_valid(secret_json_content, secret_json_dict):
    mock_file_content = secret_json_content
    mock_open_obj = mock_open(read_data=mock_file_content)

    with patch('builtins.open', mock_open_obj):
        result_dict = get_secret_info('path_to_my_secret.json')

    assert isinstance(result_dict, dict)
    assert result_dict==secret_json_dict
    mock_open_obj.assert_called_once_with('path_to_my_secret.json', 'r')


def test_get_valid_secret_dict(secret_json_dict):
    result = get_secret_info(secret_json_dict)
    assert result == secret_json_dict


def test_get_secret_invalid_type():
    with pytest.raises(ValueError):
        _ = get_secret_info(42)


def test_get_secret_invalid_not_json_file():
    with pytest.raises(ValueError):
        _ = get_secret_info('path_to_some_file.csv')