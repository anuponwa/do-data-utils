from unittest.mock import MagicMock
from do_data_utils.google import gcs_exists


def test_gcs_exists_dir(
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
    gcspath = "gs://some-bucket/path/to/investigate/another_dir"
    results = gcs_exists(gcspath=gcspath, secret=secret_json_dict)

    assert isinstance(results, bool)
    assert results is True

    mock_gcs_client.get_bucket.assert_called_once_with("some-bucket")
    mock_bucket.list_blobs.assert_called_once_with(
        prefix="path/to/investigate/", delimiter="/"
    )


def test_gcs_exists_file(
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

    def mock_list_blobs(prefix, delimiter=None):
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([m_1, m_2, m_3, m_4])
        mock_iterator.prefixes = [
            "path/to/investigate/path/",
            "path/to/investigate/another_dir/",
        ]
        return mock_iterator

    mock_bucket.list_blobs.side_effect = mock_list_blobs

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate/output.json"
    results = gcs_exists(gcspath=gcspath, secret=secret_json_dict)

    assert isinstance(results, bool)
    assert results is True

    # Each function gets called twice: 1 to the listdirs() and 1 to the listfiles()
    assert mock_gcs_client.get_bucket.call_count == 2
    assert mock_bucket.list_blobs.call_count == 2

    mock_gcs_client.get_bucket.assert_any_call("some-bucket")
    mock_bucket.list_blobs.assert_any_call(prefix="path/to/investigate/", delimiter="/")
    mock_bucket.list_blobs.assert_any_call(prefix="path/to/investigate/")


def test_gcs_not_exists(
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

    def mock_list_blobs(prefix, delimiter=None):
        mock_iterator = MagicMock()
        mock_iterator.__iter__.return_value = iter([m_1, m_2, m_3, m_4])
        mock_iterator.prefixes = [
            "path/to/investigate/path/",
            "path/to/investigate/another_dir/",
        ]
        return mock_iterator

    mock_bucket.list_blobs.side_effect = mock_list_blobs

    # Tests...
    gcspath = "gs://some-bucket/path/to/investigate/something_here"
    results = gcs_exists(gcspath=gcspath, secret=secret_json_dict)

    assert isinstance(results, bool)
    assert results is False

    # Each function gets called twice: 1 to the listdirs() and 1 to the listfiles()
    assert mock_gcs_client.get_bucket.call_count == 2
    assert mock_bucket.list_blobs.call_count == 2

    mock_gcs_client.get_bucket.assert_any_call("some-bucket")
    mock_bucket.list_blobs.assert_any_call(prefix="path/to/investigate/", delimiter="/")
    mock_bucket.list_blobs.assert_any_call(prefix="path/to/investigate/")
