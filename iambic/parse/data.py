#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
import ujson as json

from iambic import ast


class Parser:
    __resolver_map__ = ast.GenericNode.__resolver_map__

    @functools.lru_cache()
    def parse(self, data: str) -> ast.ResolvedNode:
        data = json.loads(data) if isinstance(data, str) else data
        handler = self.__resolver_map__[data.pop("type")]
        return handler(**data)

    __call__ = parse


parser = Parser()
