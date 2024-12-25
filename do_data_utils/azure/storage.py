# from azure.identity import DefaultAzureCredential
from azure.identity import ClientSecretCredential
from azure.storage.filedatalake import DataLakeServiceClient
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


def get_service_client(secret: dict) -> DataLakeServiceClient:
    """Initializes and returns a DataLakeServiceClient using Azure AD credentials."""

    try:
        cred = ClientSecretCredential(
            tenant_id=secret["tenant_id"],
            client_id=secret["client_id"],
            client_secret=secret["client_secret"],
        )

        service_client = DataLakeServiceClient(
            account_url=f"https://{secret['storage_account']}.dfs.core.windows.net",
            credential=cred,
        )
        return service_client

    except KeyError:
        raise KeyError(
            "The secret must contain `tenant_id`, `client_id`, `client_secret`, and `storage_account` keys."
        )

    except Exception as e:
        raise Exception(f"Error initializing storage account: {e}")


def io_to_azure_storage(
    buffer,
    container_name: str,
    dest_file_path: str,
    secret: dict,
    overwrite: bool = True,
) -> None:
    """Uploads an in-memory buffer to Azure Blob Storage."""

    service_client = get_service_client(secret)

    file_client = service_client.get_file_client(
        file_system=container_name, file_path=dest_file_path.lstrip("/")
    )

    buffer.seek(0)  # Reset buffer position
    file_client.upload_data(buffer, overwrite=overwrite)

    print(f"Uploaded to Azure Storage: {container_name}/{dest_file_path}")


def azure_storage_to_io(
    container_name: str, file_path: str, secret: dict
) -> io.BytesIO:
    """Downloads a blob into an in-memory buffer."""

    service_client = get_service_client(secret)

    file_client = service_client.get_file_client(
        file_system=container_name, file_path=file_path.lstrip("/")
    )

    buffer = io.BytesIO()
    blob_data = file_client.download_file()
    buffer.write(blob_data.readall())
    buffer.seek(0)  # Reset buffer position for reading
    return buffer


def file_to_azure_storage(
    src_file_path: str,
    container_name: str,
    dest_file_path: str,
    secret: dict,
    overwrite: bool = True,
) -> None:
    """Uploads a file to Azure Blob Storage.

    Parameters
    ----------
        src_file_path (str): Source file to be uploaded.

        container_name (str): Azure storage container name.

        dest_file_path (str): Destination file path.

        secret (dict): Secret dictionary.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        overwrite (bool, optional): Whether or not to overwrite existing file. Defaults to `True`.

    Returns
    -------
        None

    Example
    -------
        file_to_azure_storage(
            "test_file.txt", "test_container", "your/path/to/test_file.txt", mock_secret
        )
    """

    service_client = get_service_client(secret)

    file_client = service_client.get_file_client(
        file_system=container_name, file_path=dest_file_path.lstrip("/")
    )

    with open(src_file_path, "rb") as file:
        file_client.upload_data(file, overwrite=overwrite)

    print(
        f"Uploaded {src_file_path} to Azure Storage: {container_name}/{dest_file_path}"
    )


def azure_storage_to_file(
    container_name: str,
    file_path: str,
    secret: dict,
) -> None:
    """Downloads a file from Azure Blob Storage.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        file_path (str): Azure storage file path.
            Example: `"some/path/to/myfile.csv"`

        secret (dict): Secret dictionary.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

    Returns
    -------
        None

    Example
    -------
        azure_storage_to_file("test_container", "path/to/file", "file.txt", mock_secret)
    """

    service_client = get_service_client(secret)

    file_client = service_client.get_file_client(
        file_system=container_name,
        file_path=file_path.lstrip("/"),
    )

    blob_data = file_client.download_file()

    local_file_name = file_path.split("/")[-1]

    with open(local_file_name, "wb") as file:
        file.write(blob_data.readall())

    print(f"Downloaded blob to local path: {local_file_name}")


def azure_storage_list_files(
    container_name: str, directory_path: str, secret: dict, files_only: bool = True
) -> list[str]:
    """Lists all files (blobs) in an Azure Blob Storage container.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        directory_path (str): Path to the directory in which you want to list the files.

        secret (dict): Secret dictionary.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        files_only (bool, optional): Whether or not to return only the files, excluding the directories. Default is `True`

    Returns
    -------
        list[str] | None
            A list of blobs' names.

    Example
    -------
        azure_storage_list_files("test_container", mock_secret)
    """

    service_client = get_service_client(secret)
    # Get the file system client
    file_system_client = service_client.get_file_system_client(
        file_system=container_name
    )

    # Normalize directory path
    if directory_path and not directory_path.endswith("/"):
        directory_path += "/"

    # List paths under the specified directory or root
    paths = file_system_client.get_paths(path=directory_path)

    if files_only:
        return [path.name for path in paths if not path.is_directory]

    return [path.name for path in paths]


def df_to_azure_storage(
    df: pd.DataFrame,
    container_name: str,
    dest_file_path: str,
    secret: dict,
    overwrite: bool = True,
    **kwargs,
) -> None:
    """Uploads a dataframe to Azure Blob Storage based on file extension.

    Parameters
    ----------
        df (pd.DataFrame): Source file to be uploaded.

        container_name (str): Azure storage container name.

        dest_file_path (str): Destination file name, including the full path.

        secret (dict): Secret dictionary.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

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
    ext = dest_file_path.split(".")[-1]

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
        dest_file_path=dest_file_path,
        secret=secret,
        overwrite=overwrite,
    )


def azure_storage_to_df(
    container_name: str,
    file_path: str,
    secret: dict,
    polars: bool = False,
    **kwargs,
):
    """Downloads a blob from Azure Blob Storage and converts it to a DataFrame.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        file_path (str): Full path to file in Azure storage.

        secret (dict): Secret dictionary.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        polars (bool): Whether or not to return a polars DataFrame.

        **kwargs: Other parameters to read the csv or parquet file.

    Returns
    -------
        pd.DataFrame or pl.DataFrame

    Example
    -------
        azure_storage_to_df("test_container", "path/to/file.csv", mock_secret)
    """

    # Use the new `azure_storage_to_io` function
    buffer = azure_storage_to_io(
        container_name=container_name,
        file_path=file_path,
        secret=secret,
    )

    # Determine format based on file extension
    ext = file_path.split(".")[-1]

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
