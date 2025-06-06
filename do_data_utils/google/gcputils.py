from google.cloud import storage
from google.oauth2 import service_account
import io
import json
import os
import pandas as pd
import polars as pl
from typing import Optional, Union

from .common import get_secret_info


# ----------------
# Helper functions
# ----------------


def set_gcs_client(secret: Optional[Union[dict, str]] = None):
    """Set GCS client based on the given `secret`

    Parameters
    ----------
    secret: dict | str | None, default=None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    storage.Client
    """

    if secret:
        secret = get_secret_info(secret)
        credentials = service_account.Credentials.from_service_account_info(secret)
        client = storage.Client(credentials=credentials)
    else:
        client = storage.Client()

    return client


def io_to_gcs(io_output, gcspath: str, secret: Optional[Union[dict, str]] = None):
    """Uploads IO to GCS

    Parameters
    ----------
    io_output: io.IOBase
        IO output that has been opened or saved content to.

    gcspath: str
        GCS path that starts with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    fullpath = "/".join(gcspath.split("/")[3:])
    blob = bucket.blob(fullpath)
    io_output.seek(0)
    blob.upload_from_file(io_output)


def str_to_gcs(
    str_output: str, gcspath: str, secret: Optional[Union[dict, str]] = None
) -> None:
    """Uploads string to GCS

    Parameters
    ----------
    str_output: str
        string value that has been opened or saved content to.

    gcspath: str
        GCS path that starts with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    client = set_gcs_client(secret=secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    fullpath = "/".join(gcspath.split("/")[3:])
    blob = bucket.blob(fullpath)
    blob.upload_from_string(str_output)


def df_to_excel_gcs(
    df, gcspath: str, secret: Optional[Union[dict, str]] = None, **kwargs
) -> None:
    """Saves a pandas.DataFrame as an Excel file and uploads to GCS

    Parameters
    ----------
    df: pandas.DataFrame object
        A DataFrame object.

    gcspath: str
        GCS path that starts with 'gs://' and ends with 'xlsx'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    io_output = io.BytesIO()
    df.to_excel(io_output, index=False, **kwargs)

    io_to_gcs(io_output, gcspath, secret=secret)


def gcs_to_io(gcspath: str, secret: Optional[Union[dict, str]] = None) -> io.BytesIO:
    """Downloads a GCS file to IO

    Parameter
    ---------
    gcspath: str
        GCS path to your file.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    io.BufferedIOBase
        io.BytesIO containing the content of the file.
    """

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    fullpath = "/".join(gcspath.split("/")[3:])
    blob = bucket.blob(fullpath)
    byte_stream = io.BytesIO()
    blob.download_to_file(byte_stream)
    byte_stream.seek(0)
    return byte_stream


# ----------------
# Util functions
# ----------------


def gcs_listfiles(
    gcspath: str, secret: Optional[Union[dict, str]] = None, files_only=True
) -> list:
    """Lists files in a GCS directory

    Parameters
    ----------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    files_only: bool, default=True
        Whether to output only the file inside the given path, or output the whole path.

    Returns
    -------
    list
        A list of file(s).
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")
    if not gcspath.endswith("/"):
        gcspath += "/"

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    dirpath = "/".join(gcspath.split("/")[3:])

    if dirpath == "":
        num_slash = 0
    else:
        num_slash = sum(1 for i in dirpath if i == "/")

    file_list = []
    for i in bucket.list_blobs(prefix=dirpath):
        num_slash_i = sum(1 for j in i.name if j == "/")
        if not i.name.endswith("/") and num_slash_i == num_slash:
            if files_only:
                file_list.append(i.name.split("/")[-1])
            else:
                file_list.append(i.name)

    return file_list


def gcs_listdirs(
    gcspath: str,
    secret: Optional[Union[dict, str]] = None,
    subdirs_only=True,
    trailing_slash=False,
) -> list:
    """Lists directories in GCS

    Parameters
    ----------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    subdirs_only: bool, default=True
        Whether to output only the directory inside the given path, or output the whole path.

    trailing_slash: bool, default=False
        Whether to include the trailing slash in the directory name.

    Returns
    -------
    list
        A list of folder(s).
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")
    if not gcspath.endswith("/"):
        gcspath += "/"

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    dirpath = "/".join(gcspath.split("/")[3:])
    iterator = bucket.list_blobs(prefix=dirpath, delimiter="/")
    list(iterator)  # populate the prefixes

    if subdirs_only:
        dirs = [i.split("/")[-2] + "/" for i in iterator.prefixes]
    else:
        dirs = list(iterator.prefixes)

    if not trailing_slash:
        dirs = [d[:-1] for d in dirs]

    return dirs


def gcs_exists(gcspath: str, secret: Optional[Union[dict, str]] = None) -> bool:
    """Checks whether the given gcspath exists or not

    Parameter
    ---------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    bool
        Whether or not the file/folder exists.
    """

    end_pos = -2 if gcspath.endswith("/") else -1
    path_split = gcspath.split("/")
    element = path_split[end_pos]
    exists = element in gcs_listdirs(
        "/".join(path_split[:end_pos]), secret=secret
    ) or element in gcs_listfiles("/".join(path_split[:end_pos]), secret=secret)
    return exists


def gcs_to_dict(gcspath: str, secret: Optional[Union[dict, str]] = None) -> dict:
    """Downloads a JSON file to a dictionary

    Parameter
    ---------
    gcspath: str
        GCS path to your json (or dict like) file.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    dict
        A dictionary.
    """

    f = gcs_to_io(gcspath, secret)
    return json.load(f)


def gcs_to_df(
    gcspath: str, secret: Optional[Union[dict, str]] = None, polars=False, **kwargs
):
    """Downloads a .csv or.xlsx file to a pandas.DataFrame

    Parameters
    ----------
    gcspath: str
        GCS path to your file.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    polars: bool, default=False
        If polars is True, the function returns polars.DataFrame (only if polars is installed in the environment).

    **kwargs: keyword arguments
        Other keyword arguments available in function pd.read_csv() and pd.read_excel().
        For example, `dtype=str`.

    Returns
    -------
    pandas.DataFrame (or a dict if the file is .xlsx)
        A DataFrame containing the content of the downloaded file or;
        a dictionary with the keys being the sheet names of the Excel file, and the values being the DataFrames.
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")
    if not gcspath.endswith(".csv") and not gcspath.endswith(".xlsx"):
        raise ValueError("The file name has to be either .csv or .xlsx file.")

    if gcspath.endswith(".csv"):
        f = gcs_to_io(gcspath, secret=secret)
        df = pd.read_csv(f, **kwargs)

    elif gcspath.endswith(".xlsx"):
        f = gcs_to_io(gcspath, secret=secret)
        df = pd.read_excel(f, sheet_name=None, **kwargs)

    if polars:
        df = pl.from_pandas(df)

    return df


# -----------------
# Uploading to GCS
# -----------------


def df_to_gcs(df: pd.DataFrame, gcspath: str, secret: Optional[Union[dict, str]] = None, **kwargs):
    """Saves a pandas.DataFrame (to any file type, e.g., .csv, parquet or .xlsx) and uploads to GCS

    Parameters
    ----------
    df: pandas.DataFrame object
        A DataFrame object.

    gcspath: str
        GCS path that starts with 'gs://' and ends with your preferred file type such as '.csv', '.parquet' or '.xlsx'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    **kwargs:
        Keyword arguments to use with `df.to_csv()` and `df.to_excel()`.

    Returns
    -------
    None
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")

    if not gcspath.endswith(".csv") and not gcspath.endswith(".parquet") and not gcspath.endswith(".xlsx"):
        raise ValueError("The file name has to be either .csv, .parquet or .xlsx file.")

    if gcspath.endswith(".csv"):
        csv_data = df.to_csv(index=False, **kwargs)
        str_to_gcs(csv_data, gcspath, secret=secret)
        print(f"The file has been successfully uploaded to {gcspath}.")

    elif gcspath.endswith(".parquet"):
        buffer: Union[io.BytesIO, io.StringIO] = io.BytesIO()
        df.to_parquet(buffer, index=False, **kwargs)
        io_to_gcs(buffer, gcspath, secret=secret)
        print(f"The file has been successfully uploaded to {gcspath}.")

    elif gcspath.endswith(".xlsx"):
        df_to_excel_gcs(df, gcspath, secret=secret, **kwargs)
        print(f"The file has been successfully uploaded to {gcspath}.")


def dict_to_json_gcs(
    dict_data: dict, gcspath: str, secret: Optional[Union[dict, str]] = None
):
    """Uploads a dictionary to a JSON file

    Parameters
    ----------
    dict_data: dict
        A dictionary.

    gcspath: str
        GCS path that starts with 'gs://' and ends with '.json'

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")

    if not gcspath.endswith(".json"):
        raise ValueError("The file name has .json file.")

    byte_stream = io.StringIO()
    json.dump(dict_data, byte_stream)

    io_to_gcs(byte_stream, gcspath, secret=secret)


# ------------------
# Files and folders
# ------------------


def gcs_to_file(gcspath: str, secret: Optional[Union[dict, str]] = None) -> None:
    """Downloads a GCS file to the current directory

    Parameters
    ----------
    gcspath: str
        GCS path to a file. It must start with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")

    if gcspath.endswith("/"):
        raise ValueError("`gcspath` parameter must be a file.")

    byte_stream = gcs_to_io(gcspath=gcspath, secret=secret)
    file_name = gcspath.split("/")[-1]
    with open(file_name, "wb") as f:
        f.write(byte_stream.read())


def file_to_gcs(
    file_path: str, gcspath: str, secret: Optional[Union[dict, str]] = None
) -> None:
    """Uploads a local file to GCS bucket/directory

    Parameters
    ----------
    file_path: str
        Path to file to upload.

    gcspath: str
        GCS path to a file. It must start with 'gs://'.
        It must have the same file type as the `file_path`.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")

    if gcspath.endswith("/"):
        raise ValueError("`gcspath` parameter must be a file.")

    file_ext = file_path.split(".")[-1]
    gcsp_ext = gcspath.split(".")[-1]
    if file_ext != gcsp_ext:
        raise ValueError(
            "Both `file_path` and `gcspath` must have the same file extensions."
        )

    with open(file_path, "rb") as f:
        io_to_gcs(io_output=f, gcspath=gcspath, secret=secret)


def download_folder_gcs(
    gcspath: str, local_dir: str, secret: Optional[Union[dict, str]] = None
) -> None:
    """Downloads the entire folder to a local directory

    Parameters
    ----------
    gcspath: str
        GCS path to a folder. It must start with 'gs://'.

    local_dir: str
        Local directory you want to save the results.
        The folder can either exist or not.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")

    if not gcspath.endswith("/"):
        gcspath += "/"

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    dirpath = "/".join(gcspath.split("/")[3:])  # Directory path in GCS

    blobs = bucket.list_blobs(prefix=dirpath)

    # Ensure the local directory exists
    os.makedirs(local_dir, exist_ok=True)

    # Iterate through all files and download them
    for blob in blobs:
        # If it's a "folder" (trailing slash in GCS), skip
        if blob.name.endswith("/"):
            continue

        # Create a local file path by joining the local directory with the blob's name
        local_file_path = os.path.join(local_dir, blob.name[len(dirpath):])


        # Ensure the local folder structure exists
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

        # Download the file
        blob.download_to_filename(local_file_path)
        print(f"Downloaded {blob.name} to {local_file_path}")


def upload_folder_gcs(
    local_dir: str, gcspath: str, secret: Optional[Union[dict, str]] = None
) -> None:
    """Uploads the entire folder to GCS

    Parameters
    ----------
    local_dir: str
        Local directory you want to upload.

    gcspath: str
        GCS path to the folder to upload to. It must start with 'gs://'.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    None
    """

    if not gcspath.startswith("gs://"):
        raise ValueError("The path has to start with 'gs://'.")

    # Authenticate and create a GCS client
    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    dirpath = "/".join(gcspath.split("/")[3:])  # Directory path in GCS

    # Iterate over all files in the local directory (including subfolders)
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)

            # Create a relative path for the file from the local directory
            relative_path = os.path.relpath(local_file_path, local_dir)

            # Construct the GCS path (including the folder prefix)
            gcs_path = os.path.join(dirpath, relative_path).replace(os.sep, "/")

            # Upload the file to GCS
            blob = bucket.blob(gcs_path)
            blob.upload_from_filename(local_file_path)
            print(f"Uploaded {local_file_path} to gs://{bucket}/{gcs_path}")
