#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import functools
from textwrap import indent
from typing import Iterable, Mapping, Union, cast, Dict, Tuple

from inflection import titleize

from iambic import ast
from .table import RichMarker, tabulate, iter_tabs, export_grid, Column

TITLE = "# {0}"
ACT = "## {0}"
SCENE = "### {0}"
DIR = "*{0}*"
ACTION = r"*\[{0}]*"
CHAR = "**{0}**"
ID = "{{: id={0} }}"
LINK = '<a class="headerlink" href="#{0}" title="Permanent link">{1}</a>'
USPACE = "&nbsp;"  # unicode space to preserve indent


def iter_stage_direction(entry: Union[ast.Direction, ast.Entrance]) -> Iterable[str]:
    yield ""
    text = entry.action if isinstance(entry, ast.Direction) else entry.text
    line = DIR.format(text)
    link = LINK.format(entry.id, RichMarker.PRES.value)
    yield f"{line} {link}"
    yield ID.format(entry.id)
    yield ""


@functools.lru_cache(maxsize=100_000)
def _indent_shared_line(line: str, last: str) -> Tuple[str, str]:
    token = None
    stripped = line.strip()
    for join in ast.JOIN_TOKENS:
        if stripped.startswith(join):
            token = join
    if token:
        last = last.rstrip(token)
        indent = USPACE * len(last)
        last = f"{last}{line.rstrip(token)}"
        return f"{indent}{line}", last
    return line, last


_seen_lines_by_no: Dict[int, str] = {}


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
            last = line
        elif isinstance(entry, (ast.Direction, ast.Entrance)):
            # Build a new linked paragraph for stage directions
            if last:
                if not speech_linked:
                    yield ID.format(speech.id)
                    speech_linked = True
                yield ""
            yield from iter_stage_direction(entry)
            last = entry.action if isinstance(entry, ast.Direction) else entry.text
        else:
            # Otherwise continue building the speech.
            line = entry.line
            last = line
            if entry.linepart:
                if entry.lineno in _seen_lines_by_no:
                    line, last = _indent_shared_line(
                        entry.line, _seen_lines_by_no[entry.lineno]
                    )
                _seen_lines_by_no[entry.lineno] = last
            yield f"{line}  "
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


def iter_stats(play: ast.Play) -> Iterable[str]:
    linecount = play.linecount
    scenes = sum(
        len(a.body)
        if isinstance(a, ast.Act)
        or (isinstance(a, (ast.Prologue, ast.Epilogue)) and a.as_act)
        else 1
        for a in play.body
    )
    yield '???+ "High-Level Stats"'
    yield ""
    yield f"    **Total Lines:** {linecount}  "
    yield f"    **Total Characters:** {len(play.personae)}  "
    yield f"    **Total Scenes:** {scenes}  "
    yield ""


def iter_meta(meta: ast.Metadata) -> Iterable[str]:
    yield '???+ "Publication Information"'
    yield ""
    for field in dataclasses.fields(meta):
        value = getattr(meta, field.name)
        if value:
            pre = f"    **{titleize(field.name)}:** "
            if isinstance(value, tuple):
                yield pre + " "
                for item in value:
                    yield f"    - {item}"
            else:
                yield f"{pre}{value}  "
    yield ""


def iter_character_index(play: ast.Play):
    tbl = tabulate(play, links=True, rich=True)
    characters, lines = tbl[Column.CHAR], tbl[Column.CLINE]
    yield '???+ "Dramatis Personae (Order of Appearance)"'
    yield ""
    for character, line_count in zip(characters, lines):
        yield f"    - {character} ({line_count} lines)"
    yield ""
    yield '???+ "Character Navigation"'
    yield ""
    for line in iter_tabs(tbl, include_grid=False):
        yield indent(line, "    ")
    yield ""
    yield '??? "Character Navigation (Grid)"'
    yield ""
    yield indent(export_grid(tbl), "    ")


def iter_overview(play: ast.Play) -> Iterable[str]:

    yield ACT.format("Overview")
    yield ""
    yield from iter_stats(play)
    yield from iter_meta(play.meta)
    yield ACT.format("Index")
    yield ""
    yield from iter_character_index(play)
    yield ""


def iter_play(play: ast.Play, overview: bool = True) -> Iterable[str]:
    try:
        personae = {p.id: p for p in play.personae}
        if play.meta.title:
            yield f"# {play.meta.title}"
            yield ""
        if overview:
            yield from iter_overview(play)
        for act in play.body:
            yield from iter_act(act, personae)
    finally:
        _seen_lines_by_no.clear()


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
    return "\n".join(iter_play(play, overview=table))
