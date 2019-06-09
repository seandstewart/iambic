#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from iambic import parse, render
from tests.static import MD_RAW


def test_json():
    parsed = parse.text(MD_RAW)
    assert render.json(parsed) == parsed.json()
