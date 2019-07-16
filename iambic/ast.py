#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import enum
import functools
import inspect
import json
import re
from collections import deque
from typing import (
    Pattern,
    ClassVar,
    Optional,
    Tuple,
    Union,
    Sequence,
    Type,
    Any,
    List,
    Set,
    Match,
    Mapping,
    Collection,
    Callable,
    Deque,
)

import inflection
import typic
from cachetools import cached, LFUCache
from cachetools.keys import hashkey

from iambic import schema, roman
from iambic.schema import frozendict

DEFINITIONS = schema.SCHEMA["definitions"]
jsonify = functools.partial(json.dumps, indent=4, separators=(", ", ": "))


class NodeType(str, enum.Enum):
    """An enumeration of the different types of nodes in a script."""

    ACT = "act"
    SCENE = "scene"
    PROL = "prologue"
    EPIL = "epilogue"
    INTER = "intermission"
    PERS = "persona"
    ENTER = "entrance"
    EXIT = "exit"
    ACTION = "action"
    DIR = "direction"
    DIAL = "dialogue"
    SPCH = "speech"
    TREE = "tree"
    PLAY = "play"
    META = "meta"


class NodeToken(str, enum.Enum):
    """An enumeration of special 'tokens', e.g., strings of characters."""

    JOIN1 = "…"
    JOIN2 = "..."


class NodePattern(enum.Enum):
    """An Enumeration of the regex patterns matching the types of nodes.

    Note
    ----
    Order is important!
    """

    ACT = re.compile(r"^#+ (?P<act>(ACT)\s([IVX]+|\d+))", re.I)
    SCENE = re.compile(r"^#+ (?P<scene>SCENE\s([IVX]+|\d+)).*", re.I)
    PROL = re.compile(r"^#+ (?P<prologue>PROLOGUE).*", re.I)
    EPIL = re.compile(r"^#+ (?P<epilogue>EPILOGUE).*", re.I)
    INTER = re.compile(r"^#+ (?P<intermission>(INTERMISSION)).*", re.I)
    PERS = re.compile(
        r"[*_]{2}(?P<persona>(([A-Z][a-zA-Z'’]*\W{0,2}([a-z]+)?\s?)+([A-Z]|\d)*))[*_]{2}"
    )
    ENTER = re.compile(
        r"(?P<start>^[_*])?(?P<entrance>(enter)((?![_*]).)*)(?P<end>[_*])?\s{0,2}",
        (re.I | re.M),
    )
    EXIT = re.compile(
        r"(?P<start>^[_*])?(?P<exit>(exeunt|exit)((?![_*]).)*)(?P<end>[_*])?\s{0,2}",
        (re.I | re.M),
    )
    ACTION = re.compile(
        r"(?P<start>^[_*]\[)?(?P<action>((?!\][_*]).)*)(?P<end>\][_*])?\s{0,2}",
        (re.I | re.M),
    )
    DIR = re.compile(
        r"(?P<start>^[_*])?(?P<direction>((?![_*]).)*)(?P<end>[_*])?\s{0,2}",
        (re.I | re.M),
    )
    DIAL = re.compile(r"(?P<dialogue>(^.+))")

    @classmethod
    @functools.lru_cache(maxsize=len(list(NodeType)))
    def get(cls, node: NodeType) -> Pattern:
        """Get the pattern matching this node-type."""
        for pattern in cls:
            if pattern.name == node.name:
                return pattern.value
        raise TypeError(f"Unrecognized value for parameter node: {node}")


def asdict(obj):
    result = {}
    for attr in (
        x
        for x in dir(obj)
        if not x.startswith("_")
        and x not in {"id", "klass", "linerange", "col", "cols", "num_lines"}
    ):
        val = getattr(obj, attr)
        if inspect.ismethod(val):
            continue
        if hasattr(val, "asdict"):
            val = val.asdict()
        elif isinstance(val, enum.Enum):
            val = val.value
        elif isinstance(val, Mapping):
            val = {x: asdict(y) for x, y in val.items()}
        elif isinstance(val, Collection) and not isinstance(val, str):
            val = tuple(asdict(x) for x in val)

        result[attr] = val

    return result


