#!/usr/bin/env python
# -*- coding: UTF-8 -*-

TABLE = {
    "Dramatis Personae": ["Foo", "A Bar", "Bar'S Foo", "Bar"],
    "Lines": [5, 1, 1, 3],
    "P": ["X", "X", "X", ""],
    "I.P": ["", "", "", "X"],
    "INT": ["", "", "", ""],
    "I.i": ["X", "", "", "X"],
    "I.E": ["X", "", "", ""],
}

MATRIX = [
    ("Dramatis Personae", "Lines", "P", "I.P", "INT", "I.i", "I.E"),
    ("Foo", 5, "X", "", "", "X", "X"),
    ("A Bar", 1, "X", "", "", "", ""),
    ("Bar'S Foo", 1, "X", "", "", "", ""),
    ("Bar", 3, "", "X", "", "X", ""),
]
