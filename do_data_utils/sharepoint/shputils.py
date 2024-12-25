import msal
import io
import pandas as pd
import requests
from typing import Optional


def get_msal_app(secret: dict) -> msal.ConfidentialClientApplication:
    """Gets the MSAL application client

    Parameters
    ----------
    secret: dict
        A secret dictionary to authenticate to "https://login.microsoftonline.com/".
        The authentication is done using `msal`'s `ConfidentialClientApplication` class.
        The secret must have these keys:
            - "client_id"
            - "tenant_id"
            - "client_secret"

    Returns
    -------
    msal.ConfidentialClientApplication
    """

    client_id = secret["client_id"]
    tenant_id = secret["tenant_id"]
    client_secret = secret["client_secret"]

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority="https://login.microsoftonline.com/" + tenant_id,
        client_credential=client_secret,
    )
    return app


def get_access_token(
    msal_app: msal.ConfidentialClientApplication,
    refresh_token: str,
    scopes: Optional[list[str]] = None,
) -> Optional[str]:
    """Gets access token to authorise to Sharepoint site

    Parameters
    ----------
    msal_app: msal.ConfidentialClientApplication
        Credential client application from `msal` package.
        You need `client_id`, `tenant_id`, and `client_secret` to login.

    refresh_token: str
        A refresh token to get the access token from `msal_app`.

    scopes: list[str] | None
        A list of scopes to use with `msal`.
        The default values are:
        [
            "https://scgo365.sharepoint.com/AllSites.Manage",
            "https://scgo365.sharepoint.com/AllSites.Read",
            "https://scgo365.sharepoint.com/AllSites.Write"
        ]

    Returns
    -------
    str
        Access token
    """

    if not scopes:
        scopes = [
            f"https://scgo365.sharepoint.com/AllSites.{s}"
            for s in ("Manage", "Read", "Write")
        ]

    result = msal_app.acquire_token_by_refresh_token(
        refresh_token=refresh_token,
        scopes=scopes,
    )

    access_token = result.get("access_token")

    if access_token:
        return access_token
    else:
        return None


def bytes_to_sharepoint(
    file_content: bytes,
    site: str,
    sharepoint_dir: str,
    file_name: str,
    access_token: str,
) -> None:
    """Uploads a bytes object to a Sharepoint location

    Parameters
    ----------
    file_content: bytes
        File content in bytes.

    site: str
        Sharepoint site.

    sharepoint_dir: str
        A Sharepoint directory.
        E.g., "Shared Documents/Directory1/Some sub-directory".

    file_name: str
        Path to the local file to be uploaded.
        This will also be the name of the file in Sharepoint.

    access_token: str
        An access token to authorise and upload to Sharepoint.

    Returns
    -------
    None
    """

    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json;odata=verbose",
        "Accept": "application/json;odata=verbose",
    }
    upload_url = f"https://scgo365.sharepoint.com/sites/{site}/_api/web/getfolderbyserverrelativeurl('{sharepoint_dir}')/files/add(url='{file_name}',overwrite=true)"

    # Make the request to upload the file
    response = requests.post(upload_url, headers=headers, data=file_content)

    # Check if the file was uploaded successfully
    if response.status_code == 200:
        print("File uploaded successfully!")
    else:
        print("Failed to upload file. Status code:", response.status_code)
        print("Response:", response.text)
        raise RuntimeError("Failed to upload file.")


