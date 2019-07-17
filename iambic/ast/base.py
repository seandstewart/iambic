#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
import functools
import inspect
import ujson as json
import re
from typing import Pattern, Mapping, Collection

from iambic import schema


__all__ = (
    "NodeType",
    "NodeToken",
    "NodeMixin",
    "NodePattern",
    "DEFINITIONS",
    "jsonify",
)


class NodeType(str, enum.Enum):
    """An enumeration of the different types of nodes in a script."""

    ACT = "act"
    SCENE = "scene"
    PROL = "prologue"
    EPIL = "epilogue"
    INTER = "intermission"
    PERS = "persona"
    ENTER = "entrance"
    EXIT = "exit"
    ACTION = "action"
    DIR = "direction"
    DIAL = "dialogue"
    SPCH = "speech"
    TREE = "tree"
    PLAY = "play"
    META = "meta"


class NodeToken(str, enum.Enum):
    """An enumeration of special 'tokens', e.g., strings of characters."""

    JOIN1 = "…"
    JOIN2 = "..."


class NodePattern(enum.Enum):
    """An Enumeration of the regex patterns matching the types of nodes.

    Note
    ----
    Order is important!
    """

    ACT = re.compile(r"^#+ (?P<act>(ACT)\s([IVX]+|\d+))", re.I)
    SCENE = re.compile(r"^#+ (?P<scene>SCENE\s([IVX]+|\d+)).*", re.I)
    PROL = re.compile(r"^#+ (?P<prologue>PROLOGUE).*", re.I)
    EPIL = re.compile(r"^#+ (?P<epilogue>EPILOGUE).*", re.I)
    INTER = re.compile(r"^#+ (?P<intermission>(INTERMISSION)).*", re.I)
    PERS = re.compile(
        r"[*_]{2}(?P<persona>(([A-Z][a-zA-Z'’]*\W{0,2}([a-z]+)?\s?)+([A-Z]|\d)*))[*_]{2}"
    )
    ENTER = re.compile(
        r"(?P<start>^[_*])?(?P<entrance>(enter)((?![_*]).)*)(?P<end>[_*])?\s{0,2}",
        (re.I | re.M),
    )
    EXIT = re.compile(
        r"(?P<start>^[_*])?(?P<exit>(exeunt|exit)((?![_*]).)*)(?P<end>[_*])?\s{0,2}",
        (re.I | re.M),
    )
    ACTION = re.compile(
        r"(?P<start>^[_*]\[)?(?P<action>((?!\][_*]).)*)(?P<end>\][_*])?\s{0,2}",
        (re.I | re.M),
    )
    DIR = re.compile(
        r"(?P<start>^[_*])?(?P<direction>((?![_*]).)*)(?P<end>[_*])?\s{0,2}",
        (re.I | re.M),
    )
    DIAL = re.compile(r"(?P<dialogue>(^.+))")

    @classmethod
    @functools.lru_cache(maxsize=len(list(NodeType)))
    def get(cls, node: NodeType) -> Pattern:
        """Get the pattern matching this node-type."""
        for pattern in cls:
            if pattern.name == node.name:
                return pattern.value
        raise TypeError(f"Unrecognized value for parameter node: {node}")


def asdict(obj):
    if isinstance(obj, (str, bytes, int)):
        return obj

    result = {}
    for attr in (
        x
        for x in dir(obj)
        if not x.startswith("_")
        and x not in {"id", "klass", "linerange", "col", "cols", "num_lines"}
    ):
        val = getattr(obj, attr)
        if inspect.ismethod(val):
            continue
        if hasattr(val, "asdict"):
            val = val.asdict()
        elif isinstance(val, enum.Enum):
            val = val.value
        elif isinstance(val, Mapping):
            val = {x: asdict(y) for x, y in val.items()}
        elif isinstance(val, Collection) and not isinstance(val, str):
            val = tuple(asdict(x) for x in val)

        result[attr] = val

    return result


class NodeMixin:
    @property
    @functools.lru_cache(1)
    def klass(self):
        return type(self).__name__.lower()

    asdict = asdict


DEFINITIONS = schema.SCHEMA["definitions"]
jsonify = functools.partial(json.dumps, indent=4, separators=(", ", ": "))
