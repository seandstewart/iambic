#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from collections.abc import Mapping
from types import MappingProxyType
from typing import Hashable, Iterator, Union, Tuple, List, Any, FrozenSet


class frozendict(Mapping):
    """An immutable, hashable mapping."""

    def __init__(
        self, obj: Union[Mapping, List[Tuple[str, Hashable]]] = None, **kwargs
    ):
        d = {x: self._freeze(y) for x, y in dict(obj or {}, **kwargs).items()}
        self.__r = f"{type(self).__name__}({repr(d)})"
        self.__d = MappingProxyType(d)
        self.__h = hash(frozenset(self.__d))

    @classmethod
    def _freeze(cls, o: Any) -> Hashable:
        if isinstance(o, Hashable):
            return o

        if isinstance(o, Mapping):
            return cls({x: cls._freeze(y) for x, y in o.items()})

        freezer = frozenset if isinstance(o, set) else tuple
        return freezer(cls._freeze(x) for x in o)

    def __repr__(self):
        return self.__r

    def __len__(self) -> int:
        return len(self.__d)

    def __iter__(self) -> Iterator[str]:
        return iter(self.__d)

    def __getitem__(self, k: str) -> Union["frozendict", Hashable, Tuple, FrozenSet]:
        return self.__d.__getitem__(k)

    def __hash__(self):
        return self.__h
