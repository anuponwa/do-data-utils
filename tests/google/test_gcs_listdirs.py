import pytest
from unittest.mock import MagicMock
from do_data_utils.google import gcs_listdirs


def test_gcs_listdirs_subdirs_only(
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

    mock_iterator = MagicMock()
    mock_iterator.__iter__.return_value = iter([m_1, m_2, m_3, m_4])
    mock_iterator.prefixes = [
        "path/to/investigate/path/",
        "path/to/investigate/another_dir/",
    ]

    mock_bucket.list_blobs.return_value = mock_iterator

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate"
    results = gcs_listdirs(gcspath=gcspath, secret=secret_json_dict, subdirs_only=True)

    assert isinstance(results, list)
    assert set(results) == set(["path", "another_dir"])
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.list_blobs.assert_called_once_with(
        prefix="path/to/investigate/", delimiter="/"
    )


def test_gcs_listdirs_with_prefix(
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

    mock_iterator = MagicMock()
    mock_iterator.__iter__.return_value = iter([m_1, m_2, m_3, m_4])
    mock_iterator.prefixes = [
        "path/to/investigate/path/",
        "path/to/investigate/another_dir/",
    ]

    mock_bucket.list_blobs.return_value = mock_iterator

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate"
    results = gcs_listdirs(gcspath=gcspath, secret=secret_json_dict, subdirs_only=False)

    assert isinstance(results, list)
    assert set(results) == set(
        ["path/to/investigate/path", "path/to/investigate/another_dir"]
    )
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.list_blobs.assert_called_once_with(
        prefix="path/to/investigate/", delimiter="/"
    )


def test_gcs_listdirs_with_trailing(
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

    mock_iterator = MagicMock()
    mock_iterator.__iter__.return_value = iter([m_1, m_2, m_3, m_4])
    mock_iterator.prefixes = [
        "path/to/investigate/path/",
        "path/to/investigate/another_dir/",
    ]

    mock_bucket.list_blobs.return_value = mock_iterator

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate"
    results = gcs_listdirs(
        gcspath=gcspath, secret=secret_json_dict, subdirs_only=True, trailing_slash=True
    )

    assert isinstance(results, list)
    assert set(results) == set(["path/", "another_dir/"])
    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.list_blobs.assert_called_once_with(
        prefix="path/to/investigate/", delimiter="/"
    )


def test_gcs_listdirs_invalid(secret_json_dict):
    with pytest.raises(ValueError):
        gcspath = "some-invalid-path"
        _ = gcs_listdirs(gcspath=gcspath, secret=secret_json_dict)
