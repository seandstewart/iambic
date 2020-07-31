#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from iambic import parse, render
from tests.static import MD_RAW, MD_RENDERED


def test_markdown():
    parsed = parse.text(MD_RAW)
    assert render.markdown(parsed) == MD_RENDERED
