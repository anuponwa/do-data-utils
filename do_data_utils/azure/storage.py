# from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
from typing import Optional


# # Automatically authenticate using DefaultAzureCredential
# credential = DefaultAzureCredential()

# # Azure Storage account information
# account_url = "https://<storage_account_name>.blob.core.windows.net"
# container_name = "my-container"
# blob_name = "folder/file.txt"

# # Initialize BlobServiceClient with Managed Identity
# blob_service_client = BlobServiceClient(account_url=account_url, credential=credential)


def initialize_storage_account(secret: dict) -> str:
    """Returns the connection string for Azure Blob Storage."""

    try:
        storage_account = secret["accountName"]
        storage_account_key = secret["key"]

        # Format the connection string
        blob_connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={storage_account};"
            f"AccountKey={storage_account_key};"
            f"EndpointSuffix=core.windows.net"
        )
        return blob_connection_string
    
    except KeyError:
        raise KeyError("The secret must have the following keys: `accountName` and `key`.")

    except Exception as e:
        raise Exception(f"Error initializing storage account: {e}")


def file_to_azure_storage(
    src_file_path: str,
    container_name: str,
    dest_blob_path: str,
    dest_file_name: str,
    secret: dict,
    overwrite: bool = True,
) -> None:
    """Uploads a file to Azure Blob Storage.

    Parameters
    ----------
        src_file_path (str): Source file to be uploaded.

        container_name (str): Azure storage container name.

        dest_blob_path (str): Destination blob (dir) path.

        dest_file_name (str): Destination file name.

        secret (dict): Secret dictionary.
            Example: `{"accountName": "some-account", "key": "some-key"}`

        overwrite (bool, optional): Whether or not to overwrite existing file. Defaults to `True`.

    Returns
    -------
        None

    Example
    -------
        file_to_azure_storage(
            "test_file.txt", "test_container", "your/path", "file.txt", mock_secret
        )
    """

    try:
        blob_connection_string = initialize_storage_account(secret)
        blob_service_client = BlobServiceClient.from_connection_string(
            blob_connection_string
        )
        if dest_blob_path.endswith("/"):  # Remove trailing slash
            dest_blob_path = dest_blob_path[:-1]

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=f"{dest_blob_path}/{dest_file_name}".lstrip("/"),
        )

        with open(src_file_path, "rb") as file:
            blob_client.upload_blob(file, overwrite=overwrite)

        print(
            f"Uploaded {src_file_path} to Azure Storage: {container_name}/{dest_blob_path}/{dest_file_name}"
        )

    except Exception as e:
        print(f"Error uploading file to blob storage: {e}")


def azure_storage_to_file(
    container_name: str,
    src_blob_path: str,
    src_file_name: str,
    secret: dict,
) -> None:
    """Downloads a file from Azure Blob Storage.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        src_blob_path (str): Source blob (dir) path.

        src_file_name (str): Source file name.
            This file name will be used when saving in local.

        secret (dict): Secret dictionary.
            Example: `{"accountName": "some-account", "key": "some-key"}`

    Returns
    -------
        None

    Example
    -------
        azure_storage_to_file("test_container", "path/to/file", "file.txt", mock_secret)
    """

    try:
        blob_connection_string = initialize_storage_account(secret)
        blob_service_client = BlobServiceClient.from_connection_string(
            blob_connection_string
        )
        if src_blob_path.endswith("/"):  # Remove trailing slash
            src_blob_path = src_blob_path[:-1]

        blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=f"{src_blob_path}/{src_file_name}".lstrip("/"),
        )

        with open(src_file_name, "wb") as file:
            blob_data = blob_client.download_blob()
            file.write(blob_data.readall())

        print(f"Downloaded blob to local path: {src_file_name}")

    except Exception as e:
        print(f"Error downloading file from blob storage: {e}")


def azure_storage_list_files(container_name: str, secret: dict) -> Optional[list[str]]:
    """Lists all files (blobs) in an Azure Blob Storage container.
    
    Parameters
    ----------
        container_name (str): Azure storage container name.

        secret (dict): Secret dictionary.
            Example: `{"accountName": "some-account", "key": "some-key"}`

    Returns
    -------
        list[str] | None
            A list of blobs' names.

    Example
    -------
        azure_storage_list_files("test_container", mock_secret)
    """

    try:
        blob_connection_string = initialize_storage_account(secret)
        container_client = ContainerClient.from_connection_string(
            blob_connection_string, container_name=container_name
        )
        blob_list = container_client.list_blobs()
        return [blob.name for blob in blob_list]

    except Exception as e:
        print(f"Error listing files in blob storage: {e}")
        return None
