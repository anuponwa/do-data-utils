import io
import pandas as pd
import polars as pl
import pytest
from unittest.mock import patch, MagicMock
from do_data_utils.google import (
    gcs_to_df,
    gcs_to_dict,
    gcs_to_file,
    download_folder_gcs,
)


def test_gcs_csv_to_df_pandas(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):

    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    # Mock the download_to_file method to write to the byte stream
    mock_byte_stream = io.BytesIO(b"Test, value\ntest1, value1")

    def mock_download_to_file(file_obj):
        file_obj.write(mock_byte_stream.getvalue())

    mock_blob.download_to_file.side_effect = mock_download_to_file

    # Tests...
    gcspath = "gs://some-bucket/path/to/file.csv"
    results = gcs_to_df(gcspath=gcspath, secret=secret_json_dict, polars=False)

    assert isinstance(results, pd.DataFrame)
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/file.csv")


def test_gcs_csv_to_df_polars(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):

    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    # Mock the download_to_file method to write to the byte stream
    mock_byte_stream = io.BytesIO(b"Test, value\ntest1, value1")

    def mock_download_to_file(file_obj):
        file_obj.write(mock_byte_stream.getvalue())

    mock_blob.download_to_file.side_effect = mock_download_to_file

    # Tests...
    gcspath = "gs://some-bucket/path/to/file.csv"
    results = gcs_to_df(gcspath=gcspath, secret=secret_json_dict, polars=True)

    assert isinstance(results, pl.DataFrame)
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/file.csv")


@pytest.mark.parametrize("input", ["somepath.csv", "gs://somepath.json"])
def test_gcs_to_df_invalid_path(input, secret_json_dict):
    with pytest.raises(ValueError):
        _ = gcs_to_df(input, secret=secret_json_dict)


def test_gcs_to_dict(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):

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
    gcspath = "gs://some-bucket/path/to/example.json"
    results = gcs_to_dict(gcspath=gcspath, secret=secret_json_dict)

    assert isinstance(results, dict)
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/example.json")


def test_gcs_csv_to_df_pandas_empty_secret(
    mock_gcs_client, mock_gcs_service_account_credentials
):

    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    # Mock the download_to_file method to write to the byte stream
    mock_byte_stream = io.BytesIO(b"Test, value\ntest1, value1")

    def mock_download_to_file(file_obj):
        file_obj.write(mock_byte_stream.getvalue())

    mock_blob.download_to_file.side_effect = mock_download_to_file

    # Tests...
    gcspath = "gs://some-bucket/path/to/file.csv"
    results = gcs_to_df(gcspath=gcspath, secret=None, polars=False)

    assert isinstance(results, pd.DataFrame)
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/file.csv")


@patch("do_data_utils.google.gcputils.gcs_to_io")
@patch("builtins.open")
def test_gcs_to_file(mock_open, mock_gcs_to_io):
    # Setup
    mock_gcs_to_io.return_value.read.return_value = b"some content"
    mock_open.return_value.__enter__.return_value.write = MagicMock()

    gcspath = "gs://bucket/path/to/file.txt"

    # Call function
    gcs_to_file(gcspath)

    # Check if open was called with the correct file name and if content was written
    mock_open.assert_called_once_with("file.txt", "wb")
    mock_open.return_value.__enter__.return_value.write.assert_called_once_with(
        b"some content"
    )


@patch("do_data_utils.google.gcputils.set_gcs_client")
@patch("os.makedirs")
def test_download_folder_gcs(mock_makedirs, mock_set_gcs_client):
    # Setup
    mock_client = MagicMock()
    mock_set_gcs_client.return_value = mock_client
    mock_bucket = MagicMock()
    mock_client.get_bucket.return_value = mock_bucket
    
    # Mock Blob object
    mock_blob1 = MagicMock()
    mock_blob2 = MagicMock()

    mock_blob1.name = "folder/file.txt"
    mock_blob2.name = "folder/sub-folder/file2.txt"
    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]

    gcspath = "gs://bucket/folder/"
    local_dir = "local_dir"
    
    # Call function
    download_folder_gcs(gcspath, local_dir)
    
    # Ensure download_to_filename was called
    mock_blob1.download_to_filename.assert_called_once_with("local_dir/file.txt")
    mock_blob2.download_to_filename.assert_called_once_with("local_dir/sub-folder/file2.txt")
