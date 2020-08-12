#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pathlib
from typing import Set, Iterator, Optional, Union, Mapping

import inflection
import typic

from iambic import parse, ast


class Corpus:

    PATH: pathlib.Path = pathlib.Path(__file__).parent
    CACHE_SIZE: int = 1000

    def __init__(self):
        self._corpus: Mapping[str, pathlib.Path] = {x.name: x for x in self}
        self.__hits: int = 0

    def _maybe_reset(self):
        if self.__hits > 1000:
            self.__getitem__.cache_clear()
            self.__hits = 0

    @staticmethod
    def _get_names(path: pathlib.Path) -> Set[str]:
        names = {path.name}
        for child in path.iterdir():
            if child.suffix == ".md":
                names.add(inflection.parameterize(child.stem))
        return names

    def __iter__(self) -> Iterator[pathlib.Path]:
        stack = {self.PATH}
        while stack:
            d = stack.pop()
            for f in d.iterdir():
                if f.is_dir():
                    stack.add(f)
                elif f.is_file() and f.suffix == ".md":
                    yield f

    @typic.fastcachedmethod
    def __getitem__(self, item: str):
        self._maybe_reset()
        if not isinstance(item, str):
            raise ValueError(
                f"Corpus keys must be type str, provided {type(item)}: {item!r}"
            )
        if item in self._corpus:
            self.__hits += 1
            return self._corpus[item].read_text()
        seen = set()
        item = inflection.parameterize(item)
        for k, v in self._corpus.items():
            seen.add(k)
            if item in k:
                self.__hits += 1
                return v.read_text()
        raise KeyError(
            f"Couldn't locate a play with key {item!r}. Available keys are: {(*seen,)}"
        )

    def get(
        self, item: str, default: str = None, *, parsed: bool = False
    ) -> Optional[Union[str, ast.Play, ast.Index]]:
        try:
            text = self[item]
            return parse.text(text) if parsed else text
        except KeyError:
            return default


corpus = Corpus()
get = corpus.get
