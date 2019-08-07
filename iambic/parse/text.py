#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import functools
import logging
import typing
from collections import defaultdict

from html2text import html2text

from iambic.ast import (
    GenericNode,
    NodeType,
    Play,
    InputType,
    ResolvedNode,
    Index,
    NodeToken,
    NODE_PATTERN,
)
from iambic.schema import frozendict

logger = logging.getLogger(__name__)


def _safe_resolve(
    node: typing.Optional[GenericNode], *, attr: str = None
) -> ResolvedNode:
    if node:
        resolved = node.resolve()
        return getattr(resolved, attr, None) if attr else resolved


_safe_id = functools.partial(_safe_resolve, attr="id")


@dataclasses.dataclass
class _PreNode:
    type: NodeType
    match: typing.Dict[str, str] = dataclasses.field(default_factory=dict)
    text: str = None
    index: int = 0
    lineno: int = 0
    linepart: int = 0

    def to_generic(self, **kwargs) -> GenericNode:
        return GenericNode(
            type=self.type,
            text=self.text,
            index=self.index,
            lineno=self.lineno,
            linepart=self.linepart,
            match=frozendict(self.match),
            **kwargs,
        )


@dataclasses.dataclass
class ParserContext:
    parent: GenericNode = None
    act: GenericNode = None
    scene: GenericNode = None
    character: GenericNode = None
    last: GenericNode = None
    index: Index = dataclasses.field(default_factory=Index)
    lineno: int = 0
    linepart: int = 0

    def add(self, node: GenericNode):
        self.index.add(node)
        self.last = node