class NodeMixin:
    @property
    @functools.lru_cache(1)
    def klass(self):
        return type(self).__name__.lower()

    asdict = asdict


@schema.dataschema(frozen=True, delay=True)
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


@schema.dataschema(frozen=True, delay=True)
class Scene(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Scene"]
    )
    type: ClassVar[NodeType] = NodeType.SCENE
    index: int
    text: str
    num: int
    act: Act
    setting: Optional[str]

    @property
    @functools.lru_cache(1)
    def id(self) -> str:
        return inflection.parameterize(f"{self.act.id}-scene-{roman.numeral(self.num)}")

    @property
    @functools.lru_cache(1)
    def col(self) -> str:
        return f"{self.act.col}.{roman.numeral(self.num).lower()}"

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


@schema.dataschema(frozen=True, delay=True)
class Prologue(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Prologue"]
    )
    type: ClassVar[NodeType] = NodeType.PROL
    index: int
    text: str
    setting: Optional[str]
    act: Act = None

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.act.id}-prologue" if self.act else "prologue"

    @property
    @functools.lru_cache(1)
    def col(self):
        return f"{f'{self.act.col}.' if self.act else ''}P"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Prologue":
        setting = " ".join(node.pieces[1:]) if len(node.pieces) > 1 else None
        act = node.parent.resolve() if node.parent else None if node.parent else None
        return cls(index=node.index, text=node.match_text, setting=setting, act=act)


class Epilogue(Prologue):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Epilogue"]
    )
    type: ClassVar[NodeType] = NodeType.EPIL

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.act.id}-epilogue" if self.act else "epilogue"

    @property
    @functools.lru_cache(1)
    def col(self):
        return f"{f'{self.act.col}.' if self.act else ''}E"


@schema.dataschema(frozen=True, delay=True)
class Intermission(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Intermission"]
    )
    type: ClassVar[NodeType] = NodeType.INTER
    index: int
    text: str
    act: Act

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"intermission"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Intermission":
        return cls(
            node.index, node.match_text, node.parent.resolve() if node.parent else None
        )

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


@schema.dataschema(frozen=True, delay=True)
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
        return (
            other.name == self.name if hasattr(other, "name") else False
        )

    @property
    @functools.lru_cache(1)
    def id(self):
        return inflection.parameterize(self.name)

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Persona":
        return cls(index=node.index, text=node.match_text, name=node.match_text.title())


@schema.dataschema(frozen=True, delay=True)
class Entrance(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Entrance"]
    )
    type: ClassVar[NodeType] = NodeType.ENTER
    index: int
    text: str
    scene: Union[Scene, Prologue, Epilogue]
    personae: Tuple[Persona] = dataclasses.field(default_factory=tuple)

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene.id}-entrance-{self.index}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Entrance":
        return cls(
            index=node.index,
            text=node.match_text,
            scene=node.parent.resolve() if node.parent else None,
        )


class Exit(Entrance):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Exit"]
    )
    type: ClassVar[NodeType] = NodeType.EXIT

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene.id}-exit-{self.index}"


@schema.dataschema(frozen=True, delay=True)
class Action(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Action"]
    )
    type: ClassVar[NodeType] = NodeType.ACTION
    action: str
    persona: Persona
    scene: Union[Scene, Prologue, Epilogue]
    index: int

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene.id}-{self.persona.id}-action-{self.index}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Action":
        return cls(
            action=node.match_text,
            persona=node.parent.resolve() if node.parent else None,
            scene=node.scene.resolve(),
            index=node.index,
        )


@schema.dataschema(frozen=True, delay=True)
class Direction(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Direction"]
    )
    type: ClassVar[NodeType] = NodeType.DIR
    action: str
    scene: Union[Scene, Prologue, Epilogue]
    index: int
    stop: bool = True

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.scene.id}-direction-{self.index}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Direction":
        return cls(
            action=node.match_text,
            scene=node.parent.resolve() if node.parent else None,
            index=node.index,
        )


