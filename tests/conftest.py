import google_crc32c
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def secret_json_content():
    return """{
    "type": "service_account",
    "project_id": "some_project",
    "private_key_id": "some_private_key_id",
    "private_key": "-----BEGIN PRIVATE KEY-----\\nsome_private_key\\n-----END PRIVATE KEY-----\\n",
    "client_email": "service-account-email@some_project.iam.gserviceaccount.com",
    "client_id": "12345678901234567890",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/secret-access%40some_project.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
"""


@pytest.fixture
def secret_json_dict():
    return {
        "type": "service_account",
        "project_id": "some_project",
        "private_key_id": "some_private_key_id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nsome_private_key\n-----END PRIVATE KEY-----\n",
        "client_email": "service-account-email@some_project.iam.gserviceaccount.com",
        "client_id": "12345678901234567890",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/secret-access%40some_project.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }


@pytest.fixture
def secret_sharepoint():
    return {
        "client_id": "some-id",
        "tenant_id": "some-tenant",
        "client_secret": "some-secret",
    }


@pytest.fixture
def mock_secret_manager_client():
    with patch(
        "do_data_utils.google.google_secret.secretmanager.SecretManagerServiceClient"
    ) as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_secret_service_account_credentials():
    with patch(
        "do_data_utils.google.google_secret.service_account.Credentials.from_service_account_info"
    ) as mock_client:
        credentials_instance = MagicMock()
        mock_client.return_value = credentials_instance
        yield credentials_instance


@pytest.fixture
def mock_response_from_secret_access_bytes():
    mock_data = b"mocked_secret_data"
    mock_data_crc32c = google_crc32c.Checksum()
    mock_data_crc32c.update(mock_data)

    mock_payload = MagicMock()
    mock_payload.data = mock_data
    mock_payload.data_crc32c = int(mock_data_crc32c.hexdigest(), 16)

    mock_response = MagicMock()
    mock_response.payload = mock_payload

    return mock_response


@pytest.fixture
def mock_secret_manager_corrupted_response():
    mock_corrupted_data = b"corrupted-data"
    mock_response = MagicMock()
    mock_response.payload.data = mock_corrupted_data
    crc32c = google_crc32c.Checksum()
    crc32c.update(b"some-other-data")  # Simulate a mismatched checksum
    mock_response.payload.data_crc32c = int(crc32c.hexdigest(), 16)
    return mock_response


@pytest.fixture
def mock_secret_manager_invalid_json_response():
    mock_invalid_json = b'{"key": "value"'
    mock_response = MagicMock()
    mock_response.payload.data = mock_invalid_json
    crc32c = google_crc32c.Checksum()
    crc32c.update(mock_invalid_json)
    mock_response.payload.data_crc32c = int(crc32c.hexdigest(), 16)
    return mock_response


@pytest.fixture
def mock_response_from_secret_access_json():
    mock_data = b'{"some_key": "some_value"}'
    mock_data_crc32c = google_crc32c.Checksum()
    mock_data_crc32c.update(mock_data)

    mock_payload = MagicMock()
    mock_payload.data = mock_data
    mock_payload.data_crc32c = int(mock_data_crc32c.hexdigest(), 16)

    mock_response = MagicMock()
    mock_response.payload = mock_payload

    return mock_response


@pytest.fixture
def mock_gbq_service_account_credentials():
    with patch(
        "do_data_utils.google.gbqutils.service_account.Credentials.from_service_account_info"
    ) as mock_client:
        credentials_instance = MagicMock()
        mock_client.return_value = credentials_instance
        yield credentials_instance


@pytest.fixture
def mock_gbq_client():
    with patch("do_data_utils.google.gbqutils.bigquery.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_gcs_service_account_credentials():
    with patch(
        "do_data_utils.google.gcputils.service_account.Credentials.from_service_account_info"
    ) as mock_client:
        credentials_instance = MagicMock()
        mock_client.return_value = credentials_instance
        yield credentials_instance


@pytest.fixture
def mock_gcs_client():
    with patch("do_data_utils.google.gcputils.storage.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_azure_config():
    with patch("do_data_utils.azure.databricks.sdk.core.Config") as mock_config:
        config = MagicMock()
        mock_config.return_value = config
        yield config


@pytest.fixture
def mock_azure_oauth_service_principal():
    with patch(
        "do_data_utils.azure.databricks.sdk.core.oauth_service_principal"
    ) as mock_service_principal:
        mock_credentials = MagicMock()
        mock_service_principal.return_value = mock_credentials
        yield mock_credentials
