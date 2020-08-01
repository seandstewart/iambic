#!/usr/bin/env python
# -*- coding: UTF-8 -*-

TABLE = {
    "Dramatis Personae": ["Foo", "A Bar", "Bar's Foo", "Bar"],
    "First Appearance": [2, 4, 6, 12],
    "I: Epilogue": ["X", "", "", "O"],
    "I: Prologue": ["", "", "", "X"],
    "I: i": ["X", "", "", "X"],
    "Intermission": ["", "", "", ""],
    "Lines": [5, 1, 1, 3],
    "Prologue": ["X", "X", "X", ""],
}

MATRIX = [
    (
        "Dramatis Personae",
        "First Appearance",
        "I: Epilogue",
        "I: Prologue",
        "I: i",
        "Intermission",
        "Lines",
        "Prologue",
    ),
    ("Foo", 2, "X", "", "X", "", 5, "X"),
    ("A Bar", 4, "", "", "", "", 1, "X"),
    ("Bar's Foo", 6, "", "", "", "", 1, "X"),
    ("Bar", 12, "O", "X", "X", "", 3, ""),
]
