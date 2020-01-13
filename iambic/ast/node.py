#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import functools
from typing import ClassVar, Optional, Union, Tuple, Any, Mapping, Type, List, TypeVar

import inflection
import typic

from iambic import roman
from .base import NodeType, NodeMixin


__all__ = (
    "Act",
    "Scene",
    "Prologue",
    "Epilogue",
    "Intermission",
    "Persona",
    "Entrance",
    "Exit",
    "Action",
    "Direction",
    "Dialogue",
    "Speech",
    "ResolvedNode",
    "ChildNode",
    "NodeTree",
    "Play",
    "Metadata",
    "GenericNode",
    "node_coercer",
    "isnodetype",
)


T = TypeVar("T")


@typic.klass(unsafe_hash=True)
class Act(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.ACT)
    index: int
    text: str
    num: int

    @typic.cached_property
    def id(self):
        return inflection.parameterize(f"act-{self.col}")

    @typic.cached_property
    def col(self):
        return roman.numeral(self.num)

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        return cls(index=node.index, text=node.match_text, num=num)


@typic.klass(unsafe_hash=True)
class Scene(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.SCENE)
    index: int
    text: str
    num: int
    act: str
    setting: Optional[str]

    @typic.cached_property
    def id(self) -> str:
        return inflection.parameterize(f"{self.act}-scene-{roman.numeral(self.num)}")

    @typic.cached_property
    def col(self) -> str:
        if self.act in {NodeType.PROL, NodeType.EPIL}:
            pre = self.act[0].upper()
        else:
            pre = self.act.split("-")[-1].upper()
        return f"{pre}.{roman.numeral(self.num).lower()}"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        setting = " ".join(node.pieces[2:]) if len(node.pieces) > 2 else None
        parent = node.parent or node.act or node.scene
        parent = parent.resolve() if hasattr(parent, "resolve") else parent
        return cls(
            index=node.index, text=node.match_text, num=num, act=parent, setting=setting
        )


@typic.klass(unsafe_hash=True)
class Prologue(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.PROL)
    index: int
    text: str
    setting: Optional[str]
    act: str = None

    @typic.cached_property
    def id(self):
        return f"{self.act}-prologue" if self.act else "prologue"

    @typic.cached_property
    def col(self):
        pre = f"{self.act.split('-')[-1].upper()}." if self.act else ""
        return f"{pre}P"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        setting = " ".join(node.pieces[1:]) if len(node.pieces) > 1 else None
        return cls(
            index=node.index, text=node.match_text, setting=setting, act=node.parent
        )


@typic.klass(unsafe_hash=True)
class Epilogue(Prologue):
    type: NodeType = dataclasses.field(init=False, default=NodeType.EPIL)

    @typic.cached_property
    def id(self):
        return f"{self.act}-epilogue" if self.act else "epilogue"

    @typic.cached_property
    def col(self):
        pre = f"{self.act.split('-')[-1].upper()}." if self.act else ""
        return f"{pre}E"


@typic.klass(unsafe_hash=True)
class Intermission(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.INTER)
    index: int
    text: str
    act: str

    @typic.cached_property
    def id(self):
        return f"intermission"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        return cls(index=node.index, text=node.match_text, act=node.parent)

    @typic.cached_property
    def col(self):
        return "INT"


@typic.klass(unsafe_hash=True)
class Persona(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.PERS)
    index: int
    text: str
    name: str
    short: str = None

    def __eq__(self, other) -> bool:
        return other.name == self.name if hasattr(other, "name") else False

    @typic.cached_property
    def id(self):
        return inflection.parameterize(self.name)

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        return cls(
            index=node.index,
            text=node.match_text,
            name=inflection.titleize(node.match_text),
        )


@typic.klass(unsafe_hash=True)
class Entrance(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.ENTER)
    index: int
    text: str
    scene: str
    personae: Tuple[str, ...] = dataclasses.field(default_factory=tuple)

    @typic.cached_property
    def id(self):
        return f"{self.scene}-entrance-{self.index}"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        return cls(index=node.index, text=node.match_text, scene=node.parent)


