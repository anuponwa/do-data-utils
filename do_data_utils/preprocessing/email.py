from typing import Optional
from .common import search_regexp


def clean_email(email: str) -> Optional[str]:
    """Cleans the e-mail
    
    Parameters
    ----------
    email: str
        E-mail string, e.g., somename@somedomain.com

    Returns
    -------
    str
        A valid e-mail string, else None
    """

    if not email:
        return None
    
    email_pat = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
    return search_regexp(pattern=email_pat, string=email)