#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools

from iambic import ast


@functools.lru_cache()
def parser(data: str, *, __trans=ast.protocol.transmute) -> ast.ResolvedNodeT:
    return __trans(data)
