#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from html2text import html2text
from iambic import parse, render
from tests.static import HTML, MD_RAW


def test_markdown():
    parsed = parse.text(MD_RAW)
    assert render.markdown(parsed, with_toc=True).strip() == html2text(HTML).strip()
