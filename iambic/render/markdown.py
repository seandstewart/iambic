#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from html2text import html2text

from iambic import ast
from .html import render_html


def render_markdown(tree: ast.Play, with_toc: bool = False) -> str:
    """The renderer for a Markdown document.

    This is including for convenience. The guts of the document rendering is housed in
    :class:`~iambic.render.html.HTMLRenderer`

    Parameters
    ----------
    tree :
        The play tree, as loaded via :func:`~iambic.parser.parse` or :func:`~iambic.loader.load`
    with_toc : default False
        Optionally render a TOC for your tree.

    See Also
    --------
    :class:`iambic.render.html.HTMLRenderer`
    """
    return html2text(render_html(tree, with_toc=with_toc))
