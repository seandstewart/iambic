#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
from typing import List, Dict, Hashable, Tuple

import tablib

from iambic import ast


Row = List[Hashable]
Table = Dict[str, Row]
Matrix = List[Tuple[Hashable, ...]]


class Column(str, enum.Enum):
    """Predefined column names"""

    CHAR = "Dramatis Personae"
    CLINE = "Lines"
    PLINE = "Player Lines"
    PLAYR = "Player"
    SORT = "Sort"
    GSWAP = " [SW]"


class Marker(str, enum.Enum):
    """The character to use when marking a character as present in a scene."""

    SPEAK = "X"
    PRES = "O"
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

    @staticmethod
    def _tabulate_scene(
        scene: ast.NodeTree,
        node_column: List[str],
        cline_column: List[int],
        char_index: Dict[str, int],
    ):
        for child in scene.children:
            if isinstance(child, ast.Speech):
                index = char_index[child.persona.name]
                node_column[index] = Marker.SPEAK.value
                cline_column[index] += child.num_lines
            elif isinstance(child, ast.Entrance):
                for pers in child.personae:
                    index = char_index[pers.name]
                    node_column[index] = Marker.PRES.value

    def tabulate(self, play: ast.Play) -> Table:
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
        table = dict()
        table[Column.CHAR.value] = list(x.name for x in play.personae)
        char_column = table[Column.CHAR.value]
        table[Column.CLINE.value] = list(0 for _ in char_column)
        cline_column = table[Column.CLINE.value]
        char_index = {y: x for x, y in enumerate(char_column)}

        for act in play.children:
            # Epilogues and Prologues are shaped like Scenes
            # But can be top-level, like Acts.
            children = (
                [act]
                if act.node.type in {ast.NodeType.EPIL, ast.NodeType.PROL}
                else act.children
            )
            for scene in children:
                node = scene.node if isinstance(scene, ast.NodeTree) else scene
                table[node.col] = list(Marker.NONE.value for _ in char_column)
                if isinstance(scene, ast.NodeTree):
                    self._tabulate_scene(
                        scene=scene,
                        node_column=table[node.col],
                        cline_column=cline_column,
                        char_index=char_index,
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
        return [tuple(table.keys())] + list(zip(*table.values()))

    def dataset(self, table: Table) -> tablib.Dataset:
        """Transform a table into an instance of :py:class:`tablib.Dataset`."""
        pivot = self.matrix(table)
        headers = pivot.pop(0)
        return tablib.Dataset(*pivot, headers=headers)

    def __call__(self, play: ast.Play) -> tablib.Dataset:
        table = self.tabulate(play)
        return self.dataset(table)


tabulate = Tabulator()
