import pandas as pd
import polars as pl
from unittest.mock import MagicMock
from do_data_utils.google import gbq_to_df


def test_gbq_to_pandas(mock_gbq_client, mock_gbq_service_account_credentials, secret_json_dict):

    # Arrange the mock output
    mock_response_query = MagicMock()
    mock_response_query.to_dataframe.return_value = pd.DataFrame({'col_1': [1,2,3], 'col_2': [4,5,6]})

    mock_gbq_client.query_and_wait.return_value = mock_response_query

    # Start testing
    query = 'select * from my_table'
    df_results = gbq_to_df(query, secret=secret_json_dict, polars=False)

    assert isinstance(df_results, pd.DataFrame)


def test_gbq_to_polars(mock_gbq_client, mock_gbq_service_account_credentials, secret_json_dict, monkeypatch):

    # Arrange the mock output
    mock_response_query = MagicMock()
    mock_response_query.to_dataframe.return_value = pd.DataFrame({'col_1': [1,2,3], 'col_2': [4,5,6]})

    mock_gbq_client.query_and_wait.return_value = mock_response_query

    # Start testing
    query = 'select * from my_table'
    df_results = gbq_to_df(query, secret=secret_json_dict, polars=True)

    assert isinstance(df_results, pl.DataFrame)


def test_gbq_to_pandas_empty_secret(mock_gbq_client, mock_gbq_service_account_credentials):

    # Arrange the mock output
    mock_response_query = MagicMock()
    mock_response_query.to_dataframe.return_value = pd.DataFrame({'col_1': [1,2,3], 'col_2': [4,5,6]})

    mock_gbq_client.query_and_wait.return_value = mock_response_query

    # Start testing
    query = 'select * from my_table'
    df_results = gbq_to_df(query, secret=None, polars=False)

    assert isinstance(df_results, pd.DataFrame)