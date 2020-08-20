#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import functools
from operator import attrgetter
from typing import (
    ClassVar,
    Optional,
    Union,
    Tuple,
    Any,
    Mapping,
    Type,
    List,
    TypeVar,
    NewType,
    Iterable,
)

import typic
from inflection import parameterize, titleize

from iambic import roman
from .base import NodeType


__all__ = (
    "Act",
    "ActBodyT",
    "ActNodeT",
    "Scene",
    "SceneBodyT",
    "SceneNodeT",
    "Prologue",
    "Epilogue",
    "LogueBodyT",
    "Intermission",
    "Persona",
    "Entrance",
    "Exit",
    "Action",
    "Direction",
    "Dialogue",
    "Speech",
    "SpeechNodeT",
    "SpeechBodyT",
    "ResolvedNodeT",
    "Play",
    "PlayNodeT",
    "PlayBodyT",
    "Metadata",
    "GenericNode",
    "NodeID",
    "NodeType",
    "node_deserializer",
    "log_deserializer",
    "isnodetype",
)


T = TypeVar("T")
NodeID = NewType("NodeID", str)
indexgetter = attrgetter("index")


_T = TypeVar("_T")


def sort_body(body: Iterable[_T]) -> Tuple[_T, ...]:
    return tuple(sorted(body, key=indexgetter))


@typic.klass(unsafe_hash=True, order=True, slots=True)
class Act:
    """A representation of a single Act in a Play."""

    type: ClassVar[NodeType] = NodeType.ACT
    index: int
    text: str
    num: int
    body: "ActBodyT" = typic.field(compare=False, hash=False, default=())  # type: ignore

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(parameterize(f"{self.type.lower()}-{self.col}"))

    @typic.cached_property
    def col(self):
        return roman.numeral(self.num)

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Act":
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        return cls(index=node.index, text=node.match_text, num=num)


@typic.klass(unsafe_hash=True, slots=True)
class Scene:
    """A representation of a single Scene in a play."""

    type: ClassVar[NodeType] = NodeType.SCENE
    index: int
    text: str
    num: int
    setting: Optional[str] = None
    act: Optional[NodeID] = None
    body: "SceneBodyT" = typic.field(compare=False, hash=False, default=())  # type: ignore
    personae: "PersonaeIDT" = typic.field(compare=False, hash=False, default=())  # type: ignore

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(parameterize(f"{self.act}-{self.type.lower()}-{self.col}"))

    @typic.cached_property
    def col(self) -> str:
        pre = self.act or ""
        if pre:
            pieces = pre.split("-")
            if len(pieces) == 2:
                pre = pieces[1] if pre.startswith("act") else pieces[0][0]
                pre = f"{pre.upper()}: "
            else:
                pre = f"{pieces[0].title()}: "
        return f"{pre}{roman.numeral(self.num).lower()}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Scene":
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        setting = node.match.get("setting") or None
        parent = node.parent or node.act or node.scene
        if parent is None:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(
            index=node.index,
            text=node.match_text,
            num=num,
            act=parent,
            setting=setting,
        )


@typic.klass(unsafe_hash=True, slots=True)
class Prologue:
    """A representation of a single Prologue in a play.

    Notes:
        Prologues (and Epilogues) may have the body structure of either an Act or Scene.
    """

    type: ClassVar[NodeType] = NodeType.PROL
    index: int
    text: str
    setting: Optional[str] = None
    act: Optional[NodeID] = None
    body: "LogueBodyT" = typic.field(compare=False, hash=False, default=())  # type: ignore
    personae: "PersonaeIDT" = typic.field(compare=False, hash=False, default=())  # type: ignore
    as_act: bool = typic.field(init=False)  # type: ignore

    def __post_init__(self):
        # If the body conforms to the `ActBodyT` type, it should be treated as such.
        self.as_act = bool(
            self.body
            and isinstance(self.body[0], (Scene, Intermission, Epilogue, Prologue))
        )

    @typic.cached_property
    def id(self) -> NodeID:
        pre = f"{self.act}-" if self.act else ""
        return NodeID(f"{pre}{self.type.lower()}-{self.index}")

    @typic.cached_property
    def col(self):
        pre = self.act or ""
        if pre:
            pieces = self.act.split("-")
            if len(pieces) == 2:
                pre = f"{pieces[1].upper()}: "
            else:
                pre = f"{pieces[0].title()}: "
        return f"{pre}{self.type.title()}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Prologue":
        setting = node.match.get("setting") or None
        return cls(
            index=node.index, text=node.match_text, setting=setting, act=node.parent
        )


