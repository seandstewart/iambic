#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
import textwrap
from typing import List, Dict, Hashable, Tuple, Union, Type, Any, Iterable

import tablib

from iambic import ast


Row = List[Hashable]
Table = Dict[str, Row]
Matrix = List[Tuple[Hashable, ...]]


class Column(str, enum.Enum):
    """Predefined column names"""

    CHAR = "Dramatis Personae"
    APPR = "First Appearance"
    CLINE = "Lines"
    PLINE = "Player Lines"
    PLAYR = "Player"
    SORT = "Sort"
    GSWAP = " [SW]"


class Marker(str, enum.Enum):
    """The character to use when marking a persona as present in a scene."""

    SPEAK = "X"
    PRES = "O"
    NONE = ""


class RichMarker(str, enum.Enum):
    """The rich text character to use when marking a persona as present in a scene."""

    SPEAK = "💬"
    PRES = "👁️‍🗨️"
    NONE = ""


class Tabulator:
    """Generate a tabular representation of :py:class:`~iambic.ast.Play`

    Also known as a 'character map', this utility will generate a table
    which shows the number of lines for a given character and where they
    appear in the play.

    .. i.e.:
        | Dramatis Personae | Lines | I.i | I.ii | Player | Player Lines |
        ------------------------------------------------------------------
        | Johnny Appleseed  | 100   |  x  |   x  |  Jimmy |      75      |

    """

    def _tabulate_scene(
        self,
        scene: Union[ast.Scene, ast.Epilogue, ast.Prologue],
        node_column: List[str],
        cline_column: List[int],
        char_index: Dict[str, int],
        personae: Dict[str, ast.Persona],
        links: bool,
        marker_type: Type[Union[Marker, RichMarker]],
    ):
        for child in scene.body:
            marker = (
                marker_type.SPEAK
                if child.type == ast.NodeType.SPCH
                else marker_type.PRES
            )
            entry = self.link(marker, child) if links else marker.value
            if isinstance(child, ast.Speech):
                persona = personae[child.persona]
                index = char_index[persona.name]
                cline_column[index] += child.num_lines
                if marker_type.SPEAK not in node_column[index]:
                    node_column[index] = entry
            elif isinstance(child, ast.Entrance):
                for pers in child.personae:
                    persona = personae[pers]
                    index = char_index[persona.name]
                    if not node_column[index]:
                        node_column[index] = entry

    @staticmethod
    def link(marker: Union[Marker, RichMarker], node: ast.ResolvedNodeT) -> str:
        return f"[{marker.value}](#{node.id})"

    def tabulate(
        self, play: ast.Play, *, links: bool = False, rich: bool = False
    ) -> Table:
        """Generate a table for this play.

        The table is returned in the form of a Mapping.
        The keys are the header and the columns are the values.

        .. i.e.:
            {
                "foo": ['a', 'value'],
                "bar": ['another, 'value],
                ...
            }
        """
        marker_type: Type[Union[Marker, RichMarker]] = RichMarker if rich else Marker
        table: Dict[str, Any] = {
            Column.CHAR.value: [x.name for x in play.personae],
            Column.APPR.value: [x.index for x in play.personae],
            Column.CLINE.value: [0 for _ in play.personae],
        }
        char_column: List[str] = table[Column.CHAR.value]
        cline_column: List[int] = table[Column.CLINE.value]
        char_index: Dict[str, int] = {y: x for x, y in enumerate(char_column)}
        personae = {x.id: x for x in play.personae}
        for act in play.body:
            # Epilogues and Prologues can be shaped like Scenes or Acts.
            # And can be top-level, like Acts.
            children: ast.ActBodyT = act.body if (  # type: ignore
                isinstance(act, ast.Act) or act.as_act
            ) else (act,)
            for scene in children:

                table[scene.col] = [marker_type.NONE.value for _ in char_column]
                if isinstance(scene, ast.Intermission):
                    continue
                self._tabulate_scene(
                    scene=scene,
                    node_column=table[scene.col],
                    cline_column=cline_column,
                    char_index=char_index,
                    personae=personae,
                    links=links,
                    marker_type=marker_type,
                )

        return table

    @staticmethod
    def matrix(table: Table) -> Matrix:
        """Pivot a table into a 2-D array (matrix).

        The first entry is the header and the proceeding lines are values.

        .. i.e.:
            [
                ("foo", "bar"),
                ("a", "another"),
                ("value", "value"),
                ...
            ]
        """
        return [(*table.keys(),), *zip(*table.values())]

    def dataset(self, table: Table) -> tablib.Dataset:
        """Transform a table into an instance of :py:class:`tablib.Dataset`."""
        pivot = self.matrix(table)
        headers = pivot.pop(0)
        return tablib.Dataset(*pivot, headers=headers)

    def __call__(
        self, play: ast.Play, *, links: bool = False, rich: bool = False
    ) -> tablib.Dataset:
        table = self.tabulate(play, links=links, rich=rich)
        return self.dataset(table)


tabulate = Tabulator()


class TableFormat(str, enum.Enum):
    TABLE = "table"
    TABS = "tabs"


def iter_scene_tab(table: tablib.Dataset, scene_name: str) -> Iterable[str]:
    characters, scene = table[Column.CHAR], table[scene_name]
    yield f'=== "{scene_name}"'
    for character, marker in zip(characters, scene):
        if marker:
            yield f"    - [{character} ⇒ {marker.lstrip('[')}"
    yield ""


def iter_grid_tab(table: tablib.Dataset) -> Iterable[str]:
    yield '=== "Full Breakdown"'
    yield textwrap.indent(export_grid(table), "    ")
    yield ""


def iter_tabs(
    table: tablib.Dataset, *, include_grid: bool = True, __headers=frozenset(Column)
):
    for header in (h for h in table.headers if h not in __headers):
        yield from iter_scene_tab(table, header)
    if include_grid:
        yield from iter_grid_tab(table)


def export_tabs(table: tablib.Dataset) -> str:
    return "\n".join(iter_tabs(table))


def export_grid(table: tablib.Dataset) -> str:
    return table.export("cli", tablefmt="github")


def export(table: tablib.Dataset, format: TableFormat = TableFormat.TABLE):
    if format == TableFormat.TABLE:
        return export_grid(table)
    return export_tabs(table)
