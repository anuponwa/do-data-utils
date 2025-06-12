# do-data-utils

![Static Typed Checks](https://github.com/anuponwa/do-data-utils/actions/workflows/static-checking.yml/badge.svg)
![Continuous Testing](https://github.com/anuponwa/do-data-utils/actions/workflows/continuous-testing.yml/badge.svg)
![Publish Tag to PyPI](https://github.com/anuponwa/do-data-utils/actions/workflows/publish-tag-to-pypi.yml/badge.svg)

This package provides you the functionalities to connect to different cloud sources and data cleaning functions.
Package repo on PyPI: [do-data-utils - PyPI](https://pypi.org/project/do-data-utils/)

**For a full list of functions, see the [overview documentation](https://github.com/anuponwa/do-data-utils/blob/main/docs/overview.md).**

## Installation

### Commands

To install the latest version from `main` branch, use the following command:
```bash
pip install do-data-utils
```

## Available Subpackages
- `google` – Utilities for Google Cloud Platform.
- `azure` – Utilities for Azure services.
- `pathutils` – Utilities related to paths.
- `preprocessing` – Utilities for data preprocessing.
- `sharepoint` - Utilities for interacting with Microsoft Sharepoint.

For a full list of functions, see the [overview documentation](https://github.com/anuponwa/do-data-utils/blob/main/docs/overview.md).


## Example Usage

The concept of using this revolves around the idea that:
1. You keep service account JSON secrets (for cloud services) in GCP secret manager
2. You have local JSON secret file for accessing the GCP secret manager
3. Retrive the secret you want to interact with cloud platform from GCP secret manager
4. Do your stuff...


### Google

#### GCS
##### Download

```python
from do_data_utils.google import get_secret, gcs_to_df


# Load secret key and get the secret to access GCS
secret_path = 'secrets/secret-manager-key.json'
secret = get_secret(secret_id='gcs-secret-id-dev', secret=secret_path, as_json=True)

# Download a csv file to DataFrame
gcspath = 'gs://my-ai-bucket/my-path-to-csv.csv'
df = gcs_to_df(gcspath, secret, polars=False)
```


```python
from do_data_utils.google import get_secret, gcs_to_dict


# Load secret key and get the secret to access GCS
secret_path = 'secrets/secret-manager-key.json'
secret = get_secret(secret_id='gcs-secret-id-dev', secret=secret_path, as_json=True)

# Download the content from GCS
gcspath = 'gs://my-ai-bucket/my-path-to-json.json'
my_dict = gcs_to_dict(gcspath, secret=secret)
```

##### Upload
```python
from do_data_utils.google import get_secret, dict_to_json_gcs


# Load secret key and get the secret to access GCS
secret_path = 'secrets/secret-manager-key.json'

# No need to read in the secret info from version 2.3.0
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

# you can pass in either dict or path to JSON in `secret` argument
secret = get_secret(secret_id='gcs-secret-id-dev', secret=secret_info, as_json=True)

my_setting_dict = {
    'param1': 'abc',
    'param2': 'xyz',
}

gcspath = 'gs://my-bucket/my-path-to-json.json'
dict_to_json_gcs(dict_data=my_setting_dict, gcspath=gcspath, secret=secret)
```

#### GBQ

```python
from do_data_utils.google import get_secret, gbq_to_df


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

# you can pass in either dict or path to JSON in `secret` argument
secret = get_secret(secret_id='gbq-secret-id-dev', secret=secret_info, as_json=True)

# Query
query = 'select * from my-project.my-dataset.my-table'
df = gbq_to_df(query, secret, polars=False)
```


### Azure/Databricks

```python
from do_data_utils.azure import databricks_to_df


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_id='databricks-secret-id-dev', secret=secret_info, as_json=True)

# Download from Databricks sql
query = 'select * from datadev.dsplayground.my_table'
df = databricks_to_df(query, secret, polars=False)
```

For more functions, see the [overview documentation](https://github.com/anuponwa/do-data-utils/blob/main/docs/overview.md).

### Path utils

```python
from do_data_utils.pathutils import add_project_root

# Adds your root folder to sys.path,
# so you can do imports from the root directory
add_project_root(levels_up=1)
```


### Preprocessing

```python
from do_data_utils.preprocessing import clean_phone, clean_citizenid

phone_numbers = '090-123-4567|0912345678|0901234567-9'
phones_valid = clean_phone(phone_numbers) # Gets the valid phone numbers

citizenid = '0123456789012'
citizenid_cleaned = clean_citizenid(citizenid)
```

### Sharepoint

```python
import pandas as pd
from do_data_utils.google import get_secret
from do_data_utils.sharepoint import df_to_sharepoint

# Load secret key and get the secret to access GCS
secret_path = "secrets/secret-manager-key.json"

ms_secret = get_secret(secret_id="sharepoint-secret", secret=secret_path, as_json=True)
refresh_token = get_secret(
    secret_id="sharepoint-refresh-token", secret=secret_path, as_json=False
)

# Example DataFrame
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

site = "your-site"
sharepoint_dir = "Shared Documents/some/path"
file_name = "output.xlsx"  # or .csv if you wish

df_to_sharepoint(
    df,
    site=site,
    sharepoint_dir=sharepoint_dir,
    file_name=file_name,
    secret=ms_secret,
    refresh_token=refresh_token,
)
```
