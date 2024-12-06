from google.cloud import secretmanager
from google.oauth2 import service_account
import google_crc32c


def get_secret(secret_id: str, secret: dict, version_id='latest') -> str:
    """
    Parameters
    ----------
    secret_id: str
        The name of the secret you want to retrieve

    secret: dict
        A secret dictionary used to authenticate the secret manager
        The secret must have 'project_id' key

    version_id: int or str (Default: 'latest')
        The version of the secret. 'latest' gets the latest updated version.

    Returns
    -------
    A string representation of the secret.
    """

    credentials = service_account.Credentials.from_service_account_info(secret)
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    project_id = secret['project_id']

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


def list_secrets(secret: dict):
    """List all secrets in the given project.
    Parameters
    ----------
    secret: dict
        A secret dictionary used to authenticate the secret manager
        The secret must have 'project_id' key

    Returns
    -------
    list
        List of secret names
    """

    # Create the Secret Manager client.
    credentials = service_account.Credentials.from_service_account_info(secret)
    client = secretmanager.SecretManagerServiceClient(credentials=credentials)

    project_id = secret['project_id']

    # Build the resource name of the parent project.
    parent = f'projects/{project_id}'

    # List all secrets.
    secrets_list = []
    for secret in client.list_secrets(request={'parent': parent}):
        secret_name_path = secret.name
        secret_name = secret_name_path.split('/')[-1]
        secrets_list.append(secret_name)

    return secrets_list


