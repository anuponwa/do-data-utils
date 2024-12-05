from google.cloud import bigquery, secretmanager, storage
from google.oauth2 import service_account
import google_crc32c
import io
import json


def get_secret(secret_info: dict, project_id: str, secret_id: str, version_id='latest') -> str:
    """
    Parameters
    ----------
    secret_info: dict
        A secret dictionary used to authenticate the secret manager
    project_id: str
        The GCP project name that holds the secrets
    secret_id: str
        The name of the secret you want to retrieve
    version_id: int or str (Default: 'latest')
        The version of the secret. 'latest' gets the latest updated version.

    Returns
    -------
    A string representation of the secret.
    """

    credentials = service_account.Credentials.from_service_account_info(secret_info)
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    # Build the resource name of the secret version.
    name = f'projects/{project_id}/secrets/{secret_id}/versions/{version_id}'

    # Access the secret version.
    response = client.access_secret_version(request={'name': name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print('Data corruption detected.')
        raise Exception('Data corruption detected.')

    payload = response.payload.data.decode('UTF-8')
    return payload


def set_gcs_client(secret: dict):
    """
    Parameters
    ----------
    secret: dict
        A secret dictionary used to authenticate the GCS.

    Returns
    -------
    storage.Client
    """

    credentials = service_account.Credentials.from_service_account_info(secret)
    return storage.Client(credentials=credentials)


def gcs_listfiles(gcspath: str, secret: dict, files_only=True):
    """Lists files in a GCS directory
    
    Parameters
    ----------
    gcspath: str
        GCS path starting with 'gs://'.
        
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


def gcs_listdirs(gcspath: str, secret: dict, subdirs_only=True, trailing_slash=False):
    """Lists directories in GCS
    
    Parameters
    ----------
    gcspath: str
        GCS path starting with 'gs://'.

    secret: dict
        A secret dictionary used to authenticate GCS.
        
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


def gcs_exists(gcspath: str, secret: dict):
    """Checks whether the given gcspath exists or not
    
    Parameter
    ---------
    gcspath: str
        GCS path starting with 'gs://'.
    secret: dict
        A secret dictionary used to authenticate GCS.
        
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


def gcs_to_file(gcspath: str, secret: dict):
    """Downloads a GCS file to IO
    
    Parameter
    ---------
    gcspath: str
        GCS path to your file.
    secret: dict
        A secret dictionary used to authenticate GCS.
        
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


def gcs_to_dict(gcspath: str, secret: dict) -> dict:
    """Downloads a JSON file to a dictionary
    
    Parameter
    ---------
    gcspath: str
        GCS path to your json (or dict like) file.
    secret: dict
        A secret dictionary used to authenticate GCS.
        
    Returns
    -------
    dict
        A dictionary.
    """

    f = gcs_to_file(gcspath, secret)
    return json.load(f)

