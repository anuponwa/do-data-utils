# -*- coding: utf-8 -*-
"""
    pathutils sub-package
    ~~~~
    Provides utility functions related to paths.
"""

import os
import sys


def add_project_root(levels_up: int = 1):
    """Appends the project root directory to sys.path.

    Parameters
    ----------
    levels_up: int
        Number of directory levels to go up. Defaults to 1.

    Returns
    -------
    None
    """

    if levels_up < 1 or not isinstance(levels_up, int):
        raise ValueError("`levels_up` must be a positive integer.")

    # Get the current directory
    current_dir = os.path.abspath(".")

    # Traverse up by the specified number of levels
    for _ in range(levels_up):
        current_dir = os.path.dirname(current_dir)

    # Append to sys.path if it's not already included
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        print(f"{current_dir} has been added in sys.path")
    else:
        print(f"{current_dir} already exists in sys.path")
