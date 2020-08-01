#!/usr/bin/env python
# -*- coding: UTF-8 -*-

TABLE = {
    "Act I: Epilogue": ["X", "", "", "O"],
    "Act I: Prologue": ["", "", "", "X"],
    "Act I: Scene I": ["X", "", "", "X"],
    "Dramatis Personae": ["Foo", "A Bar", "Bar's Foo", "Bar"],
    "First Appearance": [2, 4, 6, 12],
    "Intermission": ["", "", "", ""],
    "Lines": [5, 1, 1, 3],
    "Prologue": ["X", "X", "X", ""],
}

MATRIX = [
    (
        "Act I: Epilogue",
        "Act I: Prologue",
        "Act I: Scene I",
        "Dramatis Personae",
        "First Appearance",
        "Intermission",
        "Lines",
        "Prologue",
    ),
    ("X", "", "X", "Foo", 2, "", 5, "X"),
    ("", "", "", "A Bar", 4, "", 1, "X"),
    ("", "", "", "Bar's Foo", 6, "", 1, "X"),
    ("O", "X", "X", "Bar", 12, "", 3, ""),
]
