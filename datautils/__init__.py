# -*- coding: utf-8 -*-
"""
    datautils
    ~~~~
    datautils provides you the functionalities to connect to different cloud sources.
    datautils also comes with common data cleaning functions.
"""

import warnings

from version import __version__
import google

try:
    import azure
except:
    warnings.warn('Azure utilities not imported. If you want to use them, please install them via: pip install "git+https://github.com/anuponwa/datautils.git@<version>#egg=datautils[azure]"')