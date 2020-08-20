#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
import re


__all__ = (
    "NodeType",
    "NodeToken",
    "NODE_PATTERN",
    "JOIN_TOKENS",
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
    JOIN = "/"
    META1 = "---"
    META2 = "..."


JOIN_TOKENS = (NodeToken.JOIN, NodeToken.JOIN1, NodeToken.JOIN2)


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
            (?P<start>^[_*]\\?\[?)?
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
