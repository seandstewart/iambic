#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import typic

from iambic import parse, render
from tests.static import MD_RAW


def test_json():
    parsed = parse.text(MD_RAW)
    assert render.json(parsed) == typic.tojson(
        parsed, indent=2, escape_forward_slashes=False
    )
