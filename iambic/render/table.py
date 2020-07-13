#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
from typing import List, Dict, Hashable, Tuple, Union, Type

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
        scene: ast.NodeTree,
        node_column: List[str],
        cline_column: List[int],
        char_index: Dict[str, int],
        personae: Dict[str, ast.Persona],
        links: bool,
        marker_type: Type[Union[Marker, RichMarker]],
    ):
        for child in scene.children:
            marker = (
                marker_type.SPEAK
                if child.type == ast.NodeType.SPCH
                else marker_type.PRES
            )
            entry = self.link(marker, child) if links else marker.value
            if child.type == ast.NodeType.SPCH:
                persona = personae[child.persona]
                index = char_index[persona.name]
                node_column[index] = entry
                cline_column[index] += child.num_lines
            elif child.type == ast.NodeType.ENTER:
                for pers in child.personae:
                    persona = personae[pers]
                    index = char_index[persona.name]
                    if not node_column[index]:
                        node_column[index] = entry

    @staticmethod
    def link(marker: Marker, node: ast.ChildNode) -> str:
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
        marker_type = RichMarker if rich else Marker
        table = {
            Column.CHAR.value: [x.name for x in play.personae],
            Column.APPR.value: [x.index for x in play.personae],
            Column.CLINE.value: [0 for _ in play.personae],
        }
        char_column = table[Column.CHAR.value]
        cline_column = table[Column.CLINE.value]
        char_index = {y: x for x, y in enumerate(char_column)}
        personae = {x.id: x for x in play.personae}
        for act in play.children:
            # Epilogues and Prologues can be shaped like Scenes or Acts.
            # And can be top-level, like Acts.
            children = act.children
            if act.node.type in {
                ast.NodeType.EPIL,
                ast.NodeType.PROL,
            } and not isinstance(children[0], ast.NodeTree):
                children = [act]
            for scene in children:
                node = scene.node if isinstance(scene, ast.NodeTree) else scene
                table[node.col] = [marker_type.NONE.value for _ in char_column]
                if isinstance(scene, ast.NodeTree):
                    self._tabulate_scene(
                        scene=scene,
                        node_column=table[node.col],
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
