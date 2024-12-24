import pytest
from unittest.mock import patch, MagicMock
from do_data_utils.azure import (
    file_to_azure_storage,
    azure_storage_to_file,
    azure_storage_list_files,
)
from do_data_utils.azure.storage import initialize_storage_account


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
        connection_string = initialize_storage_account(mock_secret)


def test_file_to_azure_storage(mock_blob_service_client, mock_secret):
    mock_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value = mock_client
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

    mock_client.list_blobs.return_value = [
        mock_file1,
        mock_file2
    ]

    files = azure_storage_list_files("test_container", mock_secret)
    assert files == ["file1", "file2"]
