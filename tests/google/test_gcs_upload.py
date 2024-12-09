import io
import pandas as pd
import pytest
from unittest.mock import MagicMock
from do_data_utils.google.gcputils import str_to_gcs, io_to_gcs, df_to_gcs, dict_to_json_gcs


def test_str_to_gcs(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_string.return_value = mock_response

    # Make a call
    gcspath = 'gs://some-bucket/path/to/investigate/output.csv'
    str_to_gcs('col1, col2, col3\nval1, val2, val3', gcspath=gcspath, secret=secret_json_dict)

    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/investigate/output.csv')
    mock_blob.upload_from_string.assert_called_once_with('col1, col2, col3\nval1, val2, val3')


def test_io_to_gcs(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_file.return_value = mock_response

    # Make a call
    gcspath = 'gs://some-bucket/path/to/investigate/output.csv'
    io_output = io.BytesIO(b'col1, col2, col3\nval1, val2, val3')
    io_to_gcs(io_output, gcspath=gcspath, secret=secret_json_dict)

    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/investigate/output.csv')
    mock_blob.upload_from_file.assert_called_once_with(io_output)


def test_df_to_gcs_csv(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_string.return_value = mock_response

    # Try uploading...
    df_to_upload = pd.DataFrame({'col1': [1,2,3], 'col2': [4,5,6]})
    gcspath = 'gs://some-bucket/path/to/investigate/output.csv'
    df_to_gcs(df_to_upload, gcspath, secret_json_dict)

    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/investigate/output.csv')
    mock_blob.upload_from_string.assert_called_once_with('col1,col2\n1,4\n2,5\n3,6\n')


def test_df_to_gcs_xlsx(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_file.return_value = mock_response

    # No mock for ExcelWriter behavior

    # Try uploading...
    df_to_upload = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    gcspath = 'gs://some-bucket/path/to/investigate/output.xlsx'
    df_to_gcs(df_to_upload, gcspath, secret_json_dict)

    # Leave ExcelWriter and skip to test only the function calls to io_to_gcs

    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/investigate/output.xlsx')
    mock_blob.upload_from_file.assert_called_once()


def test_dict_to_json_gcs(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_file.return_value = mock_response


    # Try uploading...
    some_dict = {'a': 1, 'b': 2}
    gcspath = 'gs://some-bucket/path/to/investigate/output.json'
    dict_to_json_gcs(some_dict, gcspath, secret_json_dict)

    # Skip testing for dumping json to StringIO()

    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/investigate/output.json')
    mock_blob.upload_from_file.assert_called_once()


# Test invalid inputs
@pytest.mark.parametrize('param', [
    'somepath', 'gs://some-bucket/path', 'gs://some-bucket/path/file.json', 'gs://some-bucket/path/file.txt'
])
def test_df_to_gcs_invalid_path(param, secret_json_dict):
    with pytest.raises(ValueError):
        df_to_upload = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        df_to_gcs(df_to_upload, gcspath=param, secret=secret_json_dict)


@pytest.mark.parametrize('param', [
    'somepath', 'gs://some-bucket/path', 'gs://some-bucket/path/file.txt', 'gs://some-bucket/path/file.csv'
])
def test_dict_to_json_gcs_invalid_path(param, secret_json_dict):
    with pytest.raises(ValueError):
        some_dict = {'a': 1, 'b': 2}
        dict_to_json_gcs(some_dict, gcspath=param, secret=secret_json_dict)
