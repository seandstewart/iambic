#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import typic

from iambic import parse
from tests.static import MD_RAW

JSON = typic.tojson(parse.text(MD_RAW))


def test_data():
    parsed = parse.text(MD_RAW)
    data = parse.data(JSON)
    assert data == parsed
