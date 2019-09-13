#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
from iambic import parse
from tests.static import MD_RAW


def test_data():
    parsed = parse.text(MD_RAW)
    data = parse.data(json.dumps(parsed.primitive()))
    assert data.primitive() == parsed.primitive()
