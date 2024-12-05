# datautils

This package provides you the functionalities to connect to different cloud sources and data cleaning functions.

## Installation

### Commands

To install the latest version from `main` branch, use the following command:
```bash
pip install "git+https://github.com/anuponwa/datautils.git"
```
You can install a specific version like so:
```bash
pip install "git+https://github.com/anuponwa/datautils.git@<version>"
```
For example,
```bash
pip install "git+https://github.com/anuponwa/datautils.git@1.0.0"
```

Extra options can be inspected in `setup.py` in the `extras_require` option.

### Install in requirements.txt

You can also put this source in the `requirements.txt`.
```python
# requirements.txt
git+https://github.com/anuponwa/datautils.git@1.0.0
```

## Available Subpackages
- `google` – Utilities for Google Cloud Platform.
- `azure` – Utilities for Azure services.

For a full list of functions, see the [overview documentation](docs/overview.md).

## Example Usage

`datautils` provides (as of version 1.0.0) 2 sub-packages: google and azure. Depending on where you want to interact, import your sub-package of choice.

### Google

## GCS

```python
from datautils.google import get_secret, gcs_to_file


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='gcs-secret-id-dev')

# Download the content from GCS
gcspath = 'gs://my-ai-bucket/my-path-to-json.json'
f = gcs_to_file(gcspath, secret=secret)
my_dict = json.load(f)
```

## GBQ

```python
from datautils.google import get_secret, gbq_to_df


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
from datautils.azure import databricks_to_df


# Load secret key and get the secret to access GCS
with open('secrets/secret-manager-key.json', 'r') as f:
    secret_info = json.load(f)

secret = get_secret(secret_info, project_id='my-secret-project-id', secret_id='databricks-secret-id-dev')

# Download from Databricks sql
query = 'select * from datadev.dsplayground.my_table'
df = databricks_to_df(query, secret, polars=False)
```