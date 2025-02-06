import io
from typing import Optional, Union

import pandas as pd
import polars as pl
from azure.core.credentials import TokenCredential  # Base class for credentials
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient


def get_service_client(
    secret: Optional[dict] = None, storage_account_name: Optional[str] = None
) -> DataLakeServiceClient:
    """Initializes and returns a DataLakeServiceClient using Azure AD credentials."""

    try:
        cred: TokenCredential  # Use the base class for type hinting

        if secret:
            cred = ClientSecretCredential(
                tenant_id=secret["tenant_id"],
                client_id=secret["client_id"],
                client_secret=secret["client_secret"],
            )

            storage_account_name = secret["storage_account"]

        elif storage_account_name:
            cred = DefaultAzureCredential()

        else:
            raise ValueError(
                "Either `secret` or `storage_account_name` must not be empty."
            )

        service_client = DataLakeServiceClient(
            account_url=f"https://{storage_account_name}.dfs.core.windows.net",
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
    secret: Optional[dict] = None,
    overwrite: bool = True,
    storage_account_name: Optional[str] = None,
) -> None:
    """Uploads an in-memory buffer to Azure Blob Storage."""

    service_client = get_service_client(
        secret, storage_account_name=storage_account_name
    )

    file_client = service_client.get_file_client(
        file_system=container_name, file_path=dest_file_path.lstrip("/")
    )

    buffer.seek(0)  # Reset buffer position
    file_client.upload_data(buffer, overwrite=overwrite)

    print(f"Uploaded to Azure Storage: {container_name}/{dest_file_path}")


def azure_storage_to_io(
    container_name: str,
    file_path: str,
    secret: Optional[dict] = None,
    storage_account_name: Optional[str] = None,
) -> io.BytesIO:
    """Downloads a blob into an in-memory buffer."""

    service_client = get_service_client(
        secret, storage_account_name=storage_account_name
    )

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
    secret: Optional[dict] = None,
    overwrite: bool = True,
    storage_account_name: Optional[str] = None,
) -> None:
    """Uploads a file to Azure Blob Storage.

    Parameters
    ----------
        src_file_path (str): Source file to be uploaded.

        container_name (str): Azure storage container name.

        dest_file_path (str): Destination file path.

        secret (dict, optional): Secret dictionary. Defaults = None.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        overwrite (bool): Whether or not to overwrite existing file. Defaults to `True`.

        storage_account_name (str, optional): Storage account to connect to. Only applies if `secret` is None.

    Returns
    -------
        None

    Example
    -------
        file_to_azure_storage(
            "test_file.txt", "test_container", "your/path/to/test_file.txt", mock_secret
        )

        file_to_azure_storage(
            "test_file.txt", "test_container", "your/path/to/test_file.txt", secret=None, storage_account_name="data_env"
        )
    """

    service_client = get_service_client(
        secret, storage_account_name=storage_account_name
    )

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
    secret: Optional[dict] = None,
    storage_account_name: Optional[str] = None,
) -> None:
    """Downloads a file from Azure Blob Storage.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        file_path (str): Azure storage file path.
            Example: `"some/path/to/myfile.csv"`

        secret (dict, optional): Secret dictionary. Defaults = None.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        storage_account_name (str, optional): Storage account to connect to. Only applies if `secret` is None.

    Returns
    -------
        None

    Example
    -------
        azure_storage_to_file("test_container", "path/to/file/file.txt", mock_secret)

        azure_storage_to_file("test_container", "path/to/file/file.txt", storage_account_name="data_env")
    """

    service_client = get_service_client(
        secret, storage_account_name=storage_account_name
    )

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
    container_name: str,
    directory_path: str,
    secret: Optional[dict] = None,
    files_only: bool = True,
    storage_account_name: Optional[str] = None,
) -> list[str]:
    """Lists all files (blobs) in an Azure Blob Storage container.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        directory_path (str): Path to the directory in which you want to list the files.

        secret (dict, optional): Secret dictionary. Defaults = None.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        files_only (bool): Whether or not to return only the files, excluding the directories. Default is `True`

        storage_account_name (str, optional): Storage account to connect to. Only applies if `secret` is None.

    Returns
    -------
        list[str] | None
            A list of blobs' names.

    Example
    -------
        azure_storage_list_files("test_container", "somepath", mock_secret)

        azure_storage_list_files("test_container", "somepath", storage_account_name="data_env")
    """

    service_client = get_service_client(
        secret, storage_account_name=storage_account_name
    )

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
    secret: Optional[dict] = None,
    overwrite: bool = True,
    storage_account_name: Optional[str] = None,
    **kwargs,
) -> None:
    """Uploads a dataframe to Azure Blob Storage based on file extension.

    Parameters
    ----------
        df (pd.DataFrame): Source file to be uploaded.

        container_name (str): Azure storage container name.

        dest_file_path (str): Destination file name, including the full path.

        secret (dict, optional): Secret dictionary. Defaults = None.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        overwrite (bool): Whether or not to overwrite existing file. Defaults to `True`.

        storage_account_name (str, optional): Storage account to connect to. Only applies if `secret` is None.

        **kwargs: Other keyword arguments to the write_*() method from pd.DataFrame.

    Returns
    -------
        None

    Example
    -------
        df_to_azure_storage(
            my_df, "test_container", "your/path/output.csv", mock_secret
        )

        df_to_azure_storage(
            my_df, "test_container", "your/path/output.csv", secret=None, storage_account_name="data_env"
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
        storage_account_name=storage_account_name,
    )


def azure_storage_to_df(
    container_name: str,
    file_path: str,
    secret: Optional[dict],
    polars: bool = False,
    storage_account_name: Optional[str] = None,
    **kwargs,
):
    """Downloads a blob from Azure Blob Storage and converts it to a DataFrame.

    Parameters
    ----------
        container_name (str): Azure storage container name.

        file_path (str): Full path to file in Azure storage.

        secret (dict, optional): Secret dictionary. Defaults = None.
            Example: {
                "tenant_id": "your-tenant-id",
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "storage_account": "your-storage-account"
            }

        polars (bool): Whether or not to return a polars DataFrame. Defaults to False.

        storage_account_name (str, optional): Storage account to connect to. Only applies if `secret` is None.

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
        storage_account_name=storage_account_name,
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
