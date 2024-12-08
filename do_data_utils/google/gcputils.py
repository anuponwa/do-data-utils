from google.cloud import storage
from google.oauth2 import service_account
import io
import json
import pandas as pd
from typing import Union
import warnings
from .common import get_secret_info


# ----------------
# Helper functions
# ----------------

def set_gcs_client(secret: Union[dict, str]):
    """Set GCS client based on the given `secret`
    
    Parameters
    ----------
    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.

    Returns
    -------
    storage.Client
    """

    secret = get_secret_info(secret)
    credentials = service_account.Credentials.from_service_account_info(secret)
    client = storage.Client(credentials=credentials)

    return client


def io_to_gcs(io_output, gcspath: str, secret: Union[dict, str]):
    """Uploads IO to GCS
    
    Parameters
    ----------
    io_output: io.IOBase
        IO output that has been opened or saved content to.
        
    gcspath: str
        GCS path that starts with 'gs://'.

    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.

    Returns
    -------
    None
    """

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    fullpath = '/'.join(gcspath.split("/")[3:])
    blob = bucket.blob(fullpath)
    io_output.seek(0)
    blob.upload_from_file(io_output)
        

def str_to_gcs(str_output: str, gcspath: str, secret: Union[dict, str]):
    """Uploads string to GCS
    
    Parameters
    ----------
    str_output: str
        string value that has been opened or saved content to.
        
    gcspath: str
        GCS path that starts with 'gs://'.
        
    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.

    Returns
    -------
    None
    """

    client = set_gcs_client(secret=secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    fullpath = '/'.join(gcspath.split("/")[3:])
    blob = bucket.blob(fullpath)
    blob.upload_from_string(str_output)


def df_to_excel_gcs(df, gcspath: str, secret: Union[dict, str], **kwargs):
    """Saves a pandas.DataFrame as an Excel file and uploads to GCS
    
    Parameters
    ----------
    df: pandas.DataFrame object
        A DataFrame object.
        
    gcspath: str
        GCS path that starts with 'gs://' and ends with 'xlsx'.

    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.

    Returns
    -------
    None
    """
    output = io.BytesIO()
    writer = pd.ExcelWriter(output)
    df.to_excel(writer, index=False, **kwargs)
    writer.save()
    
    io_to_gcs(output, gcspath, secret=secret)


def gcs_to_file(gcspath: str, secret: Union[dict, str]):
    """Downloads a GCS file to IO
    
    Parameter
    ---------
    gcspath: str
        GCS path to your file.

    secret: dict | str
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        
    Returns
    -------
    io.BufferedIOBase
        io.BytesIO containing the content of the file.
    """

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    fullpath = '/'.join(gcspath.split("/")[3:])
    blob = bucket.blob(fullpath)
    byte_stream = io.BytesIO()
    blob.download_to_file(byte_stream)
    byte_stream.seek(0)
    return byte_stream


# ----------------
# Util functions
# ----------------

def gcs_listfiles(gcspath: str, secret: Union[dict, str], files_only=True):
    """Lists files in a GCS directory
    
    Parameters
    ----------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
        
    files_only: bool, default=True
        Whether to output only the file inside the given path, or output the whole path.
        
    Returns
    -------
    list
        A list of file(s).
    """

    if not gcspath.startswith('gs://'):
        raise Exception("The path has to start with 'gs://'.")
    if not gcspath.endswith('/'):
        gcspath += '/'
    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    dirpath = '/'.join(gcspath.split("/")[3:])
    
    if dirpath=='':
        num_slash = 0
    else:
        num_slash = sum(1 for i in dirpath if i=='/')
    
    file_list = []
    for i in bucket.list_blobs(prefix=dirpath):
        num_slash_i = sum(1 for j in i.name if j=='/')
        if not i.name.endswith('/') and num_slash_i==num_slash:
            if files_only:
                file_list.append(i.name.split('/')[-1])
            else:
                file_list.append(i.name)

    return file_list


def gcs_listdirs(gcspath: str, secret: Union[dict, str], subdirs_only=True, trailing_slash=False):
    """Lists directories in GCS
    
    Parameters
    ----------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict | str
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        
    subdirs_only: bool, default=True
        Whether to output only the directory inside the given path, or output the whole path.
        
    trailing_slash: bool, default=False
        Whether to include the trailing slash in the directory name.
        
    Returns
    -------
    list
        A list of folder(s).
    """

    if not gcspath.startswith('gs://'):
        raise Exception("The path has to start with 'gs://'.")
    if not gcspath.endswith('/'):
        gcspath += '/'

    client = set_gcs_client(secret)
    bucket = client.get_bucket(gcspath.split("/")[2])
    dirpath = '/'.join(gcspath.split("/")[3:])
    iterator = bucket.list_blobs(prefix=dirpath, delimiter='/')
    list(iterator) # populate the prefixes

    if subdirs_only:
        dirs = [i.split('/')[-2]+'/' for i in iterator.prefixes]
    else:
        dirs = list(iterator.prefixes)
        
    if not trailing_slash:
        dirs = [d[:-1] for d in dirs]

    return dirs


def gcs_exists(gcspath: str, secret: Union[dict, str]):
    """Checks whether the given gcspath exists or not
    
    Parameter
    ---------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict | str
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        
    Returns
    -------
    bool
        Whether or not the file/folder exists.
    """

    end_pos = -2 if gcspath.endswith('/') else -1
    path_split = gcspath.split('/')
    element = path_split[end_pos]
    exists = element in gcs_listdirs('/'.join(path_split[:end_pos]), secret=secret) or element in gcs_listfiles('/'.join(path_split[:end_pos]), secret=secret)
    return exists


def gcs_to_dict(gcspath: str, secret: Union[dict, str]) -> dict:
    """Downloads a JSON file to a dictionary
    
    Parameter
    ---------
    gcspath: str
        GCS path to your json (or dict like) file.

    secret: dict | str
        A secret dictionary used to authenticate GCS
        or a path to the secret.json file.
        
    Returns
    -------
    dict
        A dictionary.
    """

    f = gcs_to_file(gcspath, secret)
    return json.load(f)


def gcs_to_df(gcspath: str, secret: Union[dict, str], polars=False, **kwargs):
    """Downloads a .csv or.xlsx file to a pandas.DataFrame
    
    Parameters
    ----------
    gcspath: str
        GCS path to your file.

    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.

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

    if not gcspath.startswith('gs://'):
        raise Exception("The path has to start with 'gs://'.")
    if not gcspath.endswith('.csv') and not gcspath.endswith('.xlsx'):
        raise Exception('The file name has to be either .csv or .xlsx or .log file.')
        
    if gcspath.endswith('.csv'):
        f = gcs_to_file(gcspath, secret=secret)
        df = pd.read_csv(f, **kwargs)
        
    elif gcspath.endswith('.xlsx'):
        f = gcs_to_file(gcspath, secret=secret)
        df = pd.read_excel(f, sheet_name=None, **kwargs)


    if polars:
        try:
            import polars as pl
        except ImportError:
            warnings.warn('Polars not installed. Falling back to pandas.')
            polars = False

    if polars:
        df = pl.from_pandas(df)
        
    return df


# -----------------
# Uploading to GCS
# -----------------

def df_to_gcs(df, gcspath: str, secret: Union[dict, str], **kwargs):
    """Saves a pandas.DataFrame (to any file type, e.g., .csv or .xlsx) and uploads to GCS
    
    Parameters
    ----------
    df: pandas.DataFrame object
        A DataFrame object.
        
    gcspath: str
        GCS path that starts with 'gs://' and ends with your preferred file type such as '.csv' or '.xlsx'.

    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.
    
    Returns
    -------
    None
    """

    if not gcspath.startswith('gs://'):
        raise Exception("The path has to start with 'gs://'.")
    if not gcspath.endswith('.csv') and not gcspath.endswith('.xlsx'):
        raise Exception('The file name has to be either .csv or .xlsx file.')
        
    if gcspath.endswith('.csv'):
        csv_data = df.to_csv(index=False, **kwargs)
        str_to_gcs(csv_data, gcspath, secret=secret)
        return f'The file has been successfully uploaded to {gcspath}.'
        
    elif gcspath.endswith('.xlsx'):
        df_to_excel_gcs(df, gcspath, secret=secret, **kwargs)
        return f'The file has been successfully uploaded to {gcspath}.'
    

def dict_to_json_gcs(dict_data: dict, gcspath: str, secret: Union[dict, str]):
    """Uploads a dictionary to a JSON file
    
    Parameters
    ----------
    dict_data: dict
        A dictionary.
    
    gcspath: str
        GCS path that starts with 'gs://' and ends with '.json'

    secret: dict | str
        A secret dictionary used to authenticate the GCS
        or a path to the secret.json file.

    Returns
    -------
    None
    """

    byte_stream = io.StringIO()
    json.dump(dict_data, byte_stream)
    
    io_to_gcs(byte_stream, gcspath, secret=secret)