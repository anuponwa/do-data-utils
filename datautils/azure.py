from databricks import sql
from databricks.sdk.core import Config, oauth_service_principal
import pandas as pd
import warnings


def authen_databrick_sql(secret: dict):
    """
    Parameters
    ----------
    secret: dict
        A secret dictionary used to authenticate to Databricks server.

    Returns
    -------
    Connection
    """
    
    server_nm = secret['server_nm']
    http_path = secret['http_path']
    client_id = secret['client_id']
    client_secret = secret['client_secret']

    config = Config(
      host          = f'https://{server_nm}',
      client_id     = client_id,
      client_secret = client_secret
    )
    
    credential_provider = lambda: oauth_service_principal(config)
    
    cnxn =  sql.connect(
 	        server_hostname = server_nm,
 	        http_path       = http_path,
 	        credentials_provider = credential_provider
    )
    
    return cnxn


def databricks_to_df(query: str, databricks_secret: dict, polars=False):
    with authen_databrick_sql(databricks_secret=databricks_secret) as conn:
        if polars:
            try:
                import polars as pl
            except ImportError:
                warnings.warn('Polars not installed. Falling back to pandas.')
                polars = False

        if polars:
            # Execute the query
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Fetch the results
                data = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Convert to Polars DataFrame
                df = pl.DataFrame(data, schema=columns, orient='row', infer_schema_length=None)
        else:
            df = pd.read_sql(query, conn)
        
    return df
