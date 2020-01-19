"""
Some useful utility functions.

"""

__all__ = ["SymbolNotFoundError", "PageLoadError",
           "extract_text_between_expressions"]


class SymbolNotFoundError(IOError):
    pass


class BadFileVersionError(IOError):
    pass


class PageLoadError(IOError):
    pass


class CorruptDaraError(IOError):
    pass


def extract_text_between_expressions(input_str, from_str, to_str):
    """Find the text between from_str to to_str, excluding from_str
    and to_str. Raises an error if from_expr and to_expr are not found.

    parameters
    --------
    input_str: str
        input string
    from_str: str
        starting string
    to_str: str
        ending string

    returns
    --------
    :str
        the expression between from_str and to_str
    """
    ind_start = input_str.find(from_str)
    assert ind_start >= 0
    ind_start += len(from_str)

    ind_end = input_str.find(to_str, ind_start)
    assert ind_end >= 0

    return input_str[ind_start:ind_end]

