# -*- coding: utf-8 -*-
"""
azure sub-package
~~~~
Provides to all the useful functionalities and allows you to interact with Azure.
"""

from .azureutils import databricks_to_df

from .storage import (
    file_to_azure_storage,
    azure_storage_to_file,
    azure_storage_list_files,
    df_to_azure_storage,
    azure_storage_to_df
)

__all__ = [
    "databricks_to_df",
    "file_to_azure_storage",
    "azure_storage_to_file",
    "azure_storage_list_files",
    "df_to_azure_storage",
    "azure_storage_to_df"
]
