from google.cloud import secretmanager
from google.oauth2 import service_account
import google_crc32c
import json
from typing import Optional, Union, Tuple
from .common import get_secret_info, get_default_project_id


# ----------------
# Helper functions
# ----------------


def set_secret_manager_client(
    secret: Optional[Union[dict, str]],
) -> Tuple[secretmanager.SecretManagerServiceClient, Optional[dict]]:
    """Gets a secret manager client

    Parameters
    ----------
    secret: dict | str | None
        A secret dictionary used to authenticate the secret manager
        or a path to the secret.json file.
        If None, it uses the default credentials.

    Returns
    -------
    Tuple[client, dict]
        A tuple of secret manager and the dictionary of the secret.
    """

    if secret:
        secret = get_secret_info(secret)
        credentials = service_account.Credentials.from_service_account_info(secret)
        client = secretmanager.SecretManagerServiceClient(credentials=credentials)
    else:
        client = secretmanager.SecretManagerServiceClient()

    if secret == "":
        secret = None

    return client, secret


# ----------------
# Utils functions
# ----------------


def get_secret(
    secret_id: str,
    secret: Optional[Union[dict, str]] = None,
    project_id: Optional[str] = None,
    as_json: bool = False,
    version_id: Union[str, int] = "latest",
) -> Union[str, dict]:
    """Gets secret from Google secret manager

    Parameters
    ----------
    secret_id: str
        The name of the secret you want to retrieve.

    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the secret manager.
        or a path to the secret.json file.
        The secret must have 'project_id' key.
        If None, it uses the default credentials.

    project_id: str | None, default = None
        Google's project ID for the secret manager.
        Used only if the `secret` is not provided.

        If a str is provided, it will attempt to use that project_id to get the secret.

        If `None`, the it will attempt to get a project-id from the default using Application Default Credentials (ADC)

        You can authenticate via `gcloud` CLI, i.e., `gcloud auth application-default login`.

    as_json: bool, default=False
        Indicates whether or not the secret is in the JSON format
        and you would like to return as a dictionary.

    version_id: str | int, default='latest'
        The version of the secret. 'latest' gets the latest updated version.

    Returns
    -------
    str | dict
        Secret string or dictionary.
    """

    client, secret = set_secret_manager_client(secret=secret)

    if secret and isinstance(secret, dict) and "project_id" in secret:
        project_id = secret["project_id"]
    elif not project_id:
        project_id = get_default_project_id()
    elif isinstance(project_id, str):
        project_id = project_id
    else:
        raise ValueError("`project_id` must be a valid string. Or you can pass in a valid `secret` (credentials JSON) instead.")

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Verify payload checksum.
    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        raise Exception("Data corruption detected.")

    payload = response.payload.data.decode("UTF-8")

    if as_json:
        try:
            return json.loads(payload)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse secret as JSON: {e}")

    return payload


def list_secrets(
    secret: Optional[Union[dict, str]] = None,
    project_id: Optional[str] = None,
):
    """List all secrets in the given project.

    Parameters
    ----------
    secret: dict | str | None, default = None
        A secret dictionary used to authenticate the secret manager
        or a path to the secret.json file.
        The secret must have 'project_id' key.
        If None, it uses the default credentials.

    project_id: str | None, default = None
        Google's project ID for the secret manager.
        Used only if the `secret` is not provided.

        If a str is provided, it will attempt to use that project_id to get the secret.

        If `None`, the it will attempt to get a project-id from the default using Application Default Credentials (ADC)

        You can authenticate via `gcloud` CLI, i.e., `gcloud auth application-default login`.

    Returns
    -------
    list
        List of secret names.
    """

    # Create the Secret Manager client.
    client, secret = set_secret_manager_client(secret=secret)

    if secret and isinstance(secret, dict) and "project_id" in secret:
        project_id = secret["project_id"]
    elif not project_id:
        project_id = get_default_project_id()
    elif isinstance(project_id, str):
        project_id = project_id
    else:
        raise ValueError("`project_id` must be a valid string. Or you can pass in a valid `secret` (credentials JSON) instead.")

    # Build the resource name of the parent project.
    parent = f"projects/{project_id}"

    # List all secrets.
    secrets_list = []
    for secret in client.list_secrets(request={"parent": parent}):
        secret_name_path = secret.name
        secret_name = secret_name_path.split("/")[-1]
        secrets_list.append(secret_name)

    return secrets_list
