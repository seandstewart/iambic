#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
from collections import deque, defaultdict
from typing import (
    Deque,
    Sequence,
    DefaultDict,
    Dict,
    Type,
    Mapping,
    Tuple,
    Optional,
    List,
    Set,
)


import iambic.ast.node as ast

__all__ = ("Index",)


class Index(Deque[ast.ResolvedNode]):
    """An ordered collection of nodes in a script.

    ``Parser.parse`` builds a list of :class:`GenericNode`, which can be resolved into the specific
    data-type for the :class:`NodeType` assigned.
    """

    def __init__(self, initlist: Sequence[ast.GenericNode] = None):
        initlist = initlist or []
        super().__init__(initlist)
        self.generic = deque()
        self.__type_map: DefaultDict[
            ast.NodeType, Dict[str, ast.ResolvedNode]
        ] = defaultdict(dict)

    def __setitem__(self, key, value: ast.GenericNode):
        if isinstance(value, ast.GenericNode):
            self.generic[key] = value
            value = value.resolve()
        self.__type_map[value.type][value.id] = value
        super().__setitem__(key, value)

    def append(self, item: ast.GenericNode) -> None:
        if isinstance(item, ast.GenericNode):
            self.generic.append(item)
            item = item.resolve()
        self.__type_map[item.type][item.id] = item
        super().append(item)

    def appendleft(self, item: ast.GenericNode) -> None:
        if isinstance(item, ast.GenericNode):
            self.generic.appendleft(item)
            item = item.resolve()
        self.__type_map[item.type] = dict(
            **{item.id: item}, **self.__type_map[item.type]
        )
        super().appendleft(item)

    def get(self, node_type: Type[ast.ResolvedNode]) -> Mapping[str, ast.ResolvedNode]:
        return self.__type_map[node_type.type]

    def personae(self) -> Tuple[ast.Persona, ...]:
        return tuple(self.get(ast.Persona).values())

    def acts(self) -> Tuple[ast.Act, ...]:
        return tuple(self.get(ast.Act).values())

    def scenes(self) -> Tuple[ast.Scene, ...]:
        return tuple(self.get(ast.Scene).values())

    def prologues(self) -> Tuple[ast.Prologue, ...]:
        return tuple(self.get(ast.Prologue).values())

    def epilogues(self) -> Tuple[ast.Epilogue, ...]:
        return tuple(self.get(ast.Epilogue).values())

    def dialogue(self) -> Tuple[ast.Dialogue, ...]:
        return tuple(self.get(ast.Dialogue).values())

    def intermission(self) -> Optional[ast.Intermission]:
        inter = tuple(self.get(ast.Intermission).values())
        return inter[-1] if inter else None

    def get_speeches(self) -> List[ast.Speech]:
        persona, scene, speech, speeches = None, None, [], []
        for node in self:
            if type(node) in {ast.Scene, ast.Prologue, ast.Epilogue, ast.Persona}:
                if isinstance(node, ast.Persona):
                    if persona and scene and speech:
                        speeches.append(
                            ast.Speech(
                                persona.id, scene.id, tuple(speech), speech[0].index
                            )
                        )
                    persona, speech = node, []
                elif type(node) in {ast.Scene, ast.Prologue, ast.Epilogue}:
                    if persona and scene and speech:
                        speeches.append(
                            ast.Speech(
                                persona.id, scene.id, tuple(speech), speech[0].index
                            )
                        )
                    persona, scene, speech = None, node, []
            elif isinstance(node, (ast.Dialogue, ast.Action, ast.Direction)):
                speech.append(node)

        if persona and scene and speech:
            speeches.append(
                ast.Speech(persona.id, scene.id, tuple(speech), speech[0].index)
            )
        return speeches

    def filter_directions(self, speeches: Set[ast.Speech]) -> Set[ast.Direction]:
        speech_directions = set(
            y for x in speeches for y in x.speech if isinstance(y, ast.Direction)
        )
        return set(self.get(ast.Direction).values()) - speech_directions

    def get_scene_trees(self, sort: bool = True) -> List[ast.NodeTree]:
        speeches = set(self.get_speeches())
        directions = self.filter_directions(speeches)
        entrances = set(self.get(ast.Entrance).values())
        exits = set(self.get(ast.Exit).values())
        children = speeches | directions | entrances | exits
        scenes = []
        for node in set(self.scenes()) | set(self.prologues()) | set(self.epilogues()):
            child_nodes = set(x for x in children if x.scene == node.id)
            personae = set(
                x.persona for x in child_nodes if x.type == ast.NodeType.SPCH
            )
            tree = ast.NodeTree(
                node=node,
                children=tuple(sorted(child_nodes, key=self.node_sort)),
                personae=tuple(personae),
            )
            scenes.append(tree)
            children -= child_nodes
        if sort:
            scenes.sort(key=self.node_sort)
        return scenes

    def get_act_trees(self, scenes: List[ast.NodeTree]) -> List[ast.NodeTree]:
        scenes = set(scenes)
        acts = [x for x in scenes if x.node.act is None]
        scenes -= set(acts)
        intermission = self.intermission()
        for act in self.acts():
            children = set(x for x in scenes if x.node.act == act.id)
            scenes -= children
            # Add the intermission if there is one.
            if intermission and intermission.act == act.id:
                children.add(intermission)
            nodes = tuple(sorted(children, key=self.node_sort))
            acts.append(ast.NodeTree(act, nodes))
        acts.sort(key=self.node_sort)
        return acts

    def to_tree(self, title: str = None) -> ast.Play:
        # Build the Act-level trees
        scenes = self.get_scene_trees()
        # Build the Play-level trees
        acts = self.get_act_trees(scenes)
        # Put it all together
        play = ast.Play(tuple(acts), tuple(self.personae()), ast.MetaData(title=title))
        return play

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def node_sort(node):
        return getattr(node, "node", node).index
