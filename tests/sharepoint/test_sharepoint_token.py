import pytest
from unittest.mock import MagicMock

from do_data_utils.sharepoint.shputils import get_msal_app, get_access_token


def test_get_msal_app_valid(secret_sharepoint, monkeypatch):

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

    msal_app = get_msal_app(secret=secret_sharepoint)
    access_token = get_access_token(msal_app=msal_app, refresh_token=mock_refresh_token)

    assert access_token == "some-valid-access-token"
    mock_client.assert_called_once_with(
        client_id="some-id",
        authority="https://login.microsoftonline.com/some-tenant",
        client_credential="some-secret",
    )
    mock_app.acquire_token_by_refresh_token.assert_called_once_with(
        refresh_token="some-refresh-token", scopes=scopes
    )


def test_get_msal_app_invalid_access_token(secret_sharepoint, monkeypatch):

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

    msal_app = get_msal_app(secret=secret_sharepoint)
    access_token = get_access_token(msal_app=msal_app, refresh_token=mock_refresh_token)

    assert access_token is None
    mock_client.assert_called_once_with(
        client_id="some-id",
        authority="https://login.microsoftonline.com/some-tenant",
        client_credential="some-secret",
    )
    mock_app.acquire_token_by_refresh_token.assert_called_once_with(
        refresh_token="some-refresh-token", scopes=scopes
    )


def test_get_msal_app_invalid_secret(monkeypatch):
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

    secret = {
        "client-id": "some-id",
        "tenant": "some-tenant",
        "credentials": "some-secret",
    }

    with pytest.raises(KeyError):
        msal_app = get_msal_app(secret=secret)
        access_token = get_access_token(
            msal_app=msal_app, refresh_token=mock_refresh_token
        )
