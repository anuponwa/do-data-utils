import json
from typing import Union


def get_secret_info(secret: Union[dict, str]) -> dict:
    """Gets the secret info

    Parameters
    ----------
    secret: dict | str
        A secret dictionary used to authenticate the secret manager
        or a path to the secret.json file.

    Returns
    -------
    dict
        A dictionary of the secret.
    """

    if isinstance(secret, dict):
        secret_info = secret

    elif isinstance(secret, str) and secret.endswith('.json'):
        with open(secret, 'r') as f:
            secret_info = json.load(f)

    else:
        raise ValueError('`secret` must be a dictionary or a JSON file path.')

    return secret_info