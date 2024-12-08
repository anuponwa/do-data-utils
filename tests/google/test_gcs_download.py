import io
import pandas as pd
import pytest
from unittest.mock import MagicMock
from do_data_utils.google import gcs_to_df, gcs_to_dict


def test_gcs_csv_to_df_pandas(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob


    # Mock the download_to_file method to write to the byte stream
    mock_byte_stream = io.BytesIO(b'Test, value\ntest1, value1')

    def mock_download_to_file(file_obj):
        file_obj.write(mock_byte_stream.getvalue())
    
    mock_blob.download_to_file.side_effect = mock_download_to_file

    # Tests...
    gcspath = 'gs://some-bucket/path/to/file.csv'
    results = gcs_to_df(gcspath=gcspath, secret=secret_json_dict, polars=False)

    assert isinstance(results, pd.DataFrame)
    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/file.csv')


@pytest.mark.parametrize('input', ['somepath.csv', 'gs://somepath.json'])
def test_gcs_to_df_invalid_path(input, secret_json_dict):
    with pytest.raises(ValueError):
        _ = gcs_to_df(input, secret=secret_json_dict)


def test_gcs_to_dict(mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict):
    
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob


    # Mock the download_to_file method to write to the byte stream
    mock_byte_stream = io.BytesIO(b'{"Some key": "Some value", "Another key": 42}')

    def mock_download_to_file(file_obj):
        file_obj.write(mock_byte_stream.getvalue())
    
    mock_blob.download_to_file.side_effect = mock_download_to_file

    # Tests...
    gcspath = 'gs://some-bucket/path/to/example.json'
    results = gcs_to_dict(gcspath=gcspath, secret=secret_json_dict)

    assert isinstance(results, dict)
    mock_gcs_client.get_bucket.assert_called_once_with('some-bucket')
    mock_bucket.blob.assert_called_once_with('path/to/example.json')


