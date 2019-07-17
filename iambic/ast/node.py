#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import functools
import inspect
from typing import (
    ClassVar,
    Optional,
    Union,
    Tuple,
    Any,
    Mapping,
    Type,
    Pattern,
    Match,
    List,
)

import inflection
import typic
from cachetools import cached, LFUCache
from cachetools.keys import hashkey

from iambic import schema, roman
from iambic.schema import frozendict
from .base import NodeType, NodeMixin, DEFINITIONS


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
    "MetaData",
    "GenericNode",
    "node_coercer",
    "isnodetype",
)


@schema.dataschema(frozen=True)
class Act(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Act"]
    )
    type: ClassVar[NodeType] = NodeType.ACT
    index: int
    text: str
    num: int

    @property
    @functools.lru_cache(1)
    def id(self):
        return inflection.parameterize(f"act-{self.col}")

    @property
    @functools.lru_cache(1)
    def col(self):
        return roman.numeral(self.num)

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Act":
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        return cls(index=node.index, text=node.match_text, num=num)


@schema.dataschema(frozen=True)
class Scene(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Scene"]
    )
    type: ClassVar[NodeType] = NodeType.SCENE
    index: int
    text: str
    num: int
    act: str
    setting: Optional[str]

    @property
    @functools.lru_cache(1)
    def id(self) -> str:
        return inflection.parameterize(f"{self.act}-scene-{roman.numeral(self.num)}")

    @property
    @functools.lru_cache(1)
    def col(self) -> str:
        return f"{self.act.split('-')[-1].upper()}.{roman.numeral(self.num).lower()}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Scene":
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        setting = " ".join(node.pieces[2:]) if len(node.pieces) > 2 else None
        parent = node.parent or node.act or node.scene
        parent = parent.resolve() if hasattr(parent, "resolve") else parent
        return cls(
            index=node.index, text=node.match_text, num=num, act=parent, setting=setting
        )


@schema.dataschema(frozen=True)
class Prologue(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Prologue"]
    )
    type: ClassVar[NodeType] = NodeType.PROL
    index: int
    text: str
    setting: Optional[str]
    act: str = None

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.act}-prologue" if self.act else "prologue"

    @property
    @functools.lru_cache(1)
    def col(self):
        pre = f"{self.act.split('-')[-1].upper()}." if self.act else ""
        return f"{pre}P"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Prologue":
        setting = " ".join(node.pieces[1:]) if len(node.pieces) > 1 else None
        return cls(
            index=node.index, text=node.match_text, setting=setting, act=node.parent
        )


class Epilogue(Prologue):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Epilogue"]
    )
    type: ClassVar[NodeType] = NodeType.EPIL

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.act}-epilogue" if self.act else "epilogue"

    @property
    @functools.lru_cache(1)
    def col(self):
        pre = f"{self.act.split('-')[-1].upper()}." if self.act else ""
        return f"{pre}E"


@schema.dataschema(frozen=True)
class Intermission(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Intermission"]
    )
    type: ClassVar[NodeType] = NodeType.INTER
    index: int
    text: str
    act: str

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"intermission"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Intermission":
        return cls(index=node.index, text=node.match_text, act=node.parent)

    @property
    @functools.lru_cache(1)
    def col(self):
        return "INT"


def persona_cache_key(
    persona: "Persona",
    index: int = None,
    name: str = None,
    text: Union["GenericNode", str] = None,
    short: str = None,
):
    text = text.match_text if isinstance(text, GenericNode) else text
    return hashkey(name, text, short)


@schema.dataschema(frozen=True)
class Persona(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Persona"]
    )
    type: ClassVar[NodeType] = NodeType.PERS
    index: int
    text: str
    name: str
    short: str = None

    # Singleton pattern utilizing LRU cache
    @cached(cache=LFUCache(5000), key=persona_cache_key)
    def __new__(
        cls,
        index: int = None,
        name: str = None,
        text: Union["GenericNode", str] = None,
        short: str = None,
    ):
        return super(type(cls), cls).__new__(cls)

    def __eq__(self, other) -> bool:
        return other.name == self.name if hasattr(other, "name") else False

    @property
    @functools.lru_cache(1)
    def id(self):
        return inflection.parameterize(self.name)

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Persona":
        return cls(
            index=node.index,
            text=node.match_text,
            name=inflection.titleize(node.match_text),
        )


@schema.dataschema(frozen=True)
class Entrance(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Entrance"]
    )
    type: ClassVar[NodeType] = NodeType.ENTER
    index: int
    text: str
    scene: str
    personae: Tuple[str] = dataclasses.field(default_factory=tuple)

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene}-entrance-{self.index}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Entrance":
        return cls(index=node.index, text=node.match_text, scene=node.parent)


class Exit(Entrance):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Exit"]
    )
    type: ClassVar[NodeType] = NodeType.EXIT

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene}-exit-{self.index}"


@schema.dataschema(frozen=True)
class Action(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Action"]
    )
    type: ClassVar[NodeType] = NodeType.ACTION
    action: str
    persona: str
    scene: str
    index: int

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene}-{self.persona}-action-{self.index}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Action":
        return cls(
            action=node.match_text,
            persona=node.parent,
            scene=node.scene,
            index=node.index,
        )