class Parser:
    """The text parser for generating a query-able data structure from a body of text.

    Text should be in valid markdown and uses the regex patterns defined in :py:class:`NodePattern`.
    """

    LOCALES = frozenset((NodeType.ACT, NodeType.PROL, NodeType.EPIL, NodeType.SCENE))
    _ACTION_BOOKENDS = frozenset(("[", "]"))

    def __init__(self):
        self.__parser_map = defaultdict(lambda: self.default_handler)
        # Map the custom handlers for different Node sub-types
        for typ in self.LOCALES:
            self.__parser_map[typ] = self.locale_handler
        self.__parser_map[NodeType.PERS] = self.persona_handler

    @classmethod
    @functools.lru_cache(maxsize=None, typed=True)
    def match(cls, line: str, index: int) -> _PreNode:
        """Take an individual line from a body of text and determine which :py:class:`NodeType` it is."""
        match = NODE_PATTERN.match(line)
        match_dict = (
            {x: y for x, y in match.groupdict().items() if y is not None}
            if match
            else {}
        )
        node = _PreNode(
            type=NodeType.DIAL, match={NodeType.DIAL: line}, text=line, index=index
        )
        for node_type in {*NodeType} & match_dict.keys():
            node_type = NodeType(node_type)
            if node_type == NodeType.DIR:
                bookend = match_dict.get("start") or match_dict.get("end")
                if bookend:
                    if cls._ACTION_BOOKENDS & {*bookend}:
                        node_type = NodeType.ACTION
                        match_dict[NodeType.ACTION] = match_dict.pop(NodeType.DIR)
                    node.match, node.type = match_dict, node_type
                    break
            else:
                node.match, node.type = match_dict, node_type
                break

        return node

    @staticmethod
    def default_handler(ctx: ParserContext, node: _PreNode) -> ParserContext:
        """The default node handler. Assumes a lower-level node.

        Takes a pre-node object and resolves it into a :py:class:`GenericNode`.
        Does some juggling of values in ``ctx`` to determine the correct values
        to provide to :py:class:`GenericNode` on init.
        """
        # determine the 'real parent' for this node
        # Set the current parent as the parent for this particular node.
        kwargs = {"parent": _safe_id(ctx.parent)}
        # We associate dialogue and character actions to the character & scene.
        if node.type in {NodeType.DIAL, NodeType.ACTION}:
            kwargs["parent"] = _safe_id(ctx.character)
            kwargs["scene"] = _safe_id(ctx.scene)
        # Intermissions can be associated to the act they occur within
        elif node.type == NodeType.INTER:
            kwargs["parent"] = _safe_id(ctx.act)

        node = node.to_generic(**kwargs)
        ctx.add(node)
        return ctx

    @staticmethod
    def persona_handler(ctx: ParserContext, node: _PreNode) -> ParserContext:
        """The handler for :py:class:`NodeType.PERS`"""
        node = node.to_generic()
        resolved = node.resolve()
        if resolved.id in ctx.index:
            node: GenericNode = dataclasses.replace(node, index=ctx.index[resolved.id].index)
        ctx.character = node
        ctx.add(node)
        return ctx

    @staticmethod
    def check_parent(
        act: typing.Optional[GenericNode], node: _PreNode
    ) -> typing.Tuple[GenericNode, GenericNode]:
        """Check if the current node qualifies as a 'Parent Node'."""
        kwargs = {}
        if node.type != NodeType.ACT:
            kwargs["parent"] = _safe_id(act)
        node = node.to_generic(**kwargs)
        parent = node
        return parent, node

    @staticmethod
    def check_linecount(ctx: ParserContext, node: _PreNode):
        """Check the current line-count and line-part of a given node & context."""
        if node.type == NodeType.DIAL:
            text = node.text.strip()
            continued = text.endswith(NodeToken.JOIN1) or text.endswith(NodeToken.JOIN2)
            continuing = text.startswith(NodeToken.JOIN1) or text.startswith(
                NodeToken.JOIN2
            )
            # started a line-continuation or isn't a line-continuation
            if (continued and not continuing) or (not continued and not continuing):
                node.lineno = ctx.lineno = ctx.lineno + 1
            # in a line-continuation
            if continued or continuing:
                node.linepart = ctx.linepart = ctx.linepart + 1
                node.lineno = ctx.lineno
            # finished a line-continuation
            if not continued:
                ctx.linepart = 0

    @classmethod
    def check_direction(cls, ctx: ParserContext, node: _PreNode) -> bool:
        """Check that a given node is not actually within a stage-direction/action/enter/exit context."""
        add = True
        if ctx.index:
            if (
                ctx.last.type
                in {NodeType.DIR, NodeType.ACTION, NodeType.EXIT, NodeType.ENTER}
                and node.type in {NodeType.DIAL, ctx.last.type}
                and not ctx.last.match.get("end")
            ):
                text = f"{ctx.last.text.strip()} {node.text.strip()}"
                node = cls.match(text, ctx.last.index)
                new: GenericNode = dataclasses.replace(
                    ctx.last, match=frozendict(node.match), text=text
                )
                ctx.add(new)
                add = False
        return add

    def locale_handler(self, ctx: ParserContext, node: _PreNode) -> ParserContext:
        """The handler for locale-types, defined in :py:attr:`Parser.LOCALES`"""
        ctx.parent, node = self.check_parent(ctx.act, node)
        if node.type == NodeType.ACT:
            ctx.act = node
        elif node.type in {NodeType.EPIL, NodeType.PROL} and ((ctx.last.type if ctx.last else None) != NodeType.ACT):
            ctx.scene = node
            ctx.act = node
        else:
            ctx.scene = node
        ctx.add(node)
        return ctx

    @staticmethod
    def guess_formatting(text: str) -> InputType:
        return (
            InputType.HTML
            if text.startswith("<") and text.endswith(">")
            else InputType.MD
        )

    @functools.lru_cache(typed=True)
    def parse(
        self,
        text: str,
        title: str = None,
        *,
        input_type: InputType = None,
        tree: bool = True,
    ) -> Play:
        ctx = ParserContext()
        input_type = input_type or self.guess_formatting(text)
        text = html2text(text) if input_type is InputType.HTML else text
        for ix, line in enumerate(x for x in text.split("\n") if x.strip()):
            node = self.match(line, ix)
            add = self.check_direction(ctx, node)
            if add:
                self.check_linecount(ctx, node)
                handler = self.__parser_map[node.type]
                ctx = handler(ctx=ctx, node=node)
        return ctx.index.to_tree(title=title) if tree else ctx.index

    __call__ = parse


parser = Parser()
