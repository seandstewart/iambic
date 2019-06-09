#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from iambic import parse, render
from tests.static import HTML, MD_RAW


def test_html():
    parsed = parse.text(MD_RAW)
    rendered = render.html(parsed)
    assert rendered.replace(" ", "").split() == HTML.replace(" ", "").split()
