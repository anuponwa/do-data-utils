# Subpackage: `google`
Utilities for interacting with Google Cloud

## Common
- `get_secret(secret_id: str, secret: Optional[Union[dict, str]], as_json: bool=False, version_id: Union[str, int]='latest')` – Retrieve secret info from Google Secret Manager
- `list_secrets(secret: Optional[Union[dict, str]])` – List all the available secrets in the secret manager that the `secret` has access to

## GCS related
### Downloading and checking files
- `gcs_listdirs(gcspath: str, secret: Optional[Union[dict, str]], subdirs_only=True, trailing_slash=False)` – Lists directories in GCS
- `gcs_listfiles(gcspath: str, secret: Optional[Union[dict, str]], files_only=True)` – Lists files in GCS
- `gcs_exists(gcspath: str, secret: Optional[Union[dict, str]])` – Checks whether the given gcspath exists or not
- `gcs_to_df(gcspath: str, secret: Optional[Union[dict, str]], polars=False, **kwargs)` – Downloads .csv or .xlsx to DataFrame
- `gcs_to_dict(gcspath: str, secret: Optional[Union[dict, str]])` – Downloads a JSON file in GCS to a dictionary
- `gcs_to_file(gcspath: str, secret: Optional[Optional[Union[dict, str]]] = None)` – Downloads a GCS file to local directory
- `download_folder_gcs(gcspath: str, local_dir: str, secret: Optional[Optional[Union[dict, str]]] = None)` – Downloads an entire GCS directory to local directory


### Uploading to GCS
- `df_to_gcs(df, gcspath: str, secret: Optional[Union[dict, str]], **kwargs)` – Saves a pandas.DataFrame (to any file type, e.g., .csv or .xlsx) and uploads to GCS
- `dict_to_json_gcs(dict_data: dict, gcspath: str, secret: Optional[Union[dict, str]])` – Uploads a dictionary to a JSON file
- `file_to_gcs(file_path: str, gcspath: str, secret: Optional[Optional[Union[dict, str]]] = None)` – Uploads a local file to GCS
- `upload_folder_gcs(local_dir: str, gcspath: str, secret: Optional[Optional[Union[dict, str]]] = None)` – Uploads an entire local directory to GCS

## GBQ related
- `gbq_to_df(query: str, secret: Optional[Union[dict, str]], polars: bool=False)` – Retrieves the data from Google Bigquery to a DataFrame
- `df_to_gbq(df, gbq_tb: str, secret: Optional[Union[dict, str]], if_exists: str='fail', table_schema=None)` – Uploads a pandas.DataFrame to Google Bigquery


# Subpackage: `azure`
Utilities for interacting with Azure

- `databricks_to_df(query: str, secret: dict, polars=False)` – Retrieves the data from Databricks SQL in a DataFrame

- `file_to_azure_storage(src_file_path: str, container_name: str, dest_file_path: str, secret: Optional[dict] = None, overwrite: bool = True, storage_account_name: Optional[str] = None)` – Uploads a file to Azure blob storage

- `azure_storage_to_file(container_name: str, file_path: str, secret: Optional[dict] = None, storage_account_name: Optional[str] = None)` – Downloads a file from Azure blob storage

- `azure_storage_list_files(container_name: str, directory_path: str, secret: Optional[dict] = None, files_only: bool = True, storage_account_name: Optional[str] = None)` – Lists files in Azure storage container

- `df_to_azure_storage(df: pd.DataFrame, container_name: str, dest_file_path: str, secret: Optional[dict] = None, overwrite: bool = True, storage_account_name: Optional[str] = None, **kwargs)` – Uploads a DataFrame to Azure blob storage

- `azure_storage_to_df(container_name: str, file_path: str, secret: Optional[dict] = None, polars: bool = False, storage_account_name: Optional[str] = None, **kwargs)` – Downloads a csv or parquet file into a DataFrame


# Subpackage: `pathutils`
Utilities related to paths

- `add_project_root(levels_up: int=1)` – Appends the project root directory to sys.path

# Subpackage: `preprocessing`
Utilities for data preprocessing

- `clean_citizenid(id_str: str)` – Cleans the given 13-digit ID
- `clean_email(email: str)` – Cleans the e-mail
- `clean_phone(phone: str, exclude_numbers: Optional[list]=None)` – Cleans phone numbers and outputs a list of valid phone numbers


# Subpackage: `sharepoint`
Utilities for interacting with Microsoft Sharepoint

- `file_to_sharepoint(site: str, sharepoint_dir: str, file_name: str, secret: dict, refresh_token: str, scopes: Optional[list[str]] = None)` – Uploads a file to Sharepoint
- `df_to_sharepoint(df: pd.DataFrame, site: str, sharepoint_dir: str, file_name: str, secret: dict, refresh_token: str, scopes: Optional[list[str]] = None)` – Uploads a DataFrame to Sharepoint
- `get_msal_app(secret: dict)` – Gets the MSAL client
- `get_access_token(msal_app, refresh_token: str, scopes: Optional[list[str]] = None)` – Use an MSAL client with a refresh token to get an access token (a wrapper of `acquire_token_by_refresh_token()` function from MSAL client)