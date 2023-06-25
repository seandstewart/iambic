from __future__ import annotations

import dataclasses
from operator import attrgetter
from typing import ClassVar, Iterable, Mapping, NewType, Self, Type, TypeVar

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
)


T = TypeVar("T")
NodeID = NewType("NodeID", str)
indexgetter = attrgetter("index")


_T = TypeVar("_T")


def sort_body(body: Iterable[_T]) -> tuple[_T, ...]:
    return tuple(sorted(body, key=indexgetter))


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Act:
    """A representation of a single Act in a Play."""

    type: ClassVar[NodeType] = NodeType.ACT
    index: int
    text: str
    num: int
    body: ActBodyT = dataclasses.field(compare=False, hash=False, default=())
    id: NodeID = dataclasses.field(init=False)
    col: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.col = self._getcol()
        self.id = self._getid()

    def _getid(self) -> NodeID:
        return NodeID(parameterize(f"{self.type.lower()}-{self.col}"))

    def _getcol(self):
        return roman.numeral(self.num)

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        numeral = node.pieces[1]
        num = int(numeral) if numeral.isdigit() else roman.integer(numeral)
        return cls(index=node.index, text=node.match_text, num=num)


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Scene:
    """A representation of a single Scene in a play."""

    type: ClassVar[NodeType] = NodeType.SCENE
    index: int
    text: str
    num: int
    setting: str | None = None
    act: NodeID | None = None
    body: SceneBodyT = dataclasses.field(compare=False, hash=False, default=())
    personae: PersonaeIDT = dataclasses.field(compare=False, hash=False, default=())
    id: NodeID = dataclasses.field(init=False)
    col: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.col = self._getcol()
        self.id = self._getid()

    def _getid(self) -> NodeID:
        return NodeID(
            f"{self.act}-{self.type.lower()}-{roman.numeral(self.num).lower()}"
        )

    def _getcol(self) -> str:
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
    def from_node(cls, node: GenericNode) -> Self:
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


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Prologue:
    """A representation of a single Prologue in a play.

    Notes:
        Prologues (and Epilogues) may have the body structure of either an Act or Scene.
    """

    type: ClassVar[NodeType] = NodeType.PROL
    index: int
    text: str
    setting: str | None = None
    act: NodeID | None = None
    body: LogueBodyT = dataclasses.field(compare=False, hash=False, default=())
    personae: PersonaeIDT = dataclasses.field(compare=False, hash=False, default=())
    as_act: bool = dataclasses.field(init=False)
    id: NodeID = dataclasses.field(init=False)
    col: str = dataclasses.field(init=False)

    def __post_init__(self):
        # If the body conforms to the `ActBodyT` type, it should be treated as such.
        self.as_act = bool(
            self.body
            and isinstance(self.body[0], (Scene, Intermission, Epilogue, Prologue))
        )
        self.col = self._getcol()
        self.id = self._getid()

    def _getid(self) -> NodeID:
        pre = f"{self.act}-" if self.act else ""
        return NodeID(f"{pre}{self.type.lower()}-{self.index}")

    def _getcol(self):
        pre = self.act or ""
        if pre:
            pieces = self.act.split("-")
            if len(pieces) == 2:
                pre = f"{pieces[1].upper()}: "
            else:
                pre = f"{pieces[0].title()}: "
        return f"{pre}{self.type.title()}"

    @classmethod
    def from_node(cls, node: GenericNode) -> Prologue:
        setting = node.match.get("setting") or None
        return cls(
            index=node.index, text=node.match_text, setting=setting, act=node.parent
        )


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Epilogue(Prologue):
    """A representation of a single Epilogue in a play.

    Notes:
        Epilogues (and Prologues) may have the body structure of either an Act or Scene.
    """

    type: ClassVar[NodeType] = NodeType.EPIL


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Intermission:
    """A representation of an Intermission in a play."""

    type: ClassVar[NodeType] = NodeType.INTER
    index: int
    text: str
    act: NodeID
    id: NodeID = dataclasses.field(init=False)
    col: str = dataclasses.field(init=False)

    def __post_init__(self):
        self.col = titleize(self.text)
        self.id = NodeID("intermission")

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        if not node.parent:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(index=node.index, text=node.match_text, act=node.parent)


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Persona:
    """A representation of a single character in a Play."""

    type: ClassVar[NodeType] = NodeType.PERS
    index: int
    text: str
    name: str
    short: str | None = None
    id: NodeID = dataclasses.field(init=False)
    ids: set[NodeID] = dataclasses.field(init=False)

    def __post_init__(self):
        self.id = NodeID(parameterize(self.name))
        self.ids = {NodeID(parameterize(n.strip())) for n in self.name.split("&")}

    def __eq__(self, other) -> bool:
        return other.name == self.name if hasattr(other, "name") else False

    @property
    def is_multi(self) -> bool:
        return "&" in self.name

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        return cls(
            index=node.index,
            text=node.match_text,
            name=titleize(node.match_text),
        )


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Entrance:
    """A representation of an entrance for character(s) in a Scene."""

    type: ClassVar[NodeType] = NodeType.ENTER
    index: int
    text: str
    scene: NodeID
    personae: PersonaeIDT = ()
    id: NodeID = dataclasses.field(init=False)

    def __post_init__(self):
        self.id = NodeID(f"{self.scene}-{self.type.lower()}-{self.index}")

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        if not node.parent:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(index=node.index, text=node.match_text, scene=node.parent)


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Exit(Entrance):
    """A representation of an exit for character(s) in a Scene."""

    type: ClassVar[NodeType] = NodeType.EXIT


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Action:
    """A representation of a stage direction related to a specific character."""

    type: ClassVar[NodeType] = NodeType.ACTION
    action: str
    persona: NodeID
    scene: NodeID
    index: int
    id: NodeID = dataclasses.field(init=False)

    def __post_init__(self):
        self.id = NodeID(
            f"{self.scene}-{self.persona}-{self.type.lower()}-{self.index}"
        )

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        if not node.parent or not node.scene:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(
            action=node.match_text,
            persona=node.parent,
            scene=node.scene,
            index=node.index,
        )


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Direction:
    """A representation of a stage direction."""

    type: ClassVar[NodeType] = NodeType.DIR
    action: str
    scene: NodeID
    index: int
    stop: bool = True
    id: NodeID = dataclasses.field(init=False)

    def __post_init__(self):
        self.id = NodeID(f"{self.scene}-{self.type.lower()}-{self.index}")

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        if not node.parent:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(action=node.match_text, scene=node.parent, index=node.index)


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Dialogue:
    """A representation of a line of dialogue for a character in a scene."""

    type: ClassVar[NodeType] = NodeType.DIAL
    line: str
    persona: NodeID
    scene: NodeID
    index: int
    lineno: int
    linepart: int = 0
    id: NodeID = dataclasses.field(init=False)

    def __post_init__(self):
        self.id = NodeID(
            f"{self.persona}-{self.type.lower()}-{self.lineno}-{self.linepart}"
        )

    @classmethod
    def from_node(cls, node: GenericNode) -> Self:
        if None in {node.parent, node.scene, node.lineno, node.linepart}:
            raise ValueError(f"Can't build {cls.__name__!r} from node: {node}")
        return cls(
            line=node.match_text,
            persona=node.parent,
            scene=node.scene,
            index=node.index,
            lineno=node.lineno,
            linepart=node.linepart,
        )


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Speech:
    """A representation of an unbroken piece of dialogue related to a single character."""

    type: ClassVar[NodeType] = NodeType.SPCH
    persona: NodeID
    scene: NodeID
    body: SpeechBodyT
    index: int
    linerange: tuple[int, int] = dataclasses.field(init=False)
    linepart: int = dataclasses.field(init=False)
    num_lines: int = dataclasses.field(init=False)
    id: NodeID = dataclasses.field(init=False)

    def __post_init__(self):
        self.body = sort_body(self.body)
        self.linerange = self._getlinerange()
        self.linepart = self._getlinepart()
        self.num_lines = self._getnum_lines()
        self.id = self._getid()

    def _getlinerange(self) -> tuple[int, int]:
        linenos = sorted((x.lineno for x in self.body if isinstance(x, Dialogue)))
        return linenos[0], linenos[-1]

    def _getlinepart(self) -> int:
        return next((x.linepart for x in self.body if isinstance(x, Dialogue)), 0)

    def _getnum_lines(self) -> int:
        x, y = self.linerange
        return y - (x - 1)

    def _getid(self) -> NodeID:
        uri = (
            f"{self.scene}-{self.persona}-{self.type.lower()}-"
            f"{'-'.join(map(str, self.linerange))}"
        )
        if self.linepart:
            uri += f"-{roman.numeral(self.linepart).lower()}"
        return NodeID(uri)


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Metadata:
    """General information about a given play."""

    type: ClassVar[NodeType] = NodeType.META
    rights: str = "Creative Commons Non-Commercial Share Alike 3.0"
    language: str = "en-GB-emodeng"
    publisher: str = "Published w/ ❤️ using iambic - https://pypi.org/project/iambic"
    title: str | None = None
    subtitle: str | None = None
    edition: int = 1
    author: str = "William Shakespeare"
    editors: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

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


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class Play:
    """A representation of a play in its entirety."""

    type: ClassVar[NodeType] = NodeType.PLAY
    body: PlayBodyT = ()
    personae: tuple[Persona, ...] = ()
    meta: Metadata = dataclasses.field(default_factory=Metadata)
    id: NodeID = dataclasses.field(init=False)
    linecount: int | None = dataclasses.field(init=False)

    def __post_init__(self):
        self.body = sort_body(self.body)
        self.id = self._getid()
        self.linecount = self._getlinecount()

    def _getid(self) -> NodeID:
        return NodeID(parameterize(f"{self.meta.title}-{self.type.lower()}"))

    def _getlinecount(self) -> int:
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

    def asjsonld(self):
        fn, ln = self.meta.author.split()
        data = {
            "@context": "https://schema.org",
            "@type": "Play",
            "name": self.meta.title,
            "author": {
                "@type": "Person",
                "givenName": fn,
                "familyName": ln,
                "birthDate": "1564-04-23",
                "birthPlace": {
                    "@type": "Place",
                    "address": "Stratford-upon-Avon, Warwickshire, England",
                },
                "deathDate": "1616-04-23",
                "deathPlace": {
                    "@type": "Place",
                    "address": "Stratford-upon-Avon, Warwickshire, England",
                },
            },
            "maintainer": {
                "@type": "Organization",
                "name": "Bardly.org",
                "url": "https://bardly.org",
            },
            "size": {
                "@type": "QuantitativeValue",
                "unitCode": "N2",
                "value": self.linecount,
            },
            "license": self.meta.rights,
            "inLanguage": self.meta.language,
            "keywords": [*self.meta.tags],
            "character": [{"@type": "Person", "name": c.name} for c in self.personae],
        }

        return data


