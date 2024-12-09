from unittest.mock import patch, MagicMock
from do_data_utils.azure import databricks_to_df


def test_databricks_to_df_wo_catalog(monkeypatch):
    # Mock Config
    mock_config = MagicMock()
    monkeypatch.setattr('do_data_utils.azure.azureutils.Config', mock_config)
    
    # Mock sql.connect
    mock_connect = MagicMock()
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection
    mock_conn_object_from_with = MagicMock()
    mock_connection.__enter__.return_value = mock_conn_object_from_with
    monkeypatch.setattr('do_data_utils.azure.azureutils.sql.connect', mock_connect)

    # Mocking pd.read_sql to avoid real DB interaction
    mock_read_sql = MagicMock(return_value='mocked_dataframe')
    monkeypatch.setattr('pandas.read_sql', mock_read_sql)

    # Prepare the input
    query = 'SELECT * FROM some_table'

    secret = {
        'server_nm': 'test-server',
        'http_path': '/test-path',
        'client_id': 'test-client-id',
        'client_secret': 'test-client-secret',
    }

    # Call the function
    result = databricks_to_df(query, secret)

    # Assertions
    mock_config.assert_called_once_with(
        host='https://test-server',
        client_id='test-client-id',
        client_secret='test-client-secret'
    )

    mock_connect.assert_called_once_with(
        server_hostname='test-server',
        http_path='/test-path',
        credentials_provider=mock_connect.call_args.kwargs['credentials_provider']
    )

    mock_read_sql.assert_called_once_with(query, mock_connection.__enter__.return_value)

    # Check the function returned the expected mock value
    assert result == 'mocked_dataframe'



def test_databricks_to_df_w_catalog(monkeypatch):
    # Mock Config
    mock_config = MagicMock()
    monkeypatch.setattr('do_data_utils.azure.azureutils.Config', mock_config)
    # mock_config_credentials = MagicMock()
    # monkeypatch.setattr('do_data_utils.azure.azureutils.oauth_service_principal', mock_config_credentials)
    
    # Mock sql.connect
    mock_connect = MagicMock()
    mock_connection = MagicMock()
    mock_connect.return_value = mock_connection
    mock_conn_object_from_with = MagicMock()
    mock_connection.__enter__.return_value = mock_conn_object_from_with
    monkeypatch.setattr('do_data_utils.azure.azureutils.sql.connect', mock_connect)

    # Mocking pd.read_sql to avoid real DB interaction
    mock_read_sql = MagicMock(return_value='mocked_dataframe')
    monkeypatch.setattr('pandas.read_sql', mock_read_sql)

    # Prepare the input
    query = 'SELECT * FROM some_table'

    secret = {
        'server_nm': 'test-server',
        'http_path': '/test-path',
        'client_id': 'test-client-id',
        'client_secret': 'test-client-secret',
        'catalog': 'test-catalog'
    }

    # Call the function
    result = databricks_to_df(query, secret)

    # Assertions
    mock_config.assert_called_once_with(
        host='https://test-server',
        client_id='test-client-id',
        client_secret='test-client-secret'
    )

    mock_connect.assert_called_once_with(
        server_hostname='test-server',
        http_path='/test-path',
        credentials_provider=mock_connect.call_args.kwargs['credentials_provider'],
        catalog='test-catalog'
    )

    mock_read_sql.assert_called_once_with(query, mock_connection.__enter__.return_value)

    # Check the function returned the expected mock value
    assert result == 'mocked_dataframe'


