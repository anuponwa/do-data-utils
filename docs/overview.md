# Subpackage: `google`
Utilities for interacting with Google Cloud

- `get_secret(secret_info: dict, project_id: str, secret_id: str, version_id='latest')` – Retrive secret info from Google Secret Manager
- `gcs_listdirs(gcspath: str, secret: dict, subdirs_only=True, trailing_slash=False)` – Lists directories in GCS
- `gcs_listfiles(gcspath: str, secret: dict, files_only=True)` – List files in GCS
- `gcs_exists(gcspath: str, secret: dict)` – Checks whether the given gcspath exists or not
- `gcs_to_dict(gcspath: str, secret: dict)` – Downloads a JSON file in GCS to a dictionary
- `gcs_to_file(gcspath: str, secret: dict)` – Downloads a GCS file to IO

# Subpackage: `azure`
Utilities for interacting with Azure

- `databricks_to_df(query: str, secret: dict, polars=False)` – Retrieve the data from Databricks SQL in a DataFrame