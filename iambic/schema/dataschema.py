#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import inspect
import dataclasses
from typing import Type

import dataslots
import typic
import ujson as json


dataclass_sig = inspect.signature(dataclasses.dataclass)
typicklass_sig = inspect.signature(typic.klass)


def dataschema(_cls=None, **kwargs) -> Type:
    """A class-wrapper in the style of :py:func:`dataclasses.dataclass`.

    Other Parameters
    ----------------
    add_dict : True
        This is passed to :py:func:`dataslots.with_slots` and will be ignored if ``slots=False``
    add_weakref : bool, default False
        This is passed to :py:func:`dataslots.with_slots` and will be ignored if ``slots=False``
    frozen : bool, default False
        This is passed to :py:func:`dataclasses.dataclass`
    init : bool, default True
        This is passed to :py:func:`dataclasses.dataclass`
    repr : bool, default True
        This is passed to :py:func:`dataclasses.dataclass`
    eq : bool, default True
        This is passed to :py:func:`dataclasses.dataclass`
    order : bool, default False
        This is passed to :py:func:`dataclasses.dataclass`
    unsafe_hash : bool, default False
        This is passed to :py:func:`dataclasses.dataclass`
    """

    def wrap_cls(_cls):
        dcls = dataclasses.dataclass(
            _cls, **{x: y for x, y in kwargs.items() if x in dataclass_sig.parameters}
        )
        dcls.astuple = dataclasses.astuple
        dcls.replace = dataclasses.replace
        dcls.json = lambda cls: json.dumps(cls.asdict(), indent=2)
        dcls.json.__name__ = "json"
        dcls.json.__qualname__ = f"{dcls.__name__}.json"
        cls_ = typic.al(
            dataslots.with_slots(
                dcls,
                add_dict=kwargs.pop('add_dict', False),
                add_weakref=kwargs.pop('add_weakref', False)
            ),
            delay=kwargs.pop('delay', False))
        cls_.__signature__ = inspect.signature(dcls)
        cls_.__annotations__ = dcls.__annotations__
        cls_.__qualname__ = dcls.__qualname__

        return cls_

    return wrap_cls if _cls is None else wrap_cls(_cls)
