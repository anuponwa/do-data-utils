# do-data-utils

This package provides you the functionalities to connect to different cloud sources and data cleaning functions.

## Installation

### Commands

To install the latest version from `main` branch, use the following command:
```bash
pip install do-data-utils
```
You can install a specific version, for example,
```bash
pip install do-data-utils==1.1.2
```

### Install in requirements.txt

You can also put this source in the `requirements.txt`.
```python
# requirements.txt

do-data-utils==1.1.2
```

## Available Subpackages
- `google` – Utilities for Google Cloud Platform.
- `azure` – Utilities for Azure services.

For a full list of functions, see the [overview documentation](docs/overview.md).


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
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='gcs-secret-id-dev')

# Download a csv file to DataFrame
gcspath = 'gs://my-ai-bucket/my-path-to-csv.csv'
df = gcs_to_df(gcspath, secret, polars=False)
```


```python
from do_data_utils.google import get_secret, gcs_to_dict


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='gcs-secret-id-dev')

# Download the content from GCS
gcspath = 'gs://my-ai-bucket/my-path-to-json.json'
my_dict = gcs_to_dict(gcspath, secret=secret)
```

##### Upload
```python
from do_data_utils.google import get_secret, dict_to_json_gcs


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='gcs-secret-id-dev')

my_setting_dict = {
    'param1': 'abc',
    'param2': 'xyz',
}

gcspath = 'gs://my-bucket/my-path-to-json.json'
dict_to_json_gcs(dict_data= my_setting_dict, gcspath=gcspath, secret=secret)
```

#### GBQ

```python
from do_data_utils.google import get_secret, gbq_to_df


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='gbq-secret-id-dev')

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

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='databricks-secret-id-dev')

# Download from Databricks sql
query = 'select * from datadev.dsplayground.my_table'
df = databricks_to_df(query, secret, polars=False)
```