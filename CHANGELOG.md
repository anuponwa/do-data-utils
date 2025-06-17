# Change Log

## 4.2.1
* Fix `df_to_azure_storage()` function for csv file type. Now uses `Bytes` object to upload.

## 4.2.0
* Add `azure_storage_delete_path()` function
* Add `azure_storage_to_dict()` function
* Support to recursively or non-recursively list files in Azure datalake storage
* Add `get_secret()` function from Azure keyvault

## 4.1.0
* Add `.parquet` file support for `df_to_gcs()` function

## 4.0.0
* Add support for Google (application) default credentials (ADC) in `list_secrets()` and `get_secret()`

## 3.2.4
* Fix bug in `download_folder_gcs()`

## 3.2.3
* Fix dependencies, more lenient in `pandas` and `polars` versions.

## 3.2.2
* Add `db-dtypes` dependency to fix `gbq_to_df()` function

## 3.2.1
* Fix empty Excel file when uploading to GCS

## 3.2.0
* Add support for `secret=None` in `azure_storage` module to download and upload to Azure Storage
* The `DefaultAzureCredential` will be used if `secret` is `None`
* But it requires `storage_account_name` parameter
* Add corresponding tests

## 3.1.0
* Add `delimiter` parameter in `preprocessing`'s `email` and `phone` modules
* Add corresponding tests
* Remove bare except clauses
* Format some parts of the code

## 3.0.0b1
* Update to `uv`
* Get rid of requirements and setuptools
* Update github actions to `uv`

## 3.0.0
**Breaking features**
* Revamp the Azure Storage related functions
* Re-design (internally) how the credentials are authenticated
* Change the parameters' names and number of parameters in each function
* Use Data Lake Gen2 instead of legacy blob

## 2.7.1
* Fix upload Excel to Sharepoint

## 2.7.0
* Add support for downloading and uploading .csv and .parquet file to/from a DataFrame
* Add tests

## 2.6.0
* Add support for downloading and uploading to Azure blob storage
* Add tests

## 2.5.0
* Add support for using default account in cloud environment
* Add files and folders download and upload functionalities with GCS
* Add tests to make coverage >= 90%

## 2.4.0
* Add upload to Sharepoint support.
* You can now upload from local file or a `pd.DataFrame`.
* `polars` is now part of the library.
* Add some tests.

## 2.3.2
* Use context manager in saving Excel to GCP
* Add checks in `gcspath` input of GCS JSON upload function
* Add a bunch of unittests relating to GBQ, uploading files, and Azure

## 2.3.1
* Fix return in `clean_phone()` in some cases where it returned `''` instead of `None`
* Add a bunch of unittests
* Add Github actions workflows to automate CI/CD testing and deployment

## 2.3.0
* Add options to pass in the secret file path instead of dict in `get_secret()`
* Other GBQ and GCS functions also have this option. `secret` can be a type of `dict` or `str` that ends with '.json'
* Add `as_json` option, (default `as_json=False`) in `get_secret()` to allow backward-compatibility and ease of use to the user in case the secret is in JSON form

## 2.2.0
* Add `preprocessing` subpackage
* Allows you to clean and extract valid citizen ID, email, phones (specific to Thai)

## 2.1.0
* Add `pathutils` subpackage
* `add_project_root(levels_up=1)` function adds higher level directory to sys.path

## 2.0.0
* Re-design google_secret functions - the `project_id` will now be inferred from the given secret
* `list_secrets()` function will now return only the names of the secrets (not their full paths)

**Breaking features**
* Remove `project_id` from functions' argument
* Re-align some of the functions' arguments

## 1.2.2
* Fix version bug

## 1.2.1
* Fix version bug

## 1.2.0
* Add `list_secrets()` function to list all the available secrets

## 1.1.4
* Support `'catalog'` key in secret for Azure Databricks

## 1.1.3
Update docs

## 1.1.2
Update instructions

## 1.1.1
* Changed to do-data-utils
* Published to PyPI

## 1.1.0
Added support for GBQ and GCS functions
### GBQ
* `gbq_to_df()` function
* `df_to_gbq()` function

### GCS
* Download .csv or .xlsx in GCS to DataFrame
* Upload related functions, e.g., `df_to_gcs()`, `dict_to_json_gcs()`

## 1.0.0

### First version
Our first version provides the following functionalites:
* Get secret from GCP secret manager
* Get files from GCS
* List files in a GCS bucket or folder
* Get data from Azure Databricks
