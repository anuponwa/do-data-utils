from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Union
import warnings
from .common import get_secret_info


# ----------------
# Helper functions
# ----------------

def set_gbq_credentials(secret: Union[dict, str]):
    """Set GBQ credentials based on the given `secret`

    Parameters
    ----------
    secret: dict | str
        A secret dictionary used to authenticate the GBQ
        or a path to the secret.json file.

    Returns
    -------
    GBQ credentials
    """

    secret_info = get_secret_info(secret)
    credentials = service_account.Credentials.from_service_account_info(secret_info)
    return credentials


def set_gbq_client(secret: Union[dict, str]):
    """Set GBQ client based on the given `secret`
    
    Parameters
    ----------
    secret: dict | str
        A secret dictionary used to authenticate the Google Bigquery
        or a path to the secret.json file.

    Returns
    -------
    bigquery.CLient
    """

    secret_info = get_secret_info(secret)
    credentials = service_account.Credentials.from_service_account_info(secret_info)
    client = bigquery.Client(credentials=credentials)
    return client


# ----------------
# Utils functions
# ----------------

def gbq_to_df(query: str, secret: Union[dict, str], polars: bool=False):
    """Executes the `select` query and downloads it as a pandas.DataFrame
    
    Parameter
    ---------
    query: str
        An SQL query to be executed.
        
    secret: dict | str
        A secret dictionary used to authenticate the Google Bigquery
        or a path to the secret.json file.

    polars: bool, default=False
        If polars is True, the function returns polars.DataFrame (only if polars is installed in the environment).
        
    Returns
    -------
    DataFrame (pandas or polars).
    """

    client = set_gbq_client(secret=secret)
    df = client.query_and_wait(query).to_dataframe()

    if polars:
        try:
            import polars as pl
        except ImportError:
            warnings.warn('Polars not installed. Falling back to pandas.')
            polars = False

    if polars:
        df = pl.from_pandas(df)

    return df


def df_to_gbq(df, gbq_tb: str, secret: Union[dict, str], if_exists: str='fail', table_schema=None):
    """Uploads a pandas.DataFrame to a GBQ table
    
    Parameters
    ----------
    df: pandas.DataFrame object
        A DataFrame.
        
    gbq_tb: str
        GBQ table name including the project id and dataset id.
        For example, 'scg-cbm-do-dev-rg.indv_abc.test_table'.
        
    secret: dict | str
        A secret dictionary used to authenticate the Google Bigquery
        or a path to the secret.json file.

    if_exists: str, default='fail'
        What to do if the table already exists.
        Possible values are:
            `fail`
                Raises an error if the table already exists.
            `replace`
                Replaces the destination table.
            `append`
                Appends to the destination table.
    
    
    table_schema: list of dict [{'name':..., 'type':...}], default=None
        Schema of each column to be uploaded. For the omitted columns, a default datatype will be used.
        Please note that pd.datetime datatype cannot be uploaded as 'DATE' data type in GBQ.
        Please also note that the type value should be upper case.
        If DATE data type is preferred, the column has to be of `str` or `object` type containing dates in the `YYYY-mm-dd` format.
        
        For example, [{'name':'ds', 'type':'DATE'}, {'name':'dsr', 'type':'DATE'}]
            >> given that these two columns contain the `str` in a correct format,
            it will upload the DataFrame using DATE for these two columns, and default data types for the others.

    Returns
    -------
    None
    """
    
    tb_split = gbq_tb.split('.')
    if len(tb_split) != 3:
        raise Exception('The table name must have all 3 components: project_id.dataset_name.table_name.')
        
    project_id = tb_split[0]
    tablename = '.'.join(tb_split[1:])

    credentials = set_gbq_credentials(secret)
    df.to_gbq(tablename, project_id, if_exists=if_exists, table_schema=table_schema, credentials=credentials)
    
    print(f'The dataframe has been successfully uploaded to {gbq_tb}.')