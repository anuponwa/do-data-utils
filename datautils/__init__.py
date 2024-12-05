# -*- coding: utf-8 -*-
"""
    datautils
    ~~~~
    datautils provides you the functionalities to connect to different cloud sources.
    datautils also comes with common data cleaning functions.
"""


from .google import (
    get_secret,
    set_gcs_client,
    gcs_exists,
    gcs_listdirs,
    gcs_listfiles,
    gcs_to_dict,
    gcs_to_file
)

try:
    from .azure import authen_databrick_sql, databricks_to_df
except:
    raise ImportError('Azure utilities not imported. If you want to use them, please install them via: pip install "git+https://github.com/anuponwa/datautils.git@<version>#egg=datautils[azure]"')