# -*- coding: utf-8 -*-
"""
    azure sub-package
    ~~~~
    Provides to all the useful functionalities in Azure.
    If the dependencies are not installed, the warnings will be thrown.
"""

import warnings

try:
    from .azureutils import authen_databrick_sql, databricks_to_df
except:
    warnings.warn('Azure utilities not imported. If you want to use them, please install them via: pip install "git+https://github.com/anuponwa/datautils.git@<version>#egg=datautils[azure]"')
