import polars as pl
from unittest.mock import patch, MagicMock
from do_data_utils.azure import databricks_to_df


def test_databricks_to_df_wo_catalog(monkeypatch):
    # Mock Config
    mock_config = MagicMock()
    monkeypatch.setattr("do_data_utils.azure.azureutils.Config", mock_config)

    # Mock sql.connect
    mock_connect = MagicMock()
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection
    mock_conn_object_from_with = MagicMock()
    mock_connection.__enter__.return_value = mock_conn_object_from_with
    monkeypatch.setattr("do_data_utils.azure.azureutils.sql.connect", mock_connect)

    # Mocking pd.read_sql to avoid real DB interaction
    mock_read_sql = MagicMock(return_value="mocked_dataframe")
    monkeypatch.setattr("pandas.read_sql", mock_read_sql)

    # Prepare the input
    query = "SELECT * FROM some_table"

    secret = {
        "server_nm": "test-server",
        "http_path": "/test-path",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
    }

    # Call the function
    result = databricks_to_df(query, secret)

    # Assertions
    mock_config.assert_called_once_with(
        host="https://test-server",
        client_id="test-client-id",
        client_secret="test-client-secret",
    )

    mock_connect.assert_called_once_with(
        server_hostname="test-server",
        http_path="/test-path",
        credentials_provider=mock_connect.call_args.kwargs["credentials_provider"],
    )

    mock_read_sql.assert_called_once_with(query, mock_connection.__enter__.return_value)

    # Check the function returned the expected mock value
    assert result == "mocked_dataframe"


def test_databricks_to_df_w_catalog(monkeypatch):
    # Mock Config
    mock_config = MagicMock()
    monkeypatch.setattr("do_data_utils.azure.azureutils.Config", mock_config)

    # Mock sql.connect
    mock_connect = MagicMock()
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection
    mock_conn_object_from_with = MagicMock()
    mock_connection.__enter__.return_value = mock_conn_object_from_with
    monkeypatch.setattr("do_data_utils.azure.azureutils.sql.connect", mock_connect)

    # Mocking pd.read_sql to avoid real DB interaction
    mock_read_sql = MagicMock(return_value="mocked_dataframe")
    monkeypatch.setattr("pandas.read_sql", mock_read_sql)

    # Prepare the input
    query = "SELECT * FROM some_table"

    secret = {
        "server_nm": "test-server",
        "http_path": "/test-path",
        "client_id": "test-client-id",
        "client_secret": "test-client-secret",
        "catalog": "test-catalog",
    }

    # Call the function
    result = databricks_to_df(query, secret)

    # Assertions
    mock_config.assert_called_once_with(
        host="https://test-server",
        client_id="test-client-id",
        client_secret="test-client-secret",
    )

    mock_connect.assert_called_once_with(
        server_hostname="test-server",
        http_path="/test-path",
        credentials_provider=mock_connect.call_args.kwargs["credentials_provider"],
        catalog="test-catalog",
    )

    mock_read_sql.assert_called_once_with(query, mock_connection.__enter__.return_value)

    # Check the function returned the expected mock value
    assert result == "mocked_dataframe"


def test_databricks_to_df_polars():
    """Test databricks_to_df with polars=True."""

    # Mock data to return from the database
    mock_data = [
        (1, "Alice", 30),
        (2, "Bob", 25)
    ]
    mock_columns = ["id", "name", "age"]

    # Patch the connection and cursor
    with patch("do_data_utils.azure.azureutils.authen_databrick_sql") as mock_auth:
        # Create mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_data
        mock_cursor.description = [(col,) for col in mock_columns]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_auth.return_value.__enter__.return_value = mock_conn

        mock_query = "select * from catalog.schema.cust_table"
        mock_secret = {
            "server_nm": "test-server",
            "http_path": "/test-path",
            "client_id": "test-client-id",
            "client_secret": "test-client-secret",
        }

        # Call the function
        result = databricks_to_df(query=mock_query, secret=mock_secret, polars=True)

        # Verify that the result is a Polars DataFrame
        assert isinstance(result, pl.DataFrame)
        assert result.shape == (2, 3)  # Two rows, three columns
        assert result.columns == mock_columns
        mock_cursor.execute.assert_called_once_with(mock_query)