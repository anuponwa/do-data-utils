# -*- coding: utf-8 -*-
"""
    google sub-package
    ~~~~
    Provides to all the useful functionalities in Google.
"""

from .gcputils import (
    get_secret,
    gcs_exists,
    gcs_listdirs,
    gcs_listfiles,
    gcs_to_dict,
    gcs_to_file,
    set_gcs_client
)