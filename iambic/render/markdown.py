#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from textwrap import indent
from typing import Iterable, Mapping, Union, cast

from iambic import ast
from .table import RichMarker, tabulate

TITLE = "# {0}"
ACT = "## {0}"
SCENE = "### {0}"
DIR = "*{0}*"
ACTION = r"*\[{0}]*"
CHAR = "**{0}**"
ID = "{{: id={0} }}"
LINK = '<a class="headerlink" href="#{0}" title="Permanent link">{1}</a>'


def iter_stage_direction(entry: Union[ast.Direction, ast.Entrance]) -> Iterable[str]:
    yield ""
    text = entry.action if isinstance(entry, ast.Direction) else entry.text
    line = DIR.format(text)
    link = LINK.format(entry.id, RichMarker.PRES.value)
    yield f"{line} {link}"
    yield ID.format(entry.id)
    yield ""


def iter_speech(speech: ast.Speech, persona: ast.Persona) -> Iterable[str]:
    character = CHAR.format(persona.name)
    charlink = LINK.format(speech.id, speech.linerange)
    yield f"{character} {charlink}  "
    last = None
    speech_linked = False
    for entry in speech.body:
        if isinstance(entry, ast.Action):
            line = ACTION.format(entry.action)
            # If this isn't the first line of the speech
            # and we haven't added an attribute to the first paragraph of the speech,
            # do so now.
            if last:
                if not speech_linked:
                    yield ID.format(speech.id)
                    speech_linked = True
                yield ""
            # yield the line with a link
            yield f"{line}  "
        elif isinstance(entry, (ast.Direction, ast.Entrance)):
            # Build a new linked paragraph for stage directions
            if last:
                if not speech_linked:
                    yield ID.format(speech.id)
                    speech_linked = True
                yield ""
            yield from iter_stage_direction(entry)
        else:
            # Otherwise continue building the speech.
            yield f"{entry.line}  "
        last = entry
    if not speech_linked:
        yield ID.format(speech.id)
    yield ""


def iter_scene(
    scene: ast.ActNodeT, personae: Mapping[ast.NodeID, ast.Persona], h1: bool = False
) -> Iterable[str]:
    if isinstance(scene, (ast.Prologue, ast.Epilogue)) and scene.as_act:
        yield from iter_act(scene, personae)
    heading = ACT.format(scene.text) if h1 else SCENE.format(scene.text)
    id = ID.format(scene.id)
    if isinstance(scene, ast.Intermission):
        yield f"{heading} {id}"
    else:
        setting = scene.setting or " "
        if setting.strip():
            setting = f". {setting} "
        yield f"{heading}{setting}{id}"
        yield ""
        body = cast(ast.SceneBodyT, scene.body)
        for entry in body:
            if isinstance(entry, (ast.Direction, ast.Entrance)):
                yield from iter_stage_direction(entry)
            else:
                persona = personae[entry.persona]
                yield from iter_speech(entry, persona)
    yield ""


def iter_act(
    act: ast.PlayNodeT, personae: Mapping[ast.NodeID, ast.Persona], h2: bool = False
) -> Iterable[str]:
    if isinstance(act, (ast.Prologue, ast.Epilogue)) and not act.as_act:
        yield from iter_scene(act, personae, h1=True)
    else:
        heading = SCENE.format(act.text) if h2 else ACT.format(act.text)
        id = ID.format(act.id)
        yield f"{heading} {id}"
        yield ""
        body = cast(ast.ActBodyT, act.body)
        for entry in body:
            yield from iter_scene(entry, personae)

    yield ""


def iter_table(play: ast.Play) -> Iterable[str]:
    tbl = tabulate(play, links=True, rich=True)
    yield ACT.format("Character Breakdown")
    yield ""
    yield '???+ "Dramatis Personae"'
    yield ""
    yield indent(tbl.export("cli", tablefmt="github"), "    ")
    yield ""


def iter_play(play: ast.Play, table: bool = True) -> Iterable[str]:
    personae = {p.id: p for p in play.personae}
    if play.meta.title:
        yield f"# {play.meta.title}"
        yield ""
    if table:
        yield from iter_table(play)
    for act in play.body:
        yield from iter_act(act, personae)


def render_markdown(play: ast.Play, *, table: bool = True) -> str:
    """The renderer for a Markdown document.

    Parameters
    ----------
    play :
        The play tree, as loaded via :func:`~iambic.parse.text` or
        :func:`~iambic.parse.data`
    table : default True
        Optionally render a character mapping for your play.
    """
    return "\n".join(iter_play(play, table=table))
