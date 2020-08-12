#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
from collections import defaultdict
from itertools import chain
from typing import (
    DefaultDict,
    Dict,
    Optional,
    List,
    Set,
    Union,
    ValuesView,
    cast,
    Mapping,
    Iterable,
    Tuple,
)

import iambic.ast.node as ast

__all__ = ("Index",)


IndexKeyT = Union[ast.NodeType, str]
IndexInputT = Union[
    Mapping[str, ast.GenericNode], Iterable[Tuple[str, ast.GenericNode]]
]


class Index(Dict[str, Union[ast.ResolvedNodeT, ast.GenericNode]]):
    """An ordered collection of nodes in a script.

    ``Parser.parse`` builds a list of :class:`GenericNode`, which can be resolved into the specific
    data-type for the :class:`NodeType` assigned.
    """

    def __init__(self, iterable: IndexInputT = None, **kwargs: ast.GenericNode):
        iterable = iterable or {}
        super().__init__(iterable, **kwargs)
        self.generic: Dict[str, ast.GenericNode] = {}
        self.__type_map: DefaultDict[
            ast.NodeType, Dict[str, ast.ResolvedNodeT]
        ] = defaultdict(dict)

    def __getitem__(self, item: IndexKeyT):
        if isinstance(item, ast.NodeType):
            return self.__type_map[item]
        return super().__getitem__(item)

    def __contains__(self, item: IndexKeyT) -> bool:  # type: ignore
        if isinstance(item, ast.NodeType):
            return item in self.__type_map
        return super().__contains__(item)

    def get(self, k: IndexKeyT, default=None):
        default = default or {}
        if k in self:
            return self[k]
        return default

    def get_values(self, k: ast.NodeType) -> ValuesView[ast.ResolvedNodeT]:
        return self.get(k, default={}).values()

    def add(self, node: ast.GenericNode):
        resolved = node.resolved
        self[resolved.id] = resolved
        self.generic[resolved.id] = node
        self.__type_map[resolved.type][resolved.id] = resolved

    @property
    def personae(self) -> ValuesView[ast.Persona]:
        return cast(ValuesView[ast.Persona], self.get_values(ast.NodeType.PERS))

    @property
    def acts(self) -> ValuesView[ast.Act]:
        return cast(ValuesView[ast.Act], self.get_values(ast.NodeType.ACT))

    @property
    def scenes(self) -> ValuesView[ast.Scene]:
        return cast(ValuesView[ast.Scene], self.get_values(ast.NodeType.SCENE))

    @property
    def prologues(self) -> ValuesView[ast.Prologue]:
        return cast(ValuesView[ast.Prologue], self.get_values(ast.NodeType.PROL))

    @property
    def epilogues(self) -> ValuesView[ast.Epilogue]:
        return cast(ValuesView[ast.Epilogue], self.get_values(ast.NodeType.EPIL))

    @property
    def dialogue(self) -> ValuesView[ast.Dialogue]:
        return cast(ValuesView[ast.Dialogue], self.get_values(ast.NodeType.DIAL))

    @property
    def directions(self) -> ValuesView[ast.Direction]:
        return cast(ValuesView[ast.Direction], self.get_values(ast.NodeType.DIR))

    @property
    def actions(self) -> ValuesView[ast.Action]:
        return cast(ValuesView[ast.Action], self.get_values(ast.NodeType.ACTION))

    @property
    def entrances(self) -> ValuesView[ast.Entrance]:
        return cast(ValuesView[ast.Entrance], self.get_values(ast.NodeType.ENTER))

    @property
    def exits(self) -> ValuesView[ast.Exit]:
        return cast(ValuesView[ast.Exit], self.get_values(ast.NodeType.EXIT))

    @property
    def intermission(self) -> Optional[ast.Intermission]:
        inter = {*self.get_values(ast.NodeType.INTER)}
        return cast(Optional[ast.Intermission], inter.pop() if inter else None)

    def resolve_presence(self):
        members: Iterable[Union[ast.Entrance, ast.Exit]] = chain(
            self.entrances, self.exits
        )
        personae = {x.text: x for x in self.personae}
        for member in members:
            present = (*(p.id for t, p in personae.items() if t in member.text),)
            member.personae = present

    _NP = {ast.NodeType.DIR, ast.NodeType.ENTER, ast.NodeType.EXIT}

    def _resolve_events(
        self,
        speech: List[ast.SpeechNodeT],
        associates: Set[Union[ast.Direction, ast.Entrance, ast.Exit]],
    ):
        start, end = speech[0].index, speech[-1].index
        events = {e for e in associates if start < e.index < end}
        associates -= events
        speech.extend(events)

    def get_speeches(self) -> List[ast.Speech]:
        # Candidates for members of speeches.
        members: List[Union[ast.Dialogue, ast.Action]] = sorted(
            chain(self.dialogue, self.actions), key=ast.indexgetter,
        )
        associates: Set[Union[ast.Direction, ast.Entrance, ast.Exit]] = {
            *self.directions,
            *self.entrances,
            *self.exits,
        }
        persona: Optional[ast.Persona] = None
        scene: ast.Scene = self[members[0].scene]
        speech: List[ast.SpeechNodeT] = []
        speeches: List[ast.Speech] = []

        for i, node in enumerate(members):
            # If we're in a new scene, we're definitely in a new speech.
            if node.scene != scene.id:
                if persona and scene and speech:
                    self._resolve_events(speech, associates)
                    spch = ast.Speech(
                        persona.id, scene.id, ast.sort_body(speech), speech[0].index
                    )
                    speeches.append(spch)
                # Directions aren't directly associated to a persona,
                # so do not have the persona attr.
                # BUT they can occur within speeches, so we still have to track them all.
                persona = (
                    None if node.type in self._NP else self[node.persona]  # type: ignore
                )
                scene, persona, speech = self[node.scene], persona, [node]
                continue
            # These puppies have a `persona` attr, so are easily associated to a speech.
            if isinstance(node, (ast.Action, ast.Dialogue)):
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
                self._resolve_events(speech, associates)
                spch = ast.Speech(
                    persona.id, scene.id, ast.sort_body(speech), speech[0].index
                )
                speeches.append(spch)
                persona, scene, speech = self[node.persona], self[node.scene], [node]
                continue
        # Once we've exhausted all members, it's possible we have one speech left.
        if persona and scene and speech:
            self._resolve_events(speech, associates)
            spch = ast.Speech(
                persona.id, scene.id, ast.sort_body(speech), speech[0].index
            )
            speeches.append(spch)

        return speeches

    def claimed_events(
        self, speeches: Set[ast.Speech]
    ) -> Set[Union[ast.Direction, ast.Exit, ast.Entrance]]:
        return {
            y
            for x in speeches
            for y in x.body
            if isinstance(y, (ast.Direction, ast.Entrance, ast.Exit))
        }

    def finalize_scenes(self) -> Iterable[ast.ActNodeT]:
        speeches = {*self.get_speeches()}
        claimed = self.claimed_events(speeches)
        directions = {*self.directions} - claimed
        entrances = {*self.entrances} - claimed
        exits = {*self.exits} - claimed
        children = speeches | directions | entrances | exits
        scenes = []
        scene: Union[ast.Scene, ast.Epilogue, ast.Prologue]
        for scene in chain(self.scenes, self.epilogues, self.prologues):  # type: ignore
            child_nodes = {c for c in children if c.scene == scene.id}
            s: ast.Speech
            personae: Set[ast.NodeID] = {
                s.persona  # type: ignore
                for s in child_nodes
                if s.type == ast.NodeType.SPCH
            }
            if child_nodes:
                scene.body = ast.sort_body(child_nodes)
                scene.personae = (*personae,)
                scenes.append(scene)
                children -= child_nodes

        return scenes

    def finalize_acts(
        self, scenes: Iterable[ast.ActNodeT]
    ) -> List[Union[ast.Act, ast.Epilogue, ast.Prologue]]:
        scenes = {*scenes}
        logues: Set[Union[ast.Prologue, ast.Epilogue]] = {
            s
            for s in scenes
            if isinstance(s, (ast.Epilogue, ast.Prologue)) and not s.act
        }
        scenes -= logues
        intermission = self.intermission
        # Add the act-level logues which have a Scene-like structure
        acts: List[ast.PlayNodeT] = [*logues]
        act: ast.PlayNodeT
        # Get the act-level logues which have an Act-like structure
        _logues = (
            log
            for log in chain(self.prologues, self.epilogues)
            if not log.body and not log.act
        )
        for act in chain(_logues, self.acts):  # type: ignore
            children: Set[
                Union[ast.Scene, ast.Intermission, ast.Prologue, ast.Epilogue]
            ] = {s for s in scenes if s.act == act.id}
            if children:
                scenes -= children
                # Add the intermission if there is one.
                if intermission and intermission.act == act.id:
                    children.add(intermission)
                act.body = ast.sort_body(children)
                if isinstance(act, (ast.Epilogue, ast.Prologue)):
                    act.as_act = True
                acts.append(act)
        return acts

    def resolve(self, meta: ast.Metadata = None) -> ast.Play:
        # Resolve the presence of personae in entrances/exits
        self.resolve_presence()
        # Build the Act-level trees
        scenes = self.finalize_scenes()
        # Build the Play-level trees
        acts = self.finalize_acts(scenes)
        # Put it all together
        play = ast.Play(
            ast.sort_body(acts), (*self.personae,), meta=(meta or ast.Metadata())
        )
        return play

    @staticmethod
    @functools.lru_cache(maxsize=2000)
    def node_sort(node: Union[ast.ResolvedNodeT, ast.GenericNode]):
        return node.index
