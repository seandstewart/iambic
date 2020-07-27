#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools

import typic

from iambic import ast


class Parser:
    __resolver_map__ = ast.GenericNode.__resolver_map__

    @functools.lru_cache()
    def parse(self, data: str) -> ast.ResolvedNodeT:
        return typic.transmute(ast.ResolvedNodeT, data)  # type: ignore

    __call__ = parse


parser = Parser()
