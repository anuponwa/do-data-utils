from typing import Optional

from .common import search_regexp


def clean_email(email: str, delimiter: Optional[str] = None) -> Optional[str]:
    """Cleans the e-mail.

    Parameters
    ----------
    email: str
        E-mail string, e.g., somename@somedomain.com.

    delimiter: str, default=None
        A delimiter character to separate multiple emails.
        If None, it expects that email is not delimited.

    Returns
    -------
    str
        A valid e-mail string, else None.
    """

    if not email:
        return None

    email_pat = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"

    if not delimiter:
        return search_regexp(pattern=email_pat, string=email)

    else:
        ret = []
        email_list = email.split(delimiter)
        for e in email_list:
            email_extracted = search_regexp(pattern=email_pat, string=e)
            if email_extracted:
                ret.append(email_extracted)

        if ret:
            return delimiter.join(ret)

        return None
