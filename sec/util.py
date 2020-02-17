"""
Some useful utility functions.

"""

__all__ = ["SymbolNotFoundError", "PageLoadError",
           "extract_text_between_expressions"]

import re


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


def find_dollar_units(title_str):
    """
    Finds the dollar unit based on the input string
    :param title_str: (str)         table title
    :return: (int)                  dollar unit
    """
    _1_regs = [r"usd\s*\(\$\)\s*$", r"\(usd\s*\$\)\s*$", r"usd\s*\(\$\)\s*shares in.*$"]
    _1e3_regs = [r"\$\)?\s*in\s*{}?".format("thousands")]
    _1e6_regs = [r"\$\)?\s*in\s*{}?".format("millions")]
    _1e9_regs = [r"\$\)?\s*in\s*{}?".format("billions")]
    for reg_exp in _1e3_regs:
        if len(re.findall(reg_exp, title_str.lower())) > 0:
            return 1e3
    for reg_exp in _1e6_regs:
        if len(re.findall(reg_exp, title_str.lower())) > 0:
            return 1e6
    for reg_exp in _1e9_regs:
        if len(re.findall(reg_exp, title_str.lower())) > 0:
            return 1e9
    for reg_exp in _1_regs:
        if len(re.findall(reg_exp, title_str.lower())) > 0:
            return 1
    if title_str.find("$") < 0:
        return 1
    file = open("debug/error_find_dollar_units.log", "a+")
    file.write(title_str + "\n")
    file.close()
    return 1