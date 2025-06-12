# -*- coding: utf-8 -*-
"""
azure sub-package
~~~~
Provides to all the useful functionalities and allows you to interact with Azure.
"""

from .azureutils import databricks_to_df
from .keyvault import get_secret
from .storage import (
    azure_storage_delete_path,
    azure_storage_list_files,
    azure_storage_to_df,
    azure_storage_to_dict,
    azure_storage_to_file,
    df_to_azure_storage,
    file_to_azure_storage,
)

__all__ = [
    "databricks_to_df",
    "azure_storage_delete_path",
    "azure_storage_list_files",
    "azure_storage_to_dict",
    "azure_storage_to_file",
    "azure_storage_to_df",
    "df_to_azure_storage",
    "file_to_azure_storage",
    "get_secret",
]
