#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from .html import render_html as _render_html
from .json import render_json as _render_json
from .markdown import render_markdown as _render_markdown
from .table import tabulate as _tabulate

markdown = _render_markdown
html = _render_html
json = _render_json
table = _tabulate
