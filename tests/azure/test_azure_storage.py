import io
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from do_data_utils.azure import (
    file_to_azure_storage,
    azure_storage_to_file,
    azure_storage_list_files,
    df_to_azure_storage,
    azure_storage_to_df,
)
from do_data_utils.azure.storage import (
    initialize_storage_account,
    io_to_azure_storage,
    azure_storage_to_io,
)


# Fixtures
@pytest.fixture
def mock_secret():
    return {"accountName": "test_account", "key": "test_key"}


@pytest.fixture
def mock_blob_service_client():
    with patch("do_data_utils.azure.storage.BlobServiceClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_container_client():
    with patch("do_data_utils.azure.storage.ContainerClient") as mock_client:
        yield mock_client


# Tests
def test_initialize_storage_account_valid_secret(mock_secret):
    connection_string = initialize_storage_account(mock_secret)
    assert "AccountName=test_account" in connection_string
    assert "AccountKey=test_key" in connection_string


def test_initialize_storage_account_missing_key(mock_secret):
    del mock_secret["key"]
    with pytest.raises(KeyError):
        _ = initialize_storage_account(mock_secret)


@patch("builtins.open")
def test_file_to_azure_storage(mock_open, mock_blob_service_client, mock_secret):
    mock_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value = mock_client
    mock_open.return_value.__enter__.return_value.read = MagicMock(
        return_value=b"file content"
    )

    file_to_azure_storage(
        "test_file.txt", "test_container", "path", "file.txt", mock_secret
    )
    mock_client.get_blob_client.assert_called_once()


def test_azure_storage_to_file(mock_blob_service_client, mock_secret):
    mock_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value = mock_client
    mock_blob = mock_client.get_blob_client.return_value
    mock_blob.download_blob.return_value.readall.return_value = b"data"

    azure_storage_to_file("test_container", "path", "file.txt", mock_secret)
    mock_blob.download_blob.assert_called_once()


def test_azure_storage_list_files(mock_container_client, mock_secret):
    mock_client = MagicMock()
    mock_container_client.from_connection_string.return_value = mock_client

    mock_file1 = MagicMock()
    mock_file1.name = "file1"
    mock_file2 = MagicMock()
    mock_file2.name = "file2"

    mock_client.list_blobs.return_value = [mock_file1, mock_file2]

    files = azure_storage_list_files("test_container", mock_secret)
    assert files == ["file1", "file2"]


# Test IO and DataFrames

MOCK_SECRET = {"accountName": "mockaccount", "key": "mockkey"}

# Mock data for testing
MOCK_DF = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
MOCK_PARQUET_FILE = "mock_data.parquet"
MOCK_CSV_FILE = "mock_data.csv"
MOCK_CONTAINER = "mock-container"
MOCK_BLOB_PATH = "mock/path"
MOCK_FILE_NAME = "mock_file"


@patch("do_data_utils.azure.storage.BlobServiceClient")
def test_io_to_azure_storage(mock_blob_service_client):
    mock_buffer = io.BytesIO(b"mock data")
    mock_blob_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    io_to_azure_storage(
        buffer=mock_buffer,
        container_name=MOCK_CONTAINER,
        dest_blob_path=MOCK_BLOB_PATH,
        dest_file_name=MOCK_FILE_NAME,
        secret=MOCK_SECRET,
    )

    # Assertions
    mock_blob_service_client.from_connection_string.assert_called_once()
    mock_blob_client.upload_blob.assert_called_once_with(mock_buffer, overwrite=True)


@patch("do_data_utils.azure.storage.BlobServiceClient")
def test_azure_storage_to_io(mock_blob_service_client):
    mock_blob_data = io.BytesIO(b"mock data")
    mock_blob_client = MagicMock()
    mock_blob_client.download_blob.return_value.readall.return_value = (
        mock_blob_data.getvalue()
    )
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    buffer = azure_storage_to_io(
        container_name=MOCK_CONTAINER,
        src_blob_path=MOCK_BLOB_PATH,
        src_file_name=MOCK_FILE_NAME,
        secret=MOCK_SECRET,
    )

    # Assertions
    mock_blob_service_client.from_connection_string.assert_called_once()
    mock_blob_client.download_blob.assert_called_once()
    assert buffer.read() == b"mock data"


@patch("do_data_utils.azure.storage.io_to_azure_storage")
def test_df_to_azure_storage_parquet(mock_io_to_azure_storage):
    buffer = io.BytesIO()
    MOCK_DF.to_parquet(buffer)
    buffer.seek(0)

    df_to_azure_storage(
        df=MOCK_DF,
        container_name=MOCK_CONTAINER,
        dest_blob_path=MOCK_BLOB_PATH,
        dest_file_name="mock_data.parquet",
        secret=MOCK_SECRET,
    )

    # Assertions
    mock_io_to_azure_storage.assert_called_once()


@patch("do_data_utils.azure.storage.io_to_azure_storage")
def test_df_to_azure_storage_csv(mock_io_to_azure_storage):
    buffer = io.StringIO()
    MOCK_DF.to_csv(buffer, index=False)
    buffer.seek(0)

    df_to_azure_storage(
        df=MOCK_DF,
        container_name=MOCK_CONTAINER,
        dest_blob_path=MOCK_BLOB_PATH,
        dest_file_name="mock_data.csv",
        secret=MOCK_SECRET,
    )

    # Assertions
    mock_io_to_azure_storage.assert_called_once()


@patch("do_data_utils.azure.storage.azure_storage_to_io")
def test_azure_storage_to_df_parquet_with_pandas(mock_azure_storage_to_io):
    buffer = io.BytesIO()
    MOCK_DF.to_parquet(buffer)
    buffer.seek(0)
    mock_azure_storage_to_io.return_value = buffer

    df = azure_storage_to_df(
        container_name=MOCK_CONTAINER,
        src_blob_path=MOCK_BLOB_PATH,
        src_file_name="mock_data.parquet",
        secret=MOCK_SECRET,
        polars=False,
    )

    # Assertions
    pd.testing.assert_frame_equal(df, MOCK_DF)


@patch("do_data_utils.azure.storage.azure_storage_to_io")
def test_azure_storage_to_df_csv_with_pandas(mock_azure_storage_to_io):
    buffer = io.StringIO()
    MOCK_DF.to_csv(buffer, index=False)
    buffer.seek(0)
    mock_azure_storage_to_io.return_value = io.BytesIO(buffer.getvalue().encode())

    df = azure_storage_to_df(
        container_name=MOCK_CONTAINER,
        src_blob_path=MOCK_BLOB_PATH,
        src_file_name="mock_data.csv",
        secret=MOCK_SECRET,
        polars=False,
    )

    # Assertions
    pd.testing.assert_frame_equal(df, MOCK_DF)


@patch("do_data_utils.azure.storage.pl.read_csv")
@patch("do_data_utils.azure.storage.azure_storage_to_io")
def test_azure_storage_to_df_csv_with_polars(mock_azure_storage_to_io, mock_pl):
    buffer = io.StringIO()
    MOCK_DF.to_csv(buffer, index=False)
    buffer.seek(0)
    mock_azure_storage_to_io.return_value = io.BytesIO(buffer.getvalue().encode())

    _ = azure_storage_to_df(
        container_name=MOCK_CONTAINER,
        src_blob_path=MOCK_BLOB_PATH,
        src_file_name="mock_data.csv",
        secret=MOCK_SECRET,
        polars=True,
    )

    # Assertions
    # Check what was passed to `pl.read_csv`
    called_args, _ = mock_pl.call_args
    actual_buffer = called_args[
        0
    ]  # The first positional argument passed to `pl.read_csv`

    # Rewind the buffer for comparison (if necessary)
    actual_buffer.seek(0)
    expected_buffer = io.StringIO(buffer.getvalue())

    assert actual_buffer.read() == expected_buffer.read()
    assert mock_pl.call_count == 1
    assert (
        len(mock_pl.call_args_list) == 1
    )  # Expected polars.read_csv to be called once.
