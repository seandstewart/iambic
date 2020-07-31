#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# flake8: noqa
import pathlib

from .table import TABLE, MATRIX
from .parsed import PARSED

DIR = pathlib.Path(__file__).parent
HTML = (DIR / "foo.html").read_text()
MD_RAW = (DIR / "foo-raw.md").read_text()
MD_RENDERED = (DIR / "foo-rendered.md").read_text()
JSON = (DIR / "foo.json").read_text()
DATASET = (DIR / "dataset").read_text().rstrip("\n")
