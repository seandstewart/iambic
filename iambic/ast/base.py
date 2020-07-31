#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
import functools

import typic
import ujson as json
import re


__all__ = ("NodeType", "NodeToken", "NodeMixin", "jsonify", "NODE_PATTERN")


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
    META1 = "---"
    META2 = "..."


NODE_PATTERN = re.compile(
    r"""
    (
        # Locales: Act, Scene, Prologue, Epilogue, Intermission
        (
            ^\#+\s
            (
                (?P<act>(ACT)\s([IVX]+|\d+))                |
                (?P<scene>SCENE\s([IVX]+|\d+))              |
                (?P<prologue>PROLOGUE)                      |
                (?P<epilogue>EPILOGUE)                      |
                (?P<intermission>INTERMISSION)              |
                (?P<title>(.*))
            )
            (?:\.)?\s?(?P<setting>.*)
            $
        )                                               |
        # Persona
        [*_]{2}(?P<persona>(
            ([A-Z][a-zA-Z'’]*\W{0,2}([a-z]+)?\s?
        )+([A-Z]|\d)*))[*_]{2}                          |
        # Enter/Exit/Action/Direction
        (
            (?P<start>^[_*]\[?)?
                (
                    (
                        (?P<entrance>(enter)((?![_*\[\]]).)*)
                        |
                        (?P<exit>(exeunt|exit)((?![_*\[\]]).)*)
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


jsonify = functools.partial(json.dumps, indent=2)


class NodeMixin:
    @typic.cached_property
    def klass(self):
        return type(self).__name__.lower()