@dataclasses.dataclass(slots=True, weakref_slot=True, unsafe_hash=True, order=True)
class GenericNode:
    """The root-object of a script.

    A script ``Node`` represents a single line of text in a script.
    """

    __resolver_map__: ClassVar[Mapping[NodeType, Type[_FromNodeT]]] = typic.FrozenDict(
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
    # Additional fields which may be present
    lineno: int | None = None
    linepart: int | None = None
    # Given by text parser
    # If reading from JSON, we don't have/need this,
    # it will be provided inherently by the data-structure
    # on resolution-time.
    match: typic.FrozenDict = dataclasses.field(default_factory=typic.FrozenDict)
    parent: NodeID | None = None
    act: NodeID | None = None
    scene: NodeID | None = None
    pieces: list[str] = dataclasses.field(init=False)
    match_text: str = dataclasses.field(init=False)
    _resolved: _FromNodeT | None = dataclasses.field(
        init=False, default=None, compare=False
    )

    def __post_init__(self):
        self.match_text = self.match[self.type] if self.match else self.text
        self.pieces = self.match_text.split()

    @property
    def resolved(self: Self) -> ResolvedNodeT:
        """Resolve a GenericNode into a typed, "resolved" Node.

        Raises
        ------
        TypeError
            If the NodeType provided has no resolved Node mapping.
        """
        if self._resolved is not None:
            return self._resolved

        if self.type in self.__resolver_map__:
            model: type[_FromNodeT] = self.__resolver_map__[self.type]
            self._resolved = model.from_node(self)
            return self._resolved

        raise ValueError(
            f"Unrecognized node-type <{self.type}> for text <{self.text}>. "
            f"Valid types are: {tuple(self.__resolver_map__)}"
        )


_FromNodeT = (
    Act
    | Scene
    | Prologue
    | Epilogue
    | Persona
    | Entrance
    | Exit
    | Action
    | Direction
    | Dialogue
    | Intermission
)
ResolvedNodeT = _FromNodeT | Speech
SpeechNodeT = Dialogue | Action | Direction | Entrance | Exit
SpeechBodyT = tuple[SpeechNodeT, ...]
ActNodeT = Scene | Intermission | Epilogue | Prologue
ActBodyT = tuple[ActNodeT, ...]
SceneNodeT = Direction | Entrance | Exit | Speech
SceneBodyT = tuple[SceneNodeT, ...]
LogueBodyT = ActBodyT | SceneBodyT
PlayNodeT = Act | Epilogue | Prologue
PlayBodyT = tuple[PlayNodeT, ...]
PersonaeIDT = tuple[NodeID, ...]
