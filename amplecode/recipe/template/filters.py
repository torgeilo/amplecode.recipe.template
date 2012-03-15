import re


def split(s):
    """
    Split a string on any whitespace.
    """

    return re.split("\s+", s.strip())


def as_bool(s):
    """
    Translate a string into a boolean.
    """

    return s.lower() in ("yes", "true", "1", "on")


template_filters = {
    "split": split,
    "as_bool": as_bool,
    "type": type,
}
