#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from iambic import parse
from tests.static import MD_RAW


def test_data():
    parsed = parse.text(MD_RAW)
    data = parse.data(parsed.json())
    assert data == parsed
