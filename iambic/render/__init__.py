#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# flake8: noqa
from .html import render_html as _render_html
from .json import render_json as _render_json
from .markdown import render_markdown as _render_markdown
from .table import tabulate as _tabulate

__all__ = ("markdown", "html", "json", "table")

markdown = _render_markdown
html = _render_html
json = _render_json
table = _tabulate
