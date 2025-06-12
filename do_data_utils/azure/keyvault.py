import json
from typing import Optional, Union

from azure.keyvault.secrets import KeyVaultSecret, SecretClient

from .storage import get_credentials


def get_secret(
    secret_id: str, keyvault: str, secret: Optional[dict] = None, as_json: bool = False
) -> Union[str, dict, None]:
    """Gets secret from Azure Keyvault

    Parameters
    ----------
    secret_id: str
        The name of the secret you want to retrieve.

    keyvault: str
        Azure Keyvault's name where the secrets are stored.

    secret: dict | None, Default = None
        A secret dictionary used to authenticate Azure Keyvault.
        If None, it will try to use Default Credentials in the machine.

    as_json: bool, default=False
        Indicates whether or not the secret is in the JSON format
        and you would like to return as a dictionary.

    Returns
    -------
    str | dict
        Secret string or dictionary.
    """

    cred = get_credentials(secret=secret)

    vault_url: str = f"https://{keyvault}.vault.azure.net"
    secret_client = SecretClient(vault_url=vault_url, credential=cred)
    keyvault_secret: KeyVaultSecret = secret_client.get_secret(secret_id)

    secret_value = keyvault_secret.value

    if secret_value is None:
        return None

    if as_json:
        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse secret as JSON: {e}")

    return secret_value
