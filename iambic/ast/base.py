#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import enum
import functools
import inspect
import ujson as json
import re
from typing import Mapping, Collection


__all__ = (
    "NodeType",
    "NodeToken",
    "NodeMixin",
    "jsonify",
    "NODE_PATTERN",
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


NODE_PATTERN = re.compile(
    r"""
    (
        # Locales: Act, Scene, Prologue, Epilogue, Intermission
        ^\#+\s(?P<act>(ACT)\s([IVX]+|\d+))              |
        ^\#+\s(?P<scene>SCENE\s([IVX]+|\d+)).*          |
        ^\#+\s(?P<prologue>PROLOGUE).*                  |
        ^\#+\s(?P<epilogue>EPILOGUE).*                  |
        ^\#+\s(?P<intermission>(INTERMISSION)).*        |
        # Persona
        [*_]{2}(?P<persona>(
            ([A-Z][a-zA-Z'’]*\W{0,2}([a-z]+)?\s?
        )+([A-Z]|\d)*))[*_]{2}                          |
        # Enter/Exit/Action/Direction
        (
            (?P<start>^[_*]\[?)?
                (
                    (
                        (?P<entrance>(enter)((?![_*\[\]]).)*)|(?P<exit>(exeunt|exit)((?![_*\[\]]).)*)
                    ) 
                    |
                    (?P<direction>((?![_*\[\]]).)+)
                )
                
            (?P<end>\]?[_*])?\s{0,2}
        )                                               |
        # Dialogue (catch-all)
        (?P<dialogue>(^.+))
    )
    """,
    re.VERBOSE | re.IGNORECASE | re.MULTILINE,
)


jsonify = functools.partial(json.dumps, indent=4)


class NodeMixin:
    @property
    @functools.lru_cache(1)
    def klass(self):
        return type(self).__name__.lower()

    def asdict(self) -> Mapping:
        dikt = dataclasses.asdict(self)
        dikt["type"] = self.type
        return dikt

    def json(self):
        return jsonify(self.asdict())