@typic.klass(unsafe_hash=True, slots=True)
class Epilogue(Prologue):
    """A representation of a single Epilogue in a play.

    Notes:
        Epilogues (and Prologues) may have the body structure of either an Act or Scene.
    """

    type: ClassVar[NodeType] = NodeType.EPIL


@typic.klass(unsafe_hash=True, slots=True)
class Intermission:
    """A representation of an Intermission in a play."""

    type: ClassVar[NodeType] = NodeType.INTER
    index: int
    text: str
    act: NodeID

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID("intermission")

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Intermission":
        if not node.parent:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(index=node.index, text=node.match_text, act=node.parent)

    @typic.cached_property
    def col(self):
        return titleize(self.text)


@typic.klass(unsafe_hash=True, slots=True)
class Persona:
    """A representation of a single character in a Play."""

    type: ClassVar[NodeType] = NodeType.PERS
    index: int
    text: str
    name: str
    short: Optional[str] = None

    def __eq__(self, other) -> bool:
        return other.name == self.name if hasattr(other, "name") else False

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(parameterize(self.name))

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Persona":
        return cls(
            index=node.index, text=node.match_text, name=titleize(node.match_text),
        )


@typic.klass(unsafe_hash=True, slots=True)
class Entrance:
    """A representation of an entrance for character(s) in a Scene."""

    type: ClassVar[NodeType] = NodeType.ENTER
    index: int
    text: str
    scene: NodeID
    personae: "PersonaeIDT" = ()

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(f"{self.scene}-{self.type.lower()}-{self.index}")

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Entrance":
        if not node.parent:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(index=node.index, text=node.match_text, scene=node.parent)


@typic.klass(unsafe_hash=True, slots=True)
class Exit(Entrance):
    """A representation of an exit for character(s) in a Scene."""

    type: ClassVar[NodeType] = NodeType.EXIT


@typic.klass(unsafe_hash=True, slots=True)
class Action:
    """A representation of a stage direction related to a specific character."""

    type: ClassVar[NodeType] = NodeType.ACTION
    action: str
    persona: NodeID
    scene: NodeID
    index: int

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(f"{self.scene}-{self.persona}-{self.type.lower()}-{self.index}")

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Action":
        if not node.parent or not node.scene:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(
            action=node.match_text,
            persona=node.parent,
            scene=node.scene,
            index=node.index,
        )


@typic.klass(unsafe_hash=True, slots=True)
class Direction:
    """A representation of a stage direction."""

    type: ClassVar[NodeType] = NodeType.DIR
    action: str
    scene: NodeID
    index: int
    stop: bool = True

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(f"{self.scene}-{self.type.lower()}-{self.index}")

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Direction":
        if not node.parent:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(action=node.match_text, scene=node.parent, index=node.index)


@typic.klass(unsafe_hash=True, slots=True)
class Dialogue:
    """A representation of a line of dialogue for a character in a scene."""

    type: ClassVar[NodeType] = NodeType.DIAL
    line: str
    persona: NodeID
    scene: NodeID
    index: int
    lineno: int
    linepart: int = 0

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(
            f"{self.persona}-{self.type.lower()}-{self.lineno}-{self.linepart}"
        )

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Dialogue":
        if None in {node.parent, node.scene, node.lineno, node.linepart}:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(
            line=node.match_text,
            persona=node.parent,  # type: ignore
            scene=node.scene,  # type: ignore
            index=node.index,  # type: ignore
            lineno=node.lineno,  # type: ignore
            linepart=node.linepart,  # type: ignore
        )


@typic.klass(unsafe_hash=True, slots=True)
class Speech:
    """A representation of an unbroken piece of dialogue related to a single character."""

    type: ClassVar[NodeType] = NodeType.SPCH
    persona: NodeID
    scene: NodeID
    body: "SpeechBodyT"
    index: int

    def __post_init__(self):
        self.body = sort_body(self.body)

    @typic.cached_property
    def linerange(self) -> Tuple[int, int]:
        linenos = sorted((x.lineno for x in self.body if isinstance(x, Dialogue)))
        return linenos[0], linenos[-1]

    @typic.cached_property
    def num_lines(self) -> int:
        x, y = self.linerange
        # line count starts at 1
        # a range of 1 - 1 is 1 line
        return y - (x - 1)

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(
            f"{self.scene}-{self.persona}-{self.type.lower()}-"
            f"{'{0}-{1}'.format(*self.linerange)}"
            f"-{self.index}"
        )


