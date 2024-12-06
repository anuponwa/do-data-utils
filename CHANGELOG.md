# Change Log

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