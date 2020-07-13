#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
import functools
import re

NUMERAL_PATTERN = re.compile(
    """
    ^                   # beginning of string
    M{0,4}              # thousands - 0 to 4 M's
    (CM|CD|D?C{0,3})    # hundreds - 900 (CM), 400 (CD), 0-300 (0 to 3 C's),
                        #            or 500-800 (D, followed by 0 to 3 C's)
    (XC|XL|L?X{0,3})    # tens - 90 (XC), 40 (XL), 0-30 (0 to 3 X's),
                        #        or 50-80 (L, followed by 0 to 3 X's)
    (IX|IV|V?I{0,3})    # ones - 9 (IX), 4 (IV), 0-3 (0 to 3 I's),
                        #        or 5-8 (V, followed by 0 to 3 I's)
    $                   # end of string
    """,
    re.VERBOSE,
)


class RomanNumeral(int, enum.Enum):
    M = 1000
    CM = 900
    D = 500
    CD = 400
    C = 100
    XC = 90
    L = 50
    XL = 40
    X = 10
    IX = 9
    V = 5
    IV = 4
    I = 1  # noqa: E741

    @classmethod
    @functools.lru_cache(maxsize=5000)
    def from_number(cls, num: int) -> str:
        """Get a Roman Numeral Notation for a given integer.

        Examples
        --------
        >>> RomanNumeral.from_number(1)
        'I'
        >>> RomanNumeral.from_number(5000)
        'MMMMM'
        >>> RomanNumeral.from_number(3724)
        'MMMDCCXXIV'
        """
        try:
            num = int(num)
            assert num <= 5000
        except (AssertionError, ValueError):
            raise ValueError(
                f"Input must be a valid integer <=5000. Provided: <{num}>"
            ) from None

        result = ""
        for notation in cls:
            name, value = notation.name, notation.value
            while num >= value:
                result += name
                num -= value

        return result

    @classmethod
    @functools.lru_cache(maxsize=5000)
    def to_number(cls, num: str) -> int:
        """Get an integer from a valid Roman Numeral Notation.

        Examples
        --------
        >>> RomanNumeral.to_number('I')
        1
        >>> RomanNumeral.to_number('MMMMM')
        5000
        >>> RomanNumeral.to_number('MMMDCCXXIV')
        3724
        """
        try:
            assert num
            assert NUMERAL_PATTERN.search(num) or num == "MMMMM"
        except AssertionError:
            raise ValueError(
                f"Input must be a valid Roman Numeral no greater than <MMMMM>. "
                f"Provided: <{num}>"
            ) from None

        result = 0
        index = 0
        for notation in cls:
            while num[index : index + len(notation.name)] == notation.name:
                result += notation
                index += len(notation.name)

        return result


numeral = RomanNumeral.from_number
integer = RomanNumeral.to_number
