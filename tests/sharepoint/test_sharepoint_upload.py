import pandas as pd
import pytest
from unittest.mock import MagicMock, patch, mock_open

from do_data_utils.sharepoint.shputils import (
    file_to_sharepoint,
    df_to_sharepoint,
)


def test_upload_file(monkeypatch, secret_sharepoint):
    # Mock response
    mock_client = MagicMock()
    mock_app = MagicMock()
    mock_client.return_value = mock_app
    mock_refresh_token = "some-refresh-token"
    scopes = [
        "https://scgo365.sharepoint.com/AllSites.Manage",
        "https://scgo365.sharepoint.com/AllSites.Read",
        "https://scgo365.sharepoint.com/AllSites.Write",
    ]

    valid_results = {"access_token": "some-valid-access-token"}
    mock_app.acquire_token_by_refresh_token.return_value = valid_results

    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.msal.ConfidentialClientApplication",
        mock_client,
    )

    mock_post_request = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post_request.return_value = mock_response
    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.requests.post", mock_post_request
    )

    mock_file_content = "Some content"
    mock_open_obj = mock_open(read_data=mock_file_content)

    with patch("builtins.open", mock_open_obj):

        # Start firing the requests
        site = "Some-site"
        sharepoint_dir = "Path/to/that/dir"
        file_name = "some-name.xlsx"

        file_to_sharepoint(
            site,
            sharepoint_dir,
            file_name,
            secret=secret_sharepoint,
            refresh_token=mock_refresh_token,
        )

    mock_client.assert_called_once_with(
        client_id="some-id",
        authority="https://login.microsoftonline.com/some-tenant",
        client_credential="some-secret",
    )
    mock_app.acquire_token_by_refresh_token.assert_called_once_with(
        refresh_token="some-refresh-token", scopes=scopes
    )

    upload_url = f"https://scgo365.sharepoint.com/sites/{site}/_api/web/getfolderbyserverrelativeurl('{sharepoint_dir}')/files/add(url='{file_name}',overwrite=true)"
    headers = headers = {
        "Authorization": "Bearer some-valid-access-token",
        "Content-Type": "application/json;odata=verbose",
        "Accept": "application/json;odata=verbose",
    }
    mock_post_request.assert_called_once_with(
        upload_url, headers=headers, data="Some content"
    )


def test_upload_file_invalid(monkeypatch, secret_sharepoint):
    # Mock response
    mock_client = MagicMock()
    mock_app = MagicMock()
    mock_client.return_value = mock_app
    mock_refresh_token = "some-refresh-token"
    scopes = [
        "https://scgo365.sharepoint.com/AllSites.Manage",
        "https://scgo365.sharepoint.com/AllSites.Read",
        "https://scgo365.sharepoint.com/AllSites.Write",
    ]

    valid_results = {"access_token": "some-valid-access-token"}
    mock_app.acquire_token_by_refresh_token.return_value = valid_results

    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.msal.ConfidentialClientApplication",
        mock_client,
    )

    mock_post_request = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_post_request.return_value = mock_response
    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.requests.post", mock_post_request
    )

    mock_file_content = "Some content"
    mock_open_obj = mock_open(read_data=mock_file_content)

    with patch("builtins.open", mock_open_obj):

        # Start firing the requests
        site = "Some-site"
        sharepoint_dir = "Path/to/that/dir"
        file_name = "some-name.xlsx"

        with pytest.raises(RuntimeError):
            file_to_sharepoint(
                site,
                sharepoint_dir,
                file_name,
                secret=secret_sharepoint,
                refresh_token=mock_refresh_token,
            )


def test_upload_file_invalid_access_token(monkeypatch, secret_sharepoint):
    # Mock response
    mock_client = MagicMock()
    mock_app = MagicMock()
    mock_client.return_value = mock_app
    mock_refresh_token = "some-refresh-token"
    scopes = [
        "https://scgo365.sharepoint.com/AllSites.Manage",
        "https://scgo365.sharepoint.com/AllSites.Read",
        "https://scgo365.sharepoint.com/AllSites.Write",
    ]

    valid_results = {}
    mock_app.acquire_token_by_refresh_token.return_value = valid_results

    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.msal.ConfidentialClientApplication",
        mock_client,
    )

    mock_post_request = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post_request.return_value = mock_response
    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.requests.post", mock_post_request
    )

    mock_file_content = "Some content"
    mock_open_obj = mock_open(read_data=mock_file_content)

    with patch("builtins.open", mock_open_obj):

        # Start firing the requests
        site = "Some-site"
        sharepoint_dir = "Path/to/that/dir"
        file_name = "some-name.xlsx"

        with pytest.raises(ValueError):
            file_to_sharepoint(
                site,
                sharepoint_dir,
                file_name,
                secret=secret_sharepoint,
                refresh_token=mock_refresh_token,
            )


def test_upload_df_csv(monkeypatch, secret_sharepoint):
    # Mock response
    mock_client = MagicMock()
    mock_app = MagicMock()
    mock_client.return_value = mock_app
    mock_refresh_token = "some-refresh-token"
    scopes = [
        "https://scgo365.sharepoint.com/AllSites.Manage",
        "https://scgo365.sharepoint.com/AllSites.Read",
        "https://scgo365.sharepoint.com/AllSites.Write",
    ]

    valid_results = {"access_token": "some-valid-access-token"}
    mock_app.acquire_token_by_refresh_token.return_value = valid_results

    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.msal.ConfidentialClientApplication",
        mock_client,
    )

    mock_post_request = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post_request.return_value = mock_response
    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.requests.post", mock_post_request
    )

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    # Start firing the requests
    site = "Some-site"
    sharepoint_dir = "Path/to/that/dir"
    file_name = "some-name.csv"

    df_to_sharepoint(
        df=df,
        site=site,
        sharepoint_dir=sharepoint_dir,
        file_name=file_name,
        secret=secret_sharepoint,
        refresh_token=mock_refresh_token,
    )

    mock_client.assert_called_once_with(
        client_id="some-id",
        authority="https://login.microsoftonline.com/some-tenant",
        client_credential="some-secret",
    )

    mock_app.acquire_token_by_refresh_token.assert_called_once_with(
        refresh_token="some-refresh-token", scopes=scopes
    )

    upload_url = f"https://scgo365.sharepoint.com/sites/{site}/_api/web/getfolderbyserverrelativeurl('{sharepoint_dir}')/files/add(url='{file_name}',overwrite=true)"
    headers = headers = {
        "Authorization": "Bearer some-valid-access-token",
        "Content-Type": "application/json;odata=verbose",
        "Accept": "application/json;odata=verbose",
    }
    mock_post_request.assert_called_once_with(
        upload_url, headers=headers, data=b"a,b\n1,3\n2,4\n"
    )


def test_upload_df_xlsx(monkeypatch, secret_sharepoint):
    # Mock response
    mock_client = MagicMock()
    mock_app = MagicMock()
    mock_client.return_value = mock_app
    mock_refresh_token = "some-refresh-token"
    scopes = [
        "https://scgo365.sharepoint.com/AllSites.Manage",
        "https://scgo365.sharepoint.com/AllSites.Read",
        "https://scgo365.sharepoint.com/AllSites.Write",
    ]

    valid_results = {"access_token": "some-valid-access-token"}
    mock_app.acquire_token_by_refresh_token.return_value = valid_results

    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.msal.ConfidentialClientApplication",
        mock_client,
    )

    mock_post_request = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post_request.return_value = mock_response
    monkeypatch.setattr(
        "do_data_utils.sharepoint.shputils.requests.post", mock_post_request
    )

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    # Start firing the requests
    site = "Some-site"
    sharepoint_dir = "Path/to/that/dir"
    file_name = "some-name.xlsx"

    df_to_sharepoint(
        df=df,
        site=site,
        sharepoint_dir=sharepoint_dir,
        file_name=file_name,
        secret=secret_sharepoint,
        refresh_token=mock_refresh_token,
    )

    mock_client.assert_called_once_with(
        client_id="some-id",
        authority="https://login.microsoftonline.com/some-tenant",
        client_credential="some-secret",
    )

    mock_app.acquire_token_by_refresh_token.assert_called_once_with(
        refresh_token="some-refresh-token", scopes=scopes
    )

    mock_post_request.assert_called_once()


@pytest.mark.parametrize("param", ["some-name.log", "some-name.json", "some-name"])
def test_upload_df_invalid_filename(param, secret_sharepoint):

    # Start firing the requests
    mock_refresh_token = "some-refresh-token"
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    site = "Some-site"
    sharepoint_dir = "Path/to/that/dir"

    with pytest.raises(ValueError):
        df_to_sharepoint(
            df=df,
            site=site,
            sharepoint_dir=sharepoint_dir,
            file_name=param,
            secret=secret_sharepoint,
            refresh_token=mock_refresh_token,
        )
