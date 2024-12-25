import io
import pandas as pd
import pytest
from unittest.mock import patch, MagicMock, mock_open
from do_data_utils.azure import (
    file_to_azure_storage,
    azure_storage_to_file,
    azure_storage_list_files,
    df_to_azure_storage,
    azure_storage_to_df,
)
from do_data_utils.azure.storage import (
    get_service_client,
    io_to_azure_storage,
    azure_storage_to_io,
)


@patch("do_data_utils.azure.storage.ClientSecretCredential")
@patch("do_data_utils.azure.storage.DataLakeServiceClient")
def test_get_service_client_success(mock_service_client, mock_cred):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }

    mock_cred_instance = MagicMock()
    mock_cred.return_value = mock_cred_instance

    mock_service_client_instance = MagicMock()
    mock_service_client.return_value = mock_service_client_instance

    # Act
    result = get_service_client(secret)

    # Assert
    mock_cred.assert_called_once_with(
        tenant_id=secret["tenant_id"],
        client_id=secret["client_id"],
        client_secret=secret["client_secret"],
    )
    mock_service_client.assert_called_once_with(
        account_url=f"https://{secret['storage_account']}.dfs.core.windows.net",
        credential=mock_cred_instance,
    )
    assert result == mock_service_client_instance


def test_get_service_client_key_error():
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        # Missing "client_secret" and "storage_account"
    }

    # Act & Assert
    with pytest.raises(KeyError, match="The secret must contain .* keys."):
        get_service_client(secret)


@patch("do_data_utils.azure.storage.get_service_client")
def test_io_to_azure_storage(mock_get_service_client):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    dest_file_path = "test/path/file.txt"
    overwrite = True
    buffer = io.BytesIO(b"test data")

    mock_service_client = MagicMock()
    mock_get_service_client.return_value = mock_service_client

    mock_file_client = MagicMock()
    mock_service_client.get_file_client.return_value = mock_file_client

    # Act
    io_to_azure_storage(buffer, container_name, dest_file_path, secret, overwrite)

    # Assert
    mock_get_service_client.assert_called_once_with(secret)
    mock_service_client.get_file_client.assert_called_once_with(
        file_system=container_name, file_path=dest_file_path.lstrip("/")
    )
    buffer.seek(0)  # Reset buffer to validate position
    mock_file_client.upload_data.assert_called_once_with(buffer, overwrite=overwrite)


@patch("do_data_utils.azure.storage.get_service_client")
def test_azure_storage_to_io(mock_get_service_client):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    file_path = "test/path/file.txt"
    expected_data = b"test data"

    mock_service_client = MagicMock()
    mock_get_service_client.return_value = mock_service_client

    mock_file_client = MagicMock()
    mock_service_client.get_file_client.return_value = mock_file_client

    mock_blob_data = MagicMock()
    mock_blob_data.readall.return_value = expected_data
    mock_file_client.download_file.return_value = mock_blob_data

    # Act
    result_buffer = azure_storage_to_io(container_name, file_path, secret)

    # Assert
    mock_get_service_client.assert_called_once_with(secret)
    mock_service_client.get_file_client.assert_called_once_with(
        file_system=container_name, file_path=file_path.lstrip("/")
    )
    mock_file_client.download_file.assert_called_once()
    mock_blob_data.readall.assert_called_once()
    assert result_buffer.read() == expected_data


@patch("do_data_utils.azure.storage.get_service_client")
@patch("builtins.open", new_callable=mock_open, read_data=b"test file data")
def test_file_to_azure_storage(mock_file, mock_get_service_client):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    src_file_path = "test_file.txt"
    container_name = "test-container"
    dest_file_path = "path/to/test_file.txt"
    overwrite = True

    mock_service_client = MagicMock()
    mock_get_service_client.return_value = mock_service_client

    mock_file_client = MagicMock()
    mock_service_client.get_file_client.return_value = mock_file_client

    # Act
    file_to_azure_storage(
        src_file_path, container_name, dest_file_path, secret, overwrite
    )

    # Assert
    mock_get_service_client.assert_called_once_with(secret)
    mock_service_client.get_file_client.assert_called_once_with(
        file_system=container_name, file_path=dest_file_path.lstrip("/")
    )
    mock_file_client.upload_data.assert_called_once_with(
        mock_file.return_value, overwrite=overwrite
    )


@patch("do_data_utils.azure.storage.get_service_client")
@patch("builtins.open", new_callable=mock_open)
def test_azure_storage_to_file(mock_file, mock_get_service_client):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    file_path = "path/to/test_file.txt"
    expected_blob_data = b"test blob data"

    mock_service_client = MagicMock()
    mock_get_service_client.return_value = mock_service_client

    mock_file_client = MagicMock()
    mock_service_client.get_file_client.return_value = mock_file_client

    mock_blob_data = MagicMock()
    mock_blob_data.readall.return_value = expected_blob_data
    mock_file_client.download_file.return_value = mock_blob_data

    # Act
    azure_storage_to_file(container_name, file_path, secret)

    # Assert
    mock_get_service_client.assert_called_once_with(secret)
    mock_service_client.get_file_client.assert_called_once_with(
        file_system=container_name, file_path=file_path.lstrip("/")
    )
    mock_file_client.download_file.assert_called_once()
    mock_blob_data.readall.assert_called_once()
    mock_file.assert_called_once_with(file_path.split("/")[-1], "wb")
    mock_file.return_value.write.assert_called_once_with(expected_blob_data)