@schema.dataschema(frozen=True, delay=True)
class Dialogue(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Dialogue"]
    )
    type: ClassVar[NodeType] = NodeType.DIAL
    line: str
    persona: Persona
    scene: Union[Scene, Prologue, Epilogue]
    index: int
    lineno: int
    linepart: int = 0

    @property
    @functools.lru_cache(1)
    def id(self):
        return f"{self.persona.id}-dialogue-{self.lineno}"

    @classmethod
    def from_node(cls, node: "GenericNode") -> "Dialogue":
        return cls(
            node.match_text,
            node.parent.resolve() if node.parent else None,
            node.scene.resolve(),
            index=node.index,
            lineno=node.lineno,
        )


@schema.dataschema(frozen=True, delay=True)
class Speech(NodeMixin):
    __static_definition__: ClassVar[schema.frozendict] = schema.frozendict(
        DEFINITIONS["Speech"]
    )
    type: ClassVar[NodeType] = NodeType.SPCH
    persona: Persona
    scene: Union[Scene, Prologue, Epilogue]
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
        return f"{self.scene.id}-{self.persona.id}-speech-{'-'.join(map(str, self.linerange))}"


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
    personae: Tuple[Persona] = dataclasses.field(default_factory=tuple)

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
    NodeTree
]


@schema.dataschema(frozen=True, delay=True)
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


@schema.dataschema(frozen=True, delay=True)
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
    parent: Any = None
    act: Any = None
    scene: Any = None

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

    @classmethod
    def fix_annotations(cls):
        cls.__annotations__.update(
            {"parent": GenericNode, "act": GenericNode, "scene": GenericNode}
        )
        sig = inspect.signature(cls)
        params = dict(sig.parameters)
        params.update(
            {
                "parent": sig.parameters["parent"].replace(annotation=GenericNode),
                "act": sig.parameters["act"].replace(annotation=GenericNode),
                "scene": sig.parameters["scene"].replace(annotation=GenericNode),
            }
        )
        cls.__signature__ = sig.replace(parameters=params.values())


GenericNode.fix_annotations()


class InputType(str, enum.Enum):
    HTML = "html"
    MD = "markdown"
    DATA = "data"


_INDEX_CACHE = dict()


def _memoize_method(call: Callable) -> Callable:

    @functools.wraps(call)
    def __memoize(self, *args, **kwargs):
        global _INDEX_CACHE
        key = hash(tuple(args) + tuple(kwargs.items()))
        if key not in _INDEX_CACHE:
            val = call(self, *args, **kwargs)
            _INDEX_CACHE[key] = val
        return _INDEX_CACHE[key]

    return __memoize


def reset_index_cache():
    global _INDEX_CACHE
    _INDEX_CACHE.clear()


