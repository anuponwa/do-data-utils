# from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
import io
import pandas as pd
import polars as pl
from typing import Union


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
        raise KeyError(
            "The secret must have the following keys: `accountName` and `key`."
        )

    except Exception as e:
        raise Exception(f"Error initializing storage account: {e}")


def io_to_azure_storage(
    buffer,
    container_name: str,
    dest_blob_path: str,
    dest_file_name: str,
    secret: dict,
    overwrite: bool = True,
) -> None:
    """Uploads an in-memory buffer to Azure Blob Storage."""

    blob_connection_string = initialize_storage_account(secret)
    blob_service_client = BlobServiceClient.from_connection_string(
        blob_connection_string
    )

    if dest_blob_path.endswith("/"):  # Remove trailing slash
        dest_blob_path = dest_blob_path[:-1]

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=f"{dest_blob_path}/{dest_file_name}".lstrip("/")
    )

    buffer.seek(0)  # Reset buffer position
    blob_client.upload_blob(buffer, overwrite=overwrite)

    print(
        f"Uploaded to Azure Storage: {container_name}/{dest_blob_path}/{dest_file_name}"
    )


def azure_storage_to_io(
    container_name: str, src_blob_path: str, src_file_name: str, secret: dict
) -> io.BytesIO:
    """Downloads a blob into an in-memory buffer."""

    blob_connection_string = initialize_storage_account(secret)
    blob_service_client = BlobServiceClient.from_connection_string(
        blob_connection_string
    )

    if src_blob_path.endswith("/"):  # Remove trailing slash
        src_blob_path = src_blob_path[:-1]

    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=f"{src_blob_path}/{src_file_name}".lstrip("/")
    )

    buffer = io.BytesIO()
    blob_data = blob_client.download_blob()
    buffer.write(blob_data.readall())
    buffer.seek(0)  # Reset buffer position for reading
    return buffer


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


def azure_storage_list_files(container_name: str, secret: dict) -> list[str]:
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

    blob_connection_string = initialize_storage_account(secret)
    container_client = ContainerClient.from_connection_string(
        blob_connection_string, container_name=container_name
    )
    blob_list = container_client.list_blobs()
    return [blob.name for blob in blob_list]


def df_to_azure_storage(
    df: pd.DataFrame,
    container_name: str,
    dest_blob_path: str,
    dest_file_name: str,
    secret: dict,
    overwrite: bool = True,
    **kwargs,
) -> None:
    """Uploads a dataframe to Azure Blob Storage based on file extension.

    Parameters
    ----------
        df (pd.DataFrame): Source file to be uploaded.

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
        df_to_azure_storage(
            my_df, "test_container", "your/path", "output.csv", mock_secret
        )
    """

    # Determine format based on file extension
    ext = dest_file_name.split(".")[-1]

    if ext == "parquet":
        buffer: Union[io.BytesIO, io.StringIO] = io.BytesIO()
        df.to_parquet(buffer, index=False, **kwargs)
    elif ext == "csv":
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, **kwargs)
    else:
        raise ValueError("The file must be either: `parquet` or `csv`.")

    io_to_azure_storage(
        buffer=buffer,
        container_name=container_name,
        dest_blob_path=dest_blob_path,
        dest_file_name=dest_file_name,
        secret=secret,
        overwrite=overwrite,
    )


def azure_storage_to_df(
    container_name: str,
    src_blob_path: str,
    src_file_name: str,
    secret: dict,
    polars: bool = False,
    **kwargs,
):
    """Downloads a blob from Azure Blob Storage and converts it to a DataFrame.
    
    Parameters
    ----------
        container_name (str): Azure storage container name.

        src_blob_path (str): Source blob (dir) path.

        src_file_name (str): Source file name.
            This file name will be used when saving in local.

        secret (dict): Secret dictionary.
            Example: `{"accountName": "some-account", "key": "some-key"}`

        polars (bool): Whether or not to return a polars DataFrame.

    Returns
    -------
        pd.DataFrame or pl.DataFrame

    Example
    -------
        azure_storage_to_df("test_container", "path/to/file", "input.csv", mock_secret)
    """

    # Use the new `azure_storage_to_io` function
    buffer = azure_storage_to_io(
        container_name=container_name,
        src_blob_path=src_blob_path,
        src_file_name=src_file_name,
        secret=secret,
    )

    # Determine format based on file extension
    ext = src_file_name.split(".")[-1]

    if ext == "parquet":
        if polars:
            return pl.read_parquet(buffer, **kwargs)
        return pd.read_parquet(buffer, **kwargs)

    elif ext == "csv":
        buffer_str = io.StringIO(buffer.getvalue().decode())
        if polars:
            return pl.read_csv(buffer_str, **kwargs)
        return pd.read_csv(buffer_str, **kwargs)

    else:
        raise ValueError("The file must be either: `parquet` or `csv`.")