def file_to_sharepoint(
    site: str,
    sharepoint_dir: str,
    file_name: str,
    secret: dict,
    refresh_token: str,
    scopes: Optional[list[str]] = None,
) -> None:
    """Uploads a local file to Sharepoint

    Parameters
    ----------
    site: str
        Sharepoint site.

    sharepoint_dir: str
        A Sharepoint directory.
        E.g., "Shared Documents/Directory1/Some sub-directory".

    file_name: str
        Path to the local file to be uploaded.
        This will also be the name of the file in Sharepoint.

    secret: dict
        A secret dictionary to authenticate to "https://login.microsoftonline.com/".
        The authentication is done using `msal`'s `ConfidentialClientApplication` class.
        The secret must have these keys:
            - "client_id"
            - "tenant_id"
            - "client_secret"

    refresh_token: str
        A refresh token to get the access token to access Sharepoint from `msal_app`.

    scopes: list[str] | None
        A list of scopes to use with `msal`.
        The default values are:
        [
            "https://scgo365.sharepoint.com/AllSites.{Manage}",
            "https://scgo365.sharepoint.com/AllSites.{Read}",
            "https://scgo365.sharepoint.com/AllSites.{Write}"
        ]

    Returns
    -------
    None
    """

    # Get the access token
    msal_app = get_msal_app(secret=secret)
    access_token = get_access_token(
        msal_app=msal_app, refresh_token=refresh_token, scopes=scopes
    )

    if not access_token:
        raise ValueError("Invalid access token.")

    # Handle the paths parameters
    site = site.strip("/")
    sharepoint_dir = sharepoint_dir.strip("/")

    # Read the file content
    with open(file_name, "rb") as f:
        file_content = f.read()

    # Upload the file content
    bytes_to_sharepoint(file_content, site, sharepoint_dir, file_name, access_token)


def df_to_sharepoint(
    df: pd.DataFrame,
    site: str,
    sharepoint_dir: str,
    file_name: str,
    secret: dict,
    refresh_token: str,
    scopes: Optional[list[str]] = None,
    **kwargs,
) -> None:
    """Uploads a DataFrame to a .csv or .xlsx file to Sharepoint

    Parameters
    ----------
    df: pd.DataFrame
        A dataframe to upload to Sharepoint.

    site: str
        Sharepoint site.

    sharepoint_dir: str
        A Sharepoint directory.
        E.g., "Shared Documents/Directory1/Some sub-directory".

    file_name: str
        Path to the local file to be uploaded.
        This will also be the name of the file in the Sharepoint.

    secret: dict
        A secret dictionary to authenticate to "https://login.microsoftonline.com/".
        The authentication is done using `msal`'s `ConfidentialClientApplication` class.
        The secret must have these keys:
            - "client_id"
            - "tenant_id"
            - "client_secret"

    refresh_token: str
        A refresh token to get the access token to access the Sharepoint from `msal_app`.

    scopes: list[str] | None
        A list of scopes to use with `msal`.
        The default values are:
        [
            "https://scgo365.sharepoint.com/AllSites.{Manage}",
            "https://scgo365.sharepoint.com/AllSites.{Read}",
            "https://scgo365.sharepoint.com/AllSites.{Write}"
        ]

    **kwargs:
        Other keyword arguments, please see more in `pd.to_csv()` and `pd.to_excel()`
        Do not supply `index=...` as the default already uses `index=False`.

    Returns
    -------
    None
    """
    # Get the access token
    msal_app = get_msal_app(secret=secret)
    access_token = get_access_token(
        msal_app=msal_app, refresh_token=refresh_token, scopes=scopes
    )

    if not access_token:
        raise ValueError("Invalid access token.")

    # Handle the paths parameters
    site = site.strip("/")
    sharepoint_dir = sharepoint_dir.strip("/")

    if not file_name.endswith(".csv") and not file_name.endswith(".xlsx"):
        raise ValueError("The `file_name` must be either .csv or .xlsx file.")

    if file_name.endswith(".csv"):
        csv_string = df.to_csv(index=False, **kwargs)
        file_content = csv_string.encode("utf-8")  # Convert to bytes

    elif file_name.endswith(".xlsx"):
        io_output = io.BytesIO()  # Define the output IO

        with pd.ExcelWriter(io_output) as writer:
            df.to_excel(writer, index=False, **kwargs)

        io_output.seek(0)  # Reset the cursor to the beginning (now, this is a file-like object)
        file_content = io_output.read() # Read the content to a variable as bytes

    # Upload the file content
    bytes_to_sharepoint(file_content, site, sharepoint_dir, file_name, access_token)
