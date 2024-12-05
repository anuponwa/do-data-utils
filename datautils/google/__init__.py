# -*- coding: utf-8 -*-
"""
    google sub-package
    ~~~~
    Provides to all the useful functionalities and allows you to interact with GCP.
"""

from .gcputils import (
    get_secret,
    gcs_exists,
    gcs_listdirs,
    gcs_listfiles,
    gcs_to_dict,
    gcs_to_file
)