from unittest.mock import MagicMock
from do_data_utils.google import df_to_gbq


def test_gbq_to_pandas(mock_gbq_service_account_credentials, secret_json_dict):

    # Arrange the mock output
    mock_df_input = MagicMock()

    def mock_to_gbq_func(tablename, project_id, if_exists, table_schema, credentials):
        pass

    mock_df_input.to_gbq.side_effect = mock_to_gbq_func

    # Start testing
    gbq_tb = "some-project.some-schema.some-table"
    df_to_gbq(mock_df_input, gbq_tb=gbq_tb, secret=secret_json_dict)

    mock_df_input.to_gbq.assert_called_once_with(
        "some-schema.some-table",
        "some-project",
        if_exists="fail",
        table_schema=None,
        credentials=mock_gbq_service_account_credentials,
    )