@typic.klass(unsafe_hash=True, slots=True)
class Metadata:
    """General information about a given play."""

    type: ClassVar[NodeType] = NodeType.META
    rights: str = "Creative Commons Non-Commercial Share Alike 3.0"
    language: str = "en-GB-emodeng"
    publisher: str = "Published w/ ❤️ using iambic - https://pypi.org/project/iambic"
    title: Optional[str] = None
    subtitle: Optional[str] = None
    edition: int = 1
    author: str = "William Shakespeare"
    editors: Tuple[str, ...] = ()
    tags: Tuple[str, ...] = ()

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


@typic.klass(unsafe_hash=True, slots=True)
class Play:
    """A representation of a play in its entirety."""

    type: ClassVar[NodeType] = NodeType.PLAY
    body: "PlayBodyT" = ()
    personae: Tuple[Persona, ...] = ()
    meta: Metadata = typic.field(default_factory=Metadata)  # type: ignore

    def __post_init__(self):
        self.body = sort_body(self.body)

    @typic.cached_property
    def id(self) -> NodeID:
        return NodeID(parameterize(f"{self.meta.title}-{self.type.lower()}"))

    @typic.cached_property
    def linecount(self) -> int:
        count = 0
        final = self.body[-1]
        scene = final.body[-1] if isinstance(final, Act) else final
        if isinstance(scene, Intermission):
            raise ValueError(f"A Play may not end with an Intermission: {scene}")
        for entry in reversed(scene.body):
            if isinstance(entry, Speech):
                count = entry.linerange[-1]
                break
        return count


@typic.klass(unsafe_hash=True, slots=True)
class GenericNode:
    """The root-object of a script.

    A script ``Node`` represents a single line of text in a script.
    """

    __resolver_map__: ClassVar[
        Mapping[NodeType, Type["ResolvedNodeT"]]
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
        }
    )
    # Minimum data for a Node
    type: NodeType
    text: str
    index: int
    # Additional typic.fields which may be present
    lineno: Optional[int] = None
    linepart: Optional[int] = None
    # Given by text parser
    # If reading from JSON, we don't have/need this,
    # it will be provided inherently by the data-structure
    # on resolution-time.
    match: typic.FrozenDict = typic.field(default_factory=typic.FrozenDict)  # type: ignore
    parent: Optional[NodeID] = None
    act: Optional[NodeID] = None
    scene: Optional[NodeID] = None

    @typic.cached_property
    def resolved(self) -> "ResolvedNodeT":
        """Resolve a GenericNode into a typed, "resolved" Node.

        Raises
        ------
        TypeError
            If the NodeType provided has no resolved Node mapping.
        """
        if self.type in self.__resolver_map__:
            model: Type[ResolvedNodeT] = self.__resolver_map__[self.type]
            return model.from_node(self)  # type: ignore
        raise ValueError(
            f"Unrecognized node-type <{self.type}> for text <{self.text}>. "
            f"Valid types are: {tuple(self.__resolver_map__)}"
        )

    @typic.cached_property
    def pieces(self) -> List[str]:
        return self.match_text.split()

    @typic.cached_property
    def match_text(self) -> str:
        return self.match[self.type] if self.match else self.text


ResolvedNodeT = Union[
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
SpeechNodeT = Union[Dialogue, Action, Direction, Entrance, Exit]
SpeechBodyT = Tuple[SpeechNodeT, ...]
ActNodeT = Union[Scene, Intermission, Epilogue, Prologue]
ActBodyT = Tuple[ActNodeT, ...]
SceneNodeT = Union[Direction, Entrance, Exit, Speech]
SceneBodyT = Tuple[SceneNodeT, ...]
LogueBodyT = Union[ActBodyT, SceneBodyT]
PlayNodeT = Union[Act, Epilogue, Prologue]
PlayBodyT = Tuple[PlayNodeT, ...]
PersonaeIDT = Tuple[NodeID, ...]

_RESOLVABLE = set(GenericNode.__resolver_map__.values())


def node_deserializer(value: Any) -> Optional[ResolvedNodeT]:
    if type(value) in _RESOLVABLE or value is None:
        return value
    if isinstance(value, GenericNode):
        return value.resolved

    if not isinstance(value, Mapping):
        value = typic.transmute(dict, value)

    handler: Type[ResolvedNodeT] = GenericNode.__resolver_map__[value.pop("type")]
    resolved: ResolvedNodeT = typic.transmute(handler, value)  # type: ignore
    return resolved


def log_deserializer(value):
    return typic.protocol(Tuple[ResolvedNodeT, ...]).transmute(value)  # type: ignore


@functools.lru_cache(maxsize=None)
def isnodetype(obj: Type, *, __candidates=frozenset(_RESOLVABLE)) -> bool:
    is_valid = obj is GenericNode or (
        getattr(obj, "__origin__", None) is Union
        and {*getattr(obj, "__args__", ())}.issubset(__candidates)
    )
    return is_valid
