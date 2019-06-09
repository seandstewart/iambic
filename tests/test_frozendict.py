#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from iambic.schema.frozendict import frozendict


def test_frozendict():
    mydict = {"foo": {"bar": ["baz"], "blah": {"shmeh"}}}
    frozen = frozendict(mydict)
    assert isinstance(frozen["foo"], frozendict)
    assert isinstance(frozen["foo"]["bar"], tuple)
    assert isinstance(frozen["foo"]["blah"], frozenset)
