# Subpackage: `google`
Utilities for interacting with Google Cloud

## Common
- `get_secret(secret_info: dict, project_id: str, secret_id: str, version_id='latest')` – Retrieve secret info from Google Secret Manager
- `list_secrets(project_id: str, secret_info: dict)` – List all the available secrets in a `project_id`

## GCS related
### Downloading and checking files
- `gcs_listdirs(gcspath: str, secret: dict, subdirs_only=True, trailing_slash=False)` – Lists directories in GCS
- `gcs_listfiles(gcspath: str, secret: dict, files_only=True)` – Lists files in GCS
- `gcs_exists(gcspath: str, secret: dict)` – Checks whether the given gcspath exists or not
- `gcs_to_df(gcspath: str, secret: dict, polars=False, **kwargs)` – Downloads .csv or .xlsx to DataFrame
- `gcs_to_dict(gcspath: str, secret: dict)` – Downloads a JSON file in GCS to a dictionary
- `gcs_to_file(gcspath: str, secret: dict)` – Downloads a GCS file to IO

### Uploading to GCS
- `df_to_gcs(df, gcspath: str, secret: dict, **kwargs)` – Saves a pandas.DataFrame (to any file type, e.g., .csv or .xlsx) and uploads to GCS
- `dict_to_json_gcs(dict_data: dict, gcspath: str, secret: dict)` – Uploads a dictionary to a JSON file

## GBQ related
- `gbq_to_df(query: str, secret: dict, polars: bool=False)` – Retrieves the data from Google Bigquery to a DataFrame
- `df_to_gbq(df, gbq_tb: str, secret: dict, if_exists: str='fail', table_schema=None)` – Uploads a pandas.DataFrame to Google Bigquery


# Subpackage: `azure`
Utilities for interacting with Azure

- `databricks_to_df(query: str, secret: dict, polars=False)` – Retrieves the data from Databricks SQL in a DataFrame


# Subpackage: `pathutils`
Utilities related to paths

- `add_project_root(levels_up: int=1)` – Appends the project root directory to sys.path

# Subpackage: `preprocessing`
Utilities for data preprocessing

- `clean_citizenid(id_str: str)` – Cleans the given 13-digit ID
- `clean_email(email: str)` – Cleans the e-mail
- `clean_phone(phone: str, exclude_numbers: Optional[list]=None)` – Cleans phone numbers and outputs a list of valid phone numbers