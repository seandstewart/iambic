#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
import pathlib
from typing import Set, Iterator, Optional, Union

import inflection

from iambic import parse, ast


class Corpus:

    PATH: pathlib.Path = pathlib.Path(__file__).parent

    @staticmethod
    def _get_names(path: pathlib.Path) -> Set[str]:
        names = {path.name}
        for child in path.iterdir():
            if child.suffix == ".md":
                names.add(inflection.parameterize(child.stem))
        return names

    def __iter__(self) -> Iterator[pathlib.Path]:
        yield from self.PATH.iterdir()

    @functools.lru_cache(maxsize=128)
    def __getitem__(self, item: str):
        if not isinstance(item, str):
            raise TypeError("Corpus keys must be type str, provided")
        seen = set()
        item = inflection.parameterize(item)
        for child in self:
            if child.is_dir():
                seen.add(child.name)
                names = self._get_names(child)
                if item in names or any(item in x for x in names):
                    for text in child.iterdir():
                        if text.suffix.endswith(".md"):
                            return text.read_text()
        raise KeyError(
            f"Couldn't locate a play with key <{item}>. Available keys are: {tuple(seen)}"
        )

    @functools.lru_cache(maxsize=128)
    def get(
        self, item: str, default: str = None, *, parsed: bool = False, tree: bool = True
    ) -> Optional[Union[str, ast.Play, ast.Index]]:
        try:
            text = self[item]
            return parse.text(text, tree=tree) if parsed else text
        except KeyError:
            return default


corpus = Corpus()
get = corpus.get