@typic.klass(unsafe_hash=True)
class Exit(Entrance):
    type: NodeType = dataclasses.field(init=False, default=NodeType.EXIT)

    @typic.cached_property
    def id(self):
        return f"{self.scene}-exit-{self.index}"


@typic.klass(unsafe_hash=True)
class Action(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.ACTION)
    action: str
    persona: str
    scene: str
    index: int

    @typic.cached_property
    def id(self):
        return f"{self.scene}-{self.persona}-action-{self.index}"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        return cls(
            action=node.match_text,
            persona=node.parent,
            scene=node.scene,
            index=node.index,
        )


@typic.klass(unsafe_hash=True)
class Direction(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.DIR)
    action: str
    scene: str
    index: int
    stop: bool = True

    @typic.cached_property
    def id(self):
        return f"{self.scene}-direction-{self.index}"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        return cls(action=node.match_text, scene=node.parent, index=node.index)


@typic.klass(unsafe_hash=True)
class Dialogue(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.DIAL)
    line: str
    persona: str
    scene: str
    index: int
    lineno: int
    linepart: int = 0

    @typic.cached_property
    def id(self):
        return f"{self.persona}-dialogue-{self.lineno}-{self.linepart}"

    @classmethod
    def from_node(cls: Type[T], node: "GenericNode") -> T:
        return cls(
            node.match_text,
            node.parent,
            node.scene,
            index=node.index,
            lineno=node.lineno,
            linepart=node.linepart,
        )


@typic.klass(unsafe_hash=True, delay=True)
class Speech(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.SPCH)
    persona: str
    scene: str
    speech: Tuple[Union[Dialogue, Action, Direction], ...]
    index: int

    @typic.cached_property
    def linerange(self) -> Tuple[int, int]:
        linenos = sorted([x.lineno for x in self.speech if hasattr(x, "lineno")])
        return linenos[0], linenos[-1]

    @typic.cached_property
    def num_lines(self) -> int:
        x, y = self.linerange
        # line count starts at 1
        # a range of 1 - 1 is 1 line
        return y - (x - 1)

    @typic.cached_property
    def id(self) -> str:
        return (
            f"{self.scene}-{self.persona}-speech-{'-'.join(map(str, self.linerange))}"
        )


ResolvedNode = Union[
    Act,
    Scene,
    Prologue,
    Epilogue,
    Persona,
    Entrance,
    Exit,
    Action,
    Direction,
    Dialogue,
    Speech,
    Intermission,
]

ChildNode = ResolvedNode


@typic.klass(unsafe_hash=True, delay=True)
class NodeTree(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.TREE)
    node: ResolvedNode
    children: Tuple[ChildNode, ...] = dataclasses.field(default_factory=tuple)
    personae: Tuple[str, ...] = dataclasses.field(default_factory=tuple)

    @typic.cached_property
    def cols(self) -> Tuple[Any, ...]:
        return tuple(
            getattr(x, "node", x).col
            for x in self.children
            if isinstance(x, (NodeTree, Prologue))
        )

    @typic.cached_property
    def id(self) -> str:
        return f"{self.node.id}-tree"


ChildNode = Union[
    Act,
    Scene,
    Prologue,
    Epilogue,
    Persona,
    Entrance,
    Exit,
    Action,
    Direction,
    Dialogue,
    Speech,
    Intermission,
    NodeTree,
]


@typic.klass(unsafe_hash=True)
class Metadata(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.META)
    rights: str = "Creative Commons Non-Commercial Share Alike 3.0"
    language: str = "en-GB-emodeng"
    publisher: str = "Published w/ ❤️ using iambic - https://pypi.org/project/iambic"
    title: str = None
    subtitle: str = None
    edition: int = 1
    author: str = "William Shakespeare"
    editors: Tuple[str, ...] = dataclasses.field(default_factory=tuple)
    tags: Tuple[str, ...] = dataclasses.field(default_factory=tuple)

    @functools.lru_cache(1)
    def asmeta(self):  # pragma: nocover
        dikt = {
            "creator": [{"type": "author", "text": self.author}],
            "contributor": [{"type": "editor", "text": "MIT"}],
            "rights": self.rights,
            "language": self.language,
            "publisher": self.publisher,
            "subject": ["Shakespeare"],
        }
        if self.title:
            dikt["title"] = [
                {"type": "main", "text": self.title},
                {"type": "edition", "text": self.edition},
            ]
            if self.subtitle:
                dikt["title"].append({"type": "subtitle", "text": self.subtitle})
        dikt["contributor"].extend(
            ({"type": "editor", "text": x} for x in self.editors or [])
        )
        dikt["subject"].extend(self.tags or [])

        return dikt