class Index(Deque):
    """An ordered collection of nodes in a script.

    ``Parser.parse`` builds a list of :class:`GenericNode`, which can be resolved into the specific
    data-type for the :class:`NodeType` assigned.
    """

    def __init__(self, initlist: Sequence["GenericNode"] = None):
        initlist = initlist or []
        super().__init__(initlist)
        self.generic = deque()

    def __setitem__(self, key, value: GenericNode):
        if isinstance(value, GenericNode):
            self.generic[key] = value
            value = value.resolve()
        super().__setitem__(key, value)

    def append(self, item: GenericNode) -> None:
        if isinstance(item, GenericNode):
            self.generic.append(item)
            item = item.resolve()
        super().append(item)

    def appendleft(self, item: GenericNode) -> None:
        if isinstance(item, GenericNode):
            self.generic.appendleft(item)
            item = item.resolve()
        super().appendleft(item)

    @_memoize_method
    def get(
        self, node_type: Type, with_loc: bool = True
    ) -> Tuple[Union[Any, Tuple[int, Any]], ...]:
        seen = set()
        iter_ = enumerate(self) if with_loc else self
        return tuple(
            x
            for x in iter_
            if isinstance(x[-1] if isinstance(x, tuple) else x, node_type)
            and not (x in seen or seen.add(x))
        )

    def personae(self) -> Tuple[Persona, ...]:
        return self.get(Persona, with_loc=False)

    def acts(self) -> Tuple[Tuple[int, Act], ...]:
        return self.get(Act)

    def scenes(self) -> Tuple[Tuple[int, Scene], ...]:
        return self.get(Scene)

    def prologues(self) -> Tuple[Tuple[int, Prologue], ...]:
        return self.get(Prologue)

    def epilogues(self) -> Tuple[Tuple[int, Epilogue], ...]:
        return self.get(Epilogue)

    def dialogue(self) -> Tuple[Tuple[int, Dialogue], ...]:
        return self.get(Dialogue)

    def intermission(self) -> Optional[Intermission]:
        inter = self.get(Intermission)
        return inter[-1] if inter else None

    def get_speeches(self) -> List[Speech]:
        persona, scene, speech, speeches = None, None, [], []
        for node in self:
            if type(node) in {Scene, Prologue, Epilogue, Persona}:
                if isinstance(node, Persona):
                    if persona and scene and speech:
                        speeches.append(
                            Speech(persona, scene, tuple(speech), speech[0].index)
                        )
                    persona, speech = node, []
                elif type(node) in {Scene, Prologue, Epilogue}:
                    if persona and scene and speech:
                        speeches.append(
                            Speech(persona, scene, tuple(speech), speech[0].index)
                        )
                    persona, scene, speech = None, node, []
            elif isinstance(node, (Dialogue, Action, Direction)):
                speech.append(node)

        if persona and scene and speech:
            speeches.append(Speech(persona, scene, tuple(speech), speech[0].index))
        return speeches

    def filter_directions(self, speeches: Set[Speech]) -> Set[Direction]:
        speech_directions = set(
            y for x in speeches for y in x.speech if isinstance(y, Direction)
        )
        return set(x for x in self.get(Direction, False) if x not in speech_directions)

    def get_scene_trees(self, sort: bool = True) -> List["NodeTree"]:
        speeches = set(self.get_speeches())
        directions = self.filter_directions(speeches)
        entrances = set(self.get(Entrance, False))
        exits = set(self.get(Entrance, False))
        children = speeches | directions | entrances | exits
        scenes = []
        for node in set(self.get(Scene, False)) | set(self.get(Prologue, False)) | set(self.get(Epilogue, False)):
            child_nodes = set(x for x in children if x.scene == node)
            personae = set(x.persona for x in child_nodes if x.type == NodeType.SPCH)
            tree = NodeTree(
                node=node,
                children=tuple(sorted(child_nodes, key=self.node_sort)),
                personae=tuple(personae),
            )
            scenes.append(tree)
            children -= child_nodes
        if sort:
            scenes.sort(key=self.node_sort)
        return scenes

    def get_act_trees(self, scenes: List["NodeTree"]) -> List["NodeTree"]:
        scenes = set(scenes)
        acts = [x for x in scenes if x.node.act is None]
        scenes -= set(acts)
        intermission = self.intermission()
        intermission = intermission[-1] if intermission else None
        for ix, act in self.acts():
            children = set(x for x in scenes if x.node.act and x.node.act.num == act.num)
            scenes -= children
            # Add the intermission if there is one.
            if intermission and intermission.act == act:
                children.add(intermission)
            nodes = tuple(sorted(children, key=self.node_sort))
            acts.append(NodeTree(act, nodes))
        acts.sort(key=self.node_sort)
        return acts

    def to_tree(self, title: str = None) -> "Play":
        # Build the Act-level trees
        scenes = self.get_scene_trees()
        # Build the Play-level trees
        acts = self.get_act_trees(scenes)
        # Put it all together
        play = Play(tuple(acts), tuple(self.personae()), MetaData(title=title))
        return play

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def node_sort(node):
        return getattr(node, "node", node).index


_RESOLVABLE = set(GenericNode.__resolver_map__.values())


def node_coercer(value: Any) -> Optional[ResolvedNode]:
    if type(value) in _RESOLVABLE or value is None:
        return value
    if isinstance(value, GenericNode):
        return value.resolve()

    if not isinstance(value, Mapping):
        value = typic.coerce(value, dict)

    handler = GenericNode.__resolver_map__[value.pop("type")]
    return handler(**value)


_candidates = _RESOLVABLE.union(ChildNode.__args__)
_candidates.add(NodeTree)


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


typic.register(coercer=node_coercer, check=isnodetype, check_origin=False)
typic.resolve()
