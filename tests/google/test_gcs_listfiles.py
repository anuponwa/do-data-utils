import pytest
from unittest.mock import MagicMock
from do_data_utils.google import gcs_listfiles


def test_gcs_listfiles_files_only(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):

    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    m_1 = MagicMock()
    m_2 = MagicMock()
    m_3 = MagicMock()
    m_4 = MagicMock()

    m_1.name = "path/to/investigate/path/"
    m_2.name = "path/to/investigate/somefile.csv"
    m_3.name = "path/to/investigate/another_dir/"
    m_4.name = "path/to/investigate/output.json"

    mock_bucket.list_blobs.return_value = [m_1, m_2, m_3, m_4]

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate"
    results = gcs_listfiles(gcspath=gcspath, secret=secret_json_dict)

    assert isinstance(results, list)
    assert set(results) == set(["somefile.csv", "output.json"])
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.list_blobs.assert_called_once_with(prefix="path/to/investigate/")


def test_gcs_listfiles_with_prefix(
    mock_gcs_client, mock_gcs_service_account_credentials, secret_json_dict
):

    # Setup some mock client and returns
    mock_bucket = MagicMock()
    mock_gcs_client.get_bucket.return_value = mock_bucket

    m_1 = MagicMock()
    m_2 = MagicMock()
    m_3 = MagicMock()
    m_4 = MagicMock()

    m_1.name = "path/to/investigate/path/"
    m_2.name = "path/to/investigate/somefile.csv"
    m_3.name = "path/to/investigate/another_dir/"
    m_4.name = "path/to/investigate/output.json"

    mock_bucket.list_blobs.return_value = [m_1, m_2, m_3, m_4]

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate"
    results = gcs_listfiles(gcspath=gcspath, secret=secret_json_dict, files_only=False)

    assert isinstance(results, list)
    assert set(results) == set(
        ["path/to/investigate/somefile.csv", "path/to/investigate/output.json"]
    )
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.list_blobs.assert_called_once_with(prefix="path/to/investigate/")


def test_gcs_listfiles_invalid(secret_json_dict):
    with pytest.raises(ValueError):
        gcspath = "some-invalid-path"
        _ = gcs_listfiles(gcspath=gcspath, secret=secret_json_dict, files_only=False)
