#!/usr/bin/env python
# -*- coding: UTF-8 -*-

TABLE = {
    "Dramatis Personae": ["Foo", "A Bar", "Bar's Foo", "Bar"],
    "First Appearance": [2, 4, 6, 12],
    "Lines": [5, 1, 1, 3],
    "P": ["X", "X", "X", ""],
    "I.P": ["", "", "", "X"],
    "INT": ["", "", "", ""],
    "I.i": ["X", "", "", "X"],
    "I.E": ["X", "", "", ""],
}

MATRIX = [
    ("Dramatis Personae", "First Appearance", "Lines", "P", "I.P", "INT", "I.i", "I.E"),
    ("Foo", 2, 5, "X", "", "", "X", "X"),
    ("A Bar", 4, 1, "X", "", "", "", ""),
    ("Bar's Foo", 6, 1, "X", "", "", "", ""),
    ("Bar", 12, 3, "", "X", "", "X", ""),
]
