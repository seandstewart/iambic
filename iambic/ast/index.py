#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
from collections import defaultdict
from typing import (
    Sequence,
    DefaultDict,
    Dict,
    Type,
    Optional,
    List,
    Set,
    Union,
    ValuesView,
)

import iambic.ast.node as ast

__all__ = ("Index",)


IndexKeyType = Union[
    ast.NodeType, ast.ResolvedNode, Type[ast.ResolvedNode], ast.GenericNode, str
]
SpeechMemberType = Union[ast.Action, ast.Dialogue, ast.Direction]


class Index(Dict[str, ast.ResolvedNode]):
    """An ordered collection of nodes in a script.

    ``Parser.parse`` builds a list of :class:`GenericNode`, which can be resolved into the specific
    data-type for the :class:`NodeType` assigned.
    """

    def __init__(self, initlist: Sequence[ast.GenericNode] = None):
        initlist = initlist or []
        super().__init__(initlist)
        self.generic = {}
        self.__type_map: DefaultDict[
            ast.NodeType, Dict[str, ast.ResolvedNode]
        ] = defaultdict(dict)

    def __getitem__(self, item: IndexKeyType):
        if isinstance(item, ast.NodeType):
            return self.__type_map[item]
        return super().__getitem__(item)

    def __contains__(self, item: IndexKeyType) -> bool:
        if isinstance(item, ast.NodeType):
            return item in self.__type_map
        return super().__contains__(item)

    def get(self, k: IndexKeyType, default=None):
        default = default or {}
        if k in self:
            return self[k]
        return default

    def get_values(self, k: ast.NodeType) -> ValuesView[ast.ResolvedNode]:
        return self.get(k, default={}).values()

    def add(self, node: ast.GenericNode):
        resolved = node.resolved
        self[resolved.id] = resolved
        self.generic[resolved.id] = node
        self.__type_map[resolved.type][resolved.id] = resolved

    @property
    def personae(self) -> ValuesView[ast.Persona]:
        return self.get_values(ast.NodeType.PERS)

    @property
    def acts(self) -> ValuesView[ast.Act]:
        return self.get_values(ast.NodeType.ACT)

    @property
    def scenes(self) -> ValuesView[ast.Scene]:
        return self.get_values(ast.NodeType.SCENE)

    @property
    def prologues(self) -> ValuesView[ast.Prologue]:
        return self.get_values(ast.NodeType.PROL)

    @property
    def epilogues(self) -> ValuesView[ast.Epilogue]:
        return self.get_values(ast.NodeType.EPIL)

    @property
    def dialogue(self) -> ValuesView[ast.Dialogue]:
        return self.get_values(ast.NodeType.DIAL)

    @property
    def directions(self) -> ValuesView[ast.Direction]:
        return self.get_values(ast.NodeType.DIR)

    @property
    def actions(self) -> ValuesView[ast.Action]:
        return self.get_values(ast.NodeType.ACTION)

    @property
    def entrances(self) -> ValuesView[ast.Entrance]:
        return self.get_values(ast.NodeType.ENTER)

    @property
    def exits(self) -> ValuesView[ast.Exit]:
        return self.get_values(ast.NodeType.EXIT)

    @property
    def intermission(self) -> Optional[ast.Intermission]:
        inter = {*self.get_values(ast.NodeType.INTER)}
        return inter.pop() if inter else None

    def resolve_presence(self):
        members: List[Union[ast.Entrance, ast.Exit]] = [*self.entrances] + [*self.exits]
        personae = {x.text: x for x in self.personae}
        for member in members:
            present = tuple(y.id for x, y in personae.items() if x in member.text)
            member.personae = present

    def get_speeches(self) -> List[ast.Speech]:
        # Candidates for members of speeches.
        members: List[SpeechMemberType] = sorted(
            [*self.dialogue] + [*self.directions] + [*self.actions], key=self.node_sort
        )
        persona: Optional[ast.Persona] = None
        scene: Optional[ast.Scene] = self[members[0].scene]
        speech: List[SpeechMemberType] = []
        speeches: List[ast.Speech] = []

        for node in members:
            # If we're in a new scene, we're definitely in a new speech.
            if node.scene != scene.id:
                spch = ast.Speech(persona.id, scene.id, tuple(speech), speech[0].index)
                speeches.append(spch)
                # Directions aren't directly associated to a persona,
                # so do not have the persona attr.
                # BUT they can occur within speeches, so we still have to track them all.
                persona = None if node.type == ast.NodeType.DIR else self[node.persona]
                scene, persona, speech = self[node.scene], persona, [node]
                continue
            # These puppies have a `persona` attr, so are easily associated to a speech.
            if node.type in {ast.NodeType.DIAL, ast.NodeType.ACTION}:
                # If the persona isn't set or has been reset.
                # See above for when persona can be set to null.
                if not persona:
                    persona = self[node.persona]
                    speech.append(node)
                    continue
                # Short-circuit the below if the personae match.
                if node.persona == persona.id:
                    speech.append(node)
                    continue
                # Otherwise, we have a new persona, meaning we have a new speech.
                spch = ast.Speech(persona.id, scene.id, tuple(speech), speech[0].index)
                speeches.append(spch)
                persona, scene, speech = self[node.persona], self[node.scene], [node]
                continue
            # If we've set a persona and we come across a Direction,
            # we can be reasonably sure this dir should be associated to this speech.
            if node.type == ast.NodeType.DIR and persona:
                speech.append(node)
        # Once we've exhausted all members, it's possible we have one speech left.
        if persona and scene and speech:
            spch = ast.Speech(persona.id, scene.id, tuple(speech), speech[0].index)
            speeches.append(spch)

        return speeches

    def filter_directions(self, speeches: Set[ast.Speech]) -> Set[ast.Direction]:
        speech_directions = set(
            y for x in speeches for y in x.speech if isinstance(y, ast.Direction)
        )
        return set(self.get(ast.Direction, {}).values()) - speech_directions

    def get_scene_trees(self, sort: bool = True) -> List[ast.NodeTree]:
        speeches = {*self.get_speeches()}
        directions = self.filter_directions(speeches)
        entrances = {*self.entrances}
        exits = {*self.exits}
        children = speeches | directions | entrances | exits
        scenes = []
        for node in {*self.scenes} | {*self.prologues} | {*self.epilogues}:
            child_nodes = set(x for x in children if x.scene == node.id)
            personae = set(
                x.persona for x in child_nodes if x.type == ast.NodeType.SPCH
            )
            if child_nodes:
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
        scenes = {*scenes}
        acts = {x for x in scenes if x.node.act is None}
        scenes -= acts
        intermission = self.intermission
        prols = set(x for x in self.prologues if x.act is None)
        epils = set(x for x in self.epilogues if x.act is None)
        for act in prols | {*self.acts} | epils:
            children = set(x for x in scenes if x.node.act == act.id)
            if children:
                scenes -= children
                # Add the intermission if there is one.
                if intermission and intermission.act == act.id:
                    children.add(intermission)
                nodes = tuple(sorted(children, key=self.node_sort))
                acts.add(ast.NodeTree(act, nodes))
        acts = list(sorted(acts, key=self.node_sort))
        return acts

    def to_tree(self, meta: ast.Metadata = None) -> ast.Play:
        # Resolve the presence of personae in entrances/exits
        self.resolve_presence()
        # Build the Act-level trees
        scenes = self.get_scene_trees()
        # Build the Play-level trees
        acts = self.get_act_trees(scenes)
        # Put it all together
        play = ast.Play((*acts,), (*self.personae,), meta=(meta or ast.Metadata()))
        return play

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def node_sort(node):
        return getattr(node, "node", node).index
