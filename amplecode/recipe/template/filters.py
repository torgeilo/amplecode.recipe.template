import re


def split(s):
    """
    Strip and split a string on any whitespace.
    """

    s = s.strip()
    if s:
        return re.split("\s+", s)
    return []


def as_bool(s):
    """
    Translate a string into a boolean.
    """

    return s.lower() in ("yes", "true", "1", "on")


default_filters = {
    "split": split,
    "as_bool": as_bool,
    "type": type,
}
