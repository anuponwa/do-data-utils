import functools
import re
from typing import Optional

from .common import search_regexp


def get_checksum(id_str: str) -> int:
    """Calculates the checksum of the 13-digit ID

    Parameters
    ----------
    id_str: str
        13-digit ID

    Returns
    -------
    int
        Checksum number
    """

    all_digits = list(
        map(lambda ele: (ele[0] + 1, int(ele[1])), list(enumerate(list(id_str))))
    )
    sum_ = functools.reduce(lambda a, b: a + ((14 - b[0]) * b[1]), all_digits[:-1], 0)
    x = sum_ % 11
    check_sum = 1 - x if x <= 1 else 11 - x
    return check_sum


def validate_citizen_id(id_str: str) -> bool:
    """Validates any 13-digit ID if the last digit is equal to its checksum

    Parameters
    ----------
    id_str: str
        13-digit ID

    Returns
    -------
    bool
        True if the ID passes the checksum test, else False
    """

    cal_checksum = get_checksum(id_str)
    digit_13rd = int(id_str[-1])
    return cal_checksum == digit_13rd


def clean_citizenid(id_str: str) -> Optional[str]:
    """Cleans the given 13-digit ID

    Parameters
    ----------
    id_str: str
        13-digit ID (can have spaces or dashes/hyphens('-'))

    Returns
    -------
    str or None
        Legitimate 13-digit ID if the ID passes all the conditions, else None
    """

    if not id_str:
        return None

    id_str = re.sub(r"\s|-", "", id_str)

    id_pat = r"\d{13}"
    id_extract = search_regexp(pattern=id_pat, string=id_str)

    if id_extract and validate_citizen_id(id_extract):
        return id_extract
    else:
        return None