@typic.klass(unsafe_hash=True, delay=True)
class Play(NodeMixin):
    type: NodeType = dataclasses.field(init=False, default=NodeType.PLAY)
    children: Tuple[NodeTree, ...] = dataclasses.field(default_factory=tuple)
    personae: Tuple[Persona, ...] = dataclasses.field(default_factory=tuple)
    meta: Metadata = dataclasses.field(default_factory=Metadata)

    @typic.cached_property
    def id(self) -> str:
        return inflection.parameterize(f"{self.meta.title}-play")


@dataclasses.dataclass(unsafe_hash=True)
class GenericNode(NodeMixin):
    """The root-object of a script.

    A script ``Node`` represents a single line of text in a script.
    """

    __resolver_map__: ClassVar[
        Mapping[NodeType, Type[ResolvedNode]]
    ] = typic.FrozenDict(
        {
            NodeType.ACT: Act,
            NodeType.ACTION: Action,
            NodeType.DIAL: Dialogue,
            NodeType.DIR: Direction,
            NodeType.ENTER: Entrance,
            NodeType.EPIL: Epilogue,
            NodeType.EXIT: Exit,
            NodeType.INTER: Intermission,
            NodeType.META: Metadata,
            NodeType.PERS: Persona,
            NodeType.PLAY: Play,
            NodeType.PROL: Prologue,
            NodeType.SCENE: Scene,
            NodeType.SPCH: Speech,
            NodeType.TREE: NodeTree,
        }
    )
    # Minimum data for a Node
    type: NodeType
    text: str
    index: int
    # Additional fields which may be present
    lineno: int = None
    linepart: int = None
    # Given by text parser
    # If reading from JSON, we don't have/need this,
    # it will be provided inherently by the data-structure
    # on resolution-time.
    match: typic.FrozenDict = dataclasses.field(default_factory=typic.FrozenDict)
    parent: str = None
    act: str = None
    scene: str = None

    @typic.cached_property
    def resolved(self) -> ResolvedNode:
        """Resolve a GenericNode into a typed, "resolved" Node.

        Raises
        ------
        TypeError
            If the NodeType provided has no resolved Node mapping.
        """
        try:
            return self.__resolver_map__[self.type].from_node(self)
        except KeyError:  # pragma: nocover
            raise TypeError(
                f"Unrecognized node-type <{self.type}> for text <{self.text}>. "
                f"Valid types are: {tuple(self.__resolver_map__)}"
            )

    @typic.cached_property
    def pieces(self) -> List[str]:
        return self.match_text.split()

    @typic.cached_property
    def match_text(self) -> str:
        return self.match[self.type] if self.match else self.text


_RESOLVABLE = set(GenericNode.__resolver_map__.values())
_candidates = _RESOLVABLE.union(ChildNode.__args__)
_candidates.add(NodeTree)


def node_coercer(value: Any) -> Optional[ResolvedNode]:
    if type(value) in _RESOLVABLE or value is None:
        return value
    if isinstance(value, GenericNode):
        return value.resolved

    if not isinstance(value, Mapping):
        value = typic.coerce(value, dict)

    handler: Type[ResolvedNode] = GenericNode.__resolver_map__[value.pop("type")]
    return handler(**value)


@functools.lru_cache(maxsize=None)
def isnodetype(obj: Type) -> bool:
    is_valid = (
        obj is ResolvedNode
        or obj is GenericNode
        or obj in _candidates
        or (
            getattr(obj, "__origin__", None) is Union
            and set(getattr(obj, "__args__", set())).issubset(_candidates)
        )
    )
    return is_valid
