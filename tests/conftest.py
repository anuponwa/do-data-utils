import google_crc32c
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def secret_json_content():
    return '''{
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
'''

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
    "universe_domain": "googleapis.com"
}


@pytest.fixture
def mock_secret_manager_client():
    with patch("do_data_utils.google.google_secret.secretmanager.SecretManagerServiceClient") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance


@pytest.fixture
def mock_secret_service_account_credentials():
    with patch("do_data_utils.google.google_secret.service_account.Credentials.from_service_account_info") as mock_client:
        credentials_instance = MagicMock()
        mock_client.return_value = credentials_instance
        yield credentials_instance


@pytest.fixture
def mock_response_from_secret_access_bytes():
    mock_data = b'mocked_secret_data'
    mock_data_crc32c = google_crc32c.Checksum()
    mock_data_crc32c.update(mock_data)

    mock_payload = MagicMock()
    mock_payload.data = mock_data
    mock_payload.data_crc32c = int(mock_data_crc32c.hexdigest(), 16)

    mock_response = MagicMock()
    mock_response.payload = mock_payload

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
    with patch("do_data_utils.google.gbqutils.service_account.Credentials.from_service_account_info") as mock_client:
        credentials_instance = MagicMock()
        mock_client.return_value = credentials_instance
        yield credentials_instance


@pytest.fixture
def mock_gbq_client():
    with patch("do_data_utils.google.gbqutils.bigquery.Client") as mock_client:
        client_instance = MagicMock()
        mock_client.return_value = client_instance
        yield client_instance

