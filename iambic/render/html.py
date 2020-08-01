#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools

from markdown import Markdown

from iambic import ast
from .markdown import render_markdown


EXTENSIONS = ("meta", "attr_list", "pymdownx.details", "tables", "pymdownx.tabbed")


@functools.lru_cache(maxsize=1)
def renderer(*extensions) -> Markdown:
    extensions = tuple(set(EXTENSIONS).union(set(extensions)))
    return Markdown(extensions=extensions)


def render_html(play: ast.Play, *extensions: str, table: bool = True) -> str:
    """Render a play instance as an html document

    This uses the `Python-Markdown` library for rendering the final html,
    so all extensions supported by that library are also supported with this function.

    Parameters
    ----------
    play
        The instance of `iambic.ast.Play`
    extensions
        Any additional Python-Markdown extensions.
    table : default True
        Optionally render a character mapping for your play.

    Returns
    -------
    str
        The HTML document.
    """
    text = render_markdown(play, table=table)
    return renderer(*extensions).convert(text)
