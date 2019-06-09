#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import ujson as json
from cachetools import func

from iambic import ast


class Parser:
    __resolver_map__ = ast.GenericNode.__resolver_map__

    @func.lru_cache(typed=True)
    def parse(self, data: str) -> ast.ResolvedNode:
        data = json.loads(data) if isinstance(data, str) else data
        handler = self.__resolver_map__[data.pop("type")]
        return handler(**data)

    __call__ = parse


parser = Parser()
