import pytest
from unittest.mock import MagicMock

from do_data_utils.google import get_secret, list_secrets


def test_get_secret_no_cred(
    mock_secret_manager_client,
    mock_response_from_secret_access_bytes,
):

    mock_secret_manager_client.access_secret_version.return_value = (
        mock_response_from_secret_access_bytes
    )

    # Act
    secret_id = "some_secret_id"
    result = get_secret(secret_id, as_json=False)

    # Assert
    assert result == "mocked_secret_data"
    mock_secret_manager_client.access_secret_version.assert_called_once_with(
        request={"name": f"projects/-/secrets/{secret_id}/versions/latest"}
    )


def test_get_secret_bytes(
    mock_secret_manager_client,
    mock_secret_service_account_credentials,
    secret_json_dict,
    mock_response_from_secret_access_bytes,
):

    mock_secret_manager_client.access_secret_version.return_value = (
        mock_response_from_secret_access_bytes
    )

    # Act
    secret_id = "some_secret_id"
    result = get_secret(secret_id, secret_json_dict, as_json=False)

    # Assert
    assert result == "mocked_secret_data"
    mock_secret_manager_client.access_secret_version.assert_called_once_with(
        request={
            "name": f"projects/{secret_json_dict['project_id']}/secrets/{secret_id}/versions/latest"
        }
    )


def test_get_secret_json(
    mock_secret_manager_client,
    mock_secret_service_account_credentials,
    secret_json_dict,
    mock_response_from_secret_access_json,
):

    mock_secret_manager_client.access_secret_version.return_value = (
        mock_response_from_secret_access_json
    )

    # Act
    secret_id = "some_secret_id"
    result = get_secret(secret_id, secret_json_dict, as_json=True)

    # Assert
    assert result == {"some_key": "some_value"}
    mock_secret_manager_client.access_secret_version.assert_called_once_with(
        request={
            "name": f"projects/{secret_json_dict['project_id']}/secrets/{secret_id}/versions/latest"
        }
    )


def test_list_secrets(
    mock_secret_manager_client,
    mock_secret_service_account_credentials,
    secret_json_dict,
):
    # Arrange: Mock the client and `list_secrets` behavior
    mock_secret1 = MagicMock()
    mock_secret1.name = f"projects/{secret_json_dict['project_id']}/secrets/secret1"

    mock_secret2 = MagicMock()
    mock_secret2.name = f"projects/{secret_json_dict['project_id']}/secrets/secret2"

    # Mock list_secrets to return an iterable of mock secrets
    mock_secret_manager_client.list_secrets.return_value = [mock_secret1, mock_secret2]

    # Act: Call the function under test
    secret = {"project_id": f"{secret_json_dict['project_id']}"}
    results = list_secrets(secret)

    # Assert: Verify the returned list of secret names
    assert results == ["secret1", "secret2"]

    # Verify `list_secrets` was called with the correct parameters
    mock_secret_manager_client.list_secrets.assert_called_once_with(
        request={"parent": f"projects/{secret_json_dict['project_id']}"}
    )


def test_get_secret_data_corruption(
    mock_secret_manager_client, mock_secret_manager_corrupted_response
):
    """Test for data corruption detection."""
    # Mock the client response
    mock_secret_manager_client.access_secret_version.return_value = (
        mock_secret_manager_corrupted_response
    )

    with pytest.raises(Exception):
        get_secret(secret_id="test-secret", as_json=False)


def test_get_secret_failed_to_parse_json(
    mock_secret_manager_client, mock_secret_manager_invalid_json_response
):
    """Test for failed JSON parsing."""
    # Mock the client response
    mock_secret_manager_client.access_secret_version.return_value = (
        mock_secret_manager_invalid_json_response
    )

    with pytest.raises(ValueError):
        get_secret(secret_id="test-secret", as_json=True)
