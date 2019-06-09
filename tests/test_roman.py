#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest

from iambic import roman


@pytest.mark.parametrize(
    argnames=("value", "expected"),
    argvalues=[("I", 1), ("MMMMM", 5000), ("MMMDCCXXIV", 3724)],
)
def test_roman_integer(value, expected):
    assert roman.integer(value) == expected


@pytest.mark.parametrize(
    argnames=("value", "expected"),
    argvalues=[(1, "I"), (5000, "MMMMM"), (3724, "MMMDCCXXIV")],
)
def test_roman_numeral(value, expected):
    assert roman.numeral(value) == expected


def test_invalid_roman_numeral():
    with pytest.raises(TypeError):
        roman.integer("MMMMMI")


def test_invalid_roman_integer():
    with pytest.raises(TypeError):
        roman.numeral(5001)