@schema.dataschema(frozen=True)
class Direction(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Direction"]
    )
    type: ClassVar[NodeType] = NodeType.DIR
    action: str
    scene: str
    index: int
    stop: bool = True

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene}-direction-{self.index}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Direction":
        return cls(action=node.match_text, scene=node.parent, index=node.index)


@schema.dataschema(frozen=True)
class Dialogue(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Dialogue"]
    )
    type: ClassVar[NodeType] = NodeType.DIAL
    line: str
    persona: str
    scene: str
    index: int
    lineno: int
    linepart: int = 0

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.persona}-dialogue-{self.lineno}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Dialogue":
        return cls(
            node.match_text,
            node.parent,
            node.scene,
            index=node.index,
            lineno=node.lineno,
        )


@schema.dataschema(frozen=True)
class Speech(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Speech"]
    )
    type: ClassVar[NodeType] = NodeType.SPCH
    persona: str
    scene: str
    speech: Tuple[Union[Dialogue, Action, Direction]]
    index: int

    @property
    @functools.lru_cache(1)
    def linerange(self) -> Tuple[int, int]:
        linenos = sorted([x.lineno for x in self.speech if hasattr(x, "lineno")])
        return linenos[0], linenos[-1]

    @property
    @functools.lru_cache(1)
    def num_lines(self) -> int:
        x, y = self.linerange
        # line count starts at 1
        # a range of 1 - 1 is 1 line
        return y - (x - 1)

    @property
    @functools.lru_cache(1)
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


@schema.dataschema(frozen=True, delay=True)
class NodeTree(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["NodeTree"]
    )
    type: ClassVar[NodeType] = NodeType.TREE
    node: ResolvedNode
    children: Tuple[ChildNode] = dataclasses.field(default_factory=tuple)
    personae: Tuple[str] = dataclasses.field(default_factory=tuple)

    @property
    @functools.lru_cache(1)
    def cols(self) -> Tuple[Any]:
        return tuple(
            getattr(x, "node", x).col
            for x in self.children
            if isinstance(x, (NodeTree, Prologue))
        )


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


@schema.dataschema(frozen=True)
class MetaData(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["MetaData"]
    )
    type: ClassVar[NodeType] = NodeType.META
    rights: str = "Creative Commons Non-Commercial Share Alike 3.0"
    language: str = "en-GB-emodeng"
    publisher: str = "Published w/ ❤️ using iambic - https://pypi.org/project/iambic"
    title: str = None
    subtitle: str = None
    edition: int = 1
    author: str = "William Shakespeare"
    editors: Tuple[str] = dataclasses.field(default_factory=tuple)
    tags: Tuple[str] = dataclasses.field(default_factory=tuple)

    @functools.lru_cache(1)
    def asmeta(self):
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


@schema.dataschema(frozen=True, delay=True)
class Play(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Play"]
    )
    type: ClassVar[NodeType] = NodeType.PLAY
    children: Tuple[NodeTree] = dataclasses.field(default_factory=tuple)
    personae: Tuple[Persona] = dataclasses.field(default_factory=tuple)
    meta: MetaData = dataclasses.field(default_factory=MetaData)

    @property
    @functools.lru_cache(1)
    def id(self) -> str:
        return inflection.parameterize(f"{self.meta.title}-play")


@schema.dataschema(frozen=True)
class GenericNode(NodeMixin):
    """The root-object of a script.

    A script ``Node`` represents a single line of text in a script.
    """

    __resolver_map__: ClassVar[Mapping[NodeType, ResolvedNode]] = frozendict(
        {
            NodeType.ACT: Act,
            NodeType.ACTION: Action,
            NodeType.DIAL: Dialogue,
            NodeType.DIR: Direction,
            NodeType.ENTER: Entrance,
            NodeType.EPIL: Epilogue,
            NodeType.EXIT: Exit,
            NodeType.INTER: Intermission,
            NodeType.META: MetaData,
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
    pattern: Pattern = None
    match: Match = None
    parent: str = None
    act: str = None
    scene: str = None

    @classmethod
    @functools.lru_cache(maxsize=1)
    def sig(cls) -> inspect.Signature:
        return inspect.signature(cls)

    @functools.lru_cache(maxsize=None)
    def resolve(self) -> ResolvedNode:
        """Resolve a GenericNode into a typed, "resolved" Node.

        Raises
        ------
        TypeError
            If the NodeType provided has no resolved Node mapping.
        """
        try:
            return self.__resolver_map__[self.type].from_node(self)
        except KeyError:
            raise TypeError(
                f"Unrecognized node-type <{self.type}> for text <{self.text}>. "
                f"Valid types are: {tuple(self.__resolver_map__)}"
            )

    @property
    @functools.lru_cache(maxsize=1)
    def pieces(self) -> List[str]:
        return self.match_text.split()

    @property
    @functools.lru_cache(maxsize=1)
    def match_text(self) -> str:
        return self.match[self.type] if self.match and self.pattern else self.text


_RESOLVABLE = set(GenericNode.__resolver_map__.values())
_candidates = _RESOLVABLE.union(ChildNode.__args__)
_candidates.add(NodeTree)


def node_coercer(value: Any) -> Optional[ResolvedNode]:
    if type(value) in _RESOLVABLE or value is None:
        return value
    if isinstance(value, GenericNode):
        return value.resolve()

    if not isinstance(value, Mapping):
        value = typic.coerce(value, dict)

    handler: ResolvedNode = GenericNode.__resolver_map__[value.pop("type")]
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
