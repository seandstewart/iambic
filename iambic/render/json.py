#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import typic

from iambic import ast


def render_json(tree: ast.Play) -> str:
    """The renderer for a JSON document.

    This callable accepts a :class:`ast.PlayTree` and returns a valid JSON document.
    It's mainly included for api-completion, since it actually just accesses already public properties.

    Parameters
    ----------
    tree
        The play tree, as loaded via :func:`iambic.parse.text` or :func:`iambic.parse.data`
    """
    return typic.tojson(tree, indent=2, escape_forward_slashes=False)
