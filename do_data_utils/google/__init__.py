# -*- coding: utf-8 -*-
"""
    google sub-package
    ~~~~
    Provides to all the useful functionalities and allows you to interact with GCP.
"""

from .google_secret import get_secret, list_secrets

from .gcputils import (
    gcs_exists,
    gcs_listdirs,
    gcs_listfiles,
    gcs_to_dict,
    gcs_to_df,
    df_to_gcs,
    dict_to_json_gcs,
    gcs_to_file,
    file_to_gcs,
    download_folder_gcs,
    upload_folder_gcs
)

from .gbqutils import gbq_to_df, df_to_gbq

__all__ = [
    "get_secret",
    "list_secrets",
    "gcs_exists",
    "gcs_listdirs",
    "gcs_listfiles",
    "gcs_to_dict",
    "gcs_to_df",
    "df_to_gcs",
    "dict_to_json_gcs",
    "gbq_to_df",
    "df_to_gbq",
    "gcs_to_file",
    "file_to_gcs",
    "download_folder_gcs",
    "upload_folder_gcs"
]
