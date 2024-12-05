from google.cloud import secretmanager
from google.oauth2 import service_account
import google_crc32c


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