@patch("do_data_utils.azure.storage.get_service_client")
def test_azure_storage_list_files(mock_get_service_client):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    directory_path = "test/directory"
    files_only = True

    mock_service_client = MagicMock()
    mock_get_service_client.return_value = mock_service_client

    mock_file_system_client = MagicMock()
    mock_service_client.get_file_system_client.return_value = mock_file_system_client

    mock_path_1 = MagicMock()
    mock_path_1.name = "test/directory/file1.txt"
    mock_path_1.is_directory = False

    mock_path_2 = MagicMock()
    mock_path_2.name = "test/directory/subdir"
    mock_path_2.is_directory = True

    mock_path_3 = MagicMock()
    mock_path_3.name = "test/directory/file2.txt"
    mock_path_3.is_directory = False

    mock_file_system_client.get_paths.return_value = [
        mock_path_1,
        mock_path_2,
        mock_path_3,
    ]

    # Act
    result = azure_storage_list_files(
        container_name, directory_path, secret, files_only
    )

    # Assert
    mock_get_service_client.assert_called_once_with(secret)
    mock_service_client.get_file_system_client.assert_called_once_with(
        file_system=container_name
    )
    mock_file_system_client.get_paths.assert_called_once_with(path=directory_path + "/")
    assert result == ["test/directory/file1.txt", "test/directory/file2.txt"]


@patch("do_data_utils.azure.storage.get_service_client")
def test_azure_storage_list_files_include_directories(mock_get_service_client):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    directory_path = "test/directory"
    files_only = False

    mock_service_client = MagicMock()
    mock_get_service_client.return_value = mock_service_client

    mock_file_system_client = MagicMock()
    mock_service_client.get_file_system_client.return_value = mock_file_system_client

    mock_path_1 = MagicMock()
    mock_path_1.name = "test/directory/file1.txt"
    mock_path_1.is_directory = False

    mock_path_2 = MagicMock()
    mock_path_2.name = "test/directory/subdir"
    mock_path_2.is_directory = True

    mock_file_system_client.get_paths.return_value = [mock_path_1, mock_path_2]

    # Act
    result = azure_storage_list_files(
        container_name, directory_path, secret, files_only
    )

    # Assert
    mock_get_service_client.assert_called_once_with(secret)
    mock_service_client.get_file_system_client.assert_called_once_with(
        file_system=container_name
    )
    mock_file_system_client.get_paths.assert_called_once_with(path=directory_path + "/")
    assert result == ["test/directory/file1.txt", "test/directory/subdir"]


@patch("do_data_utils.azure.storage.io_to_azure_storage")
def test_df_to_azure_storage_csv(mock_io_to_azure_storage):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    container_name = "test-container"
    dest_file_path = "path/to/output.csv"
    overwrite = True

    # Act
    df_to_azure_storage(df, container_name, dest_file_path, secret, overwrite)

    # Assert
    mock_io_to_azure_storage.assert_called_once()

    # Extract buffer content
    buffer = mock_io_to_azure_storage.call_args[1][
        "buffer"
    ]  # Access keyword argument 'buffer'
    buffer.seek(0)  # Reset the buffer pointer
    assert buffer.getvalue() == "col1,col2\n1,3\n2,4\n"


@patch("do_data_utils.azure.storage.io_to_azure_storage")
def test_df_to_azure_storage_parquet(mock_io_to_azure_storage):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    container_name = "test-container"
    dest_file_path = "path/to/output.parquet"
    overwrite = True

    # Act
    df_to_azure_storage(df, container_name, dest_file_path, secret, overwrite)

    # Assert
    mock_io_to_azure_storage.assert_called_once()
    buffer = mock_io_to_azure_storage.call_args[1]["buffer"]
    buffer.seek(0)
    result_df = pd.read_parquet(buffer)
    pd.testing.assert_frame_equal(result_df, df)


@patch("do_data_utils.azure.storage.azure_storage_to_io")
def test_azure_storage_to_df_csv(mock_azure_storage_to_io):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    file_path = "path/to/input.csv"
    csv_content = "col1,col2\n1,3\n2,4\n"
    mock_azure_storage_to_io.return_value = io.BytesIO(csv_content.encode())

    # Act
    result_df = azure_storage_to_df(container_name, file_path, secret)

    # Assert
    expected_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    pd.testing.assert_frame_equal(result_df, expected_df)


@patch("do_data_utils.azure.storage.azure_storage_to_io")
def test_azure_storage_to_df_parquet(mock_azure_storage_to_io):
    # Arrange
    secret = {
        "tenant_id": "test-tenant-id",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "storage_account": "test-storage-account",
    }
    container_name = "test-container"
    file_path = "path/to/input.parquet"
    input_df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    buffer = io.BytesIO()
    input_df.to_parquet(buffer, index=False)
    buffer.seek(0)
    mock_azure_storage_to_io.return_value = buffer

    # Act
    result_df = azure_storage_to_df(container_name, file_path, secret)

    # Assert
    pd.testing.assert_frame_equal(result_df, input_df)
