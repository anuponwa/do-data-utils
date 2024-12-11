import io
import itertools
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from do_data_utils.google.gcputils import (
    str_to_gcs,
    io_to_gcs,
    df_to_gcs,
    dict_to_json_gcs,
    file_to_gcs,
    upload_folder_gcs
)


def test_str_to_gcs(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_string.return_value = mock_response

    # Make a call
    gcspath = "gs://some-bucket/path/to/investigate/output.csv"
    str_to_gcs(
        "col1, col2, col3\nval1, val2, val3", gcspath=gcspath, secret=secret_json_dict
    )

    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/investigate/output.csv")
    mock_blob.upload_from_string.assert_called_once_with(
        "col1, col2, col3\nval1, val2, val3"
    )


def test_io_to_gcs(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_file.return_value = mock_response

    # Make a call
    gcspath = "gs://some-bucket/path/to/investigate/output.csv"
    io_output = io.BytesIO(b"col1, col2, col3\nval1, val2, val3")
    io_to_gcs(io_output, gcspath=gcspath, secret=secret_json_dict)

    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/investigate/output.csv")
    mock_blob.upload_from_file.assert_called_once_with(io_output)


def test_df_to_gcs_csv(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_string.return_value = mock_response

    # Try uploading...
    df_to_upload = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    gcspath = "gs://some-bucket/path/to/investigate/output.csv"
    df_to_gcs(df_to_upload, gcspath, secret_json_dict)

    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/investigate/output.csv")
    mock_blob.upload_from_string.assert_called_once_with("col1,col2\n1,4\n2,5\n3,6\n")


def test_df_to_gcs_xlsx(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_file.return_value = mock_response

    # No mock for ExcelWriter behavior

    # Try uploading...
    df_to_upload = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
    gcspath = "gs://some-bucket/path/to/investigate/output.xlsx"
    df_to_gcs(df_to_upload, gcspath, secret_json_dict)

    # Leave ExcelWriter and skip to test only the function calls to io_to_gcs

    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/investigate/output.xlsx")
    mock_blob.upload_from_file.assert_called_once()


def test_dict_to_json_gcs(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):
    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    mock_blob = MagicMock()
    mock_bucket.blob.return_value = mock_blob

    mock_response = MagicMock()
    mock_blob.upload_from_file.return_value = mock_response

    # Try uploading...
    some_dict = {"a": 1, "b": 2}
    gcspath = "gs://some-bucket/path/to/investigate/output.json"
    dict_to_json_gcs(some_dict, gcspath, secret_json_dict)

    # Skip testing for dumping json to StringIO()

    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.blob.assert_called_once_with("path/to/investigate/output.json")
    mock_blob.upload_from_file.assert_called_once()


# Test invalid inputs
@pytest.mark.parametrize(
    "param",
    [
        "somepath",
        "gs://some-bucket/path",
        "gs://some-bucket/path/file.json",
        "gs://some-bucket/path/file.txt",
    ],
)
def test_df_to_gcs_invalid_path(param, secret_json_dict):
    with pytest.raises(ValueError):
        df_to_upload = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        df_to_gcs(df_to_upload, gcspath=param, secret=secret_json_dict)


@pytest.mark.parametrize(
    "param",
    [
        "somepath",
        "gs://some-bucket/path",
        "gs://some-bucket/path/file.txt",
        "gs://some-bucket/path/file.csv",
    ],
)
def test_dict_to_json_gcs_invalid_path(param, secret_json_dict):
    with pytest.raises(ValueError):
        some_dict = {"a": 1, "b": 2}
        dict_to_json_gcs(some_dict, gcspath=param, secret=secret_json_dict)



@patch("do_data_utils.google.gcputils.io_to_gcs")
@patch("builtins.open")
def test_file_to_gcs(mock_open, mock_io_to_gcs):
    # Setup
    mock_open.return_value.__enter__.return_value.read = MagicMock(return_value=b"file content")
    
    file_path = "local_file.txt"
    gcspath = "gs://bucket/path/to/file.txt"
    
    # Call function
    file_to_gcs(file_path, gcspath)
    
    # Check if file was opened and io_to_gcs was called
    mock_open.assert_called_once_with(file_path, "rb")
    mock_io_to_gcs.assert_called_once_with(io_output=mock_open.return_value.__enter__.return_value, gcspath=gcspath, secret=None)



@patch("do_data_utils.google.gcputils.set_gcs_client")
@patch("os.walk")
@patch("os.makedirs")
def test_upload_folder_gcs(mock_makedirs, mock_os_walk, mock_set_gcs_client):
    # Setup
    mock_client = MagicMock()
    mock_set_gcs_client.return_value = mock_client
    mock_bucket = MagicMock()
    mock_client.get_bucket.return_value = mock_bucket

    mock_blob1 = MagicMock()
    mock_blob2 = MagicMock()
    mock_blob3 = MagicMock()

    mock_blobs = [mock_blob1, mock_blob2, mock_blob3]

    mock_bucket.blob.side_effect = itertools.cycle(mock_blobs)

    # Mock os.walk to simulate local directory files
    mock_os_walk.return_value = [
        ("local_dir", ["subfolder"], ["file1.txt", "file2.txt"]),
        ("local_dir/subfolder", [], ["file3.txt"]),
    ]

    local_dir = "local_dir"
    gcspath = "gs://bucket/folder/"

    # Call function
    upload_folder_gcs(local_dir, gcspath)

    # Check upload_from_filename were called
    mock_bucket.blob.assert_any_call("folder/file1.txt")
    mock_bucket.blob.assert_any_call("folder/file2.txt")
    mock_bucket.blob.assert_any_call("folder/subfolder/file3.txt")
    mock_blob1.upload_from_filename.assert_any_call("local_dir/file1.txt")
    mock_blob2.upload_from_filename.assert_any_call("local_dir/file2.txt")
    mock_blob3.upload_from_filename.assert_any_call("local_dir/subfolder/file3.txt")
