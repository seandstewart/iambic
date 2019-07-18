#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import functools
import logging
import typing
from collections import defaultdict
from typing import Pattern, Match

import cachetools.func
from html2text import html2text

from iambic.ast import (
    GenericNode,
    NodeType,
    Play,
    InputType,
    ResolvedNode,
    Index,
    NodeToken,
    NodePattern,
)

logger = logging.getLogger(__name__)


@cachetools.func.lru_cache(maxsize=None, typed=True)
def _cached_match(pattern: Pattern, value: str) -> Match:
    return pattern.fullmatch(value) or pattern.match(value)


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
    pattern: Pattern = None
    match: Match = None
    text: str = None
    index: int = 0
    lineno: int = 0
    linepart: int = 0


@dataclasses.dataclass
class ParserContext:
    parent: GenericNode = None
    act: GenericNode = None
    scene: GenericNode = None
    character: GenericNode = None
    index: Index = dataclasses.field(default_factory=Index)
    lineno: int = 0
    linepart: int = 0


class Parser:
    """The text parser for generating a query-able data structure from a body of text.

    Text should be in valid markdown and uses the regex patterns defined in :py:class:`NodePattern`.
    """

    LOCALES = frozenset((NodeType.ACT, NodeType.PROL, NodeType.EPIL, NodeType.SCENE))

    def __init__(self):
        self.__parser_map = defaultdict(lambda: self.default_handler)
        # Map the custom handlers for different Node sub-types
        for typ in self.LOCALES:
            self.__parser_map[typ] = self.locale_handler
        self.__parser_map[NodeType.PERS] = self.persona_handler

    @staticmethod
    @cachetools.func.lru_cache(maxsize=None, typed=True)
    def match(line: str, index: int) -> _PreNode:
        """Take an individual line from a body of text and determine which :py:class:`NodeType` it is."""
        node = _PreNode(
            type=NodeType.ACT,
            pattern=NodePattern.ACT.value,
            match=NodePattern.ACT.value.match(line),
            text=line,
            index=index,
        )
        for node_type in NodeType:
            pattern = NodePattern.get(node_type)
            match = _cached_match(pattern, line)
            if match:
                if node_type in {NodeType.ACTION, NodeType.DIR}:
                    match_dict = match.groupdict()
                    if match_dict.get("start") or match_dict.get("end"):
                        node.pattern, node.match, node.type = pattern, match, node_type
                        break
                else:
                    node.pattern, node.match, node.type = pattern, match, node_type
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

        node = GenericNode(**dataclasses.asdict(node), **kwargs)
        ctx.index.append(node)
        return ctx

    @staticmethod
    def persona_handler(ctx: ParserContext, node: _PreNode) -> ParserContext:
        """The handler for :py:class:`NodeType.PERS`"""
        node = GenericNode(**dataclasses.asdict(node))
        ctx.character = node
        ctx.index.append(node)
        return ctx

    @staticmethod
    def check_parent(
        act: typing.Optional[GenericNode], node: _PreNode
    ) -> typing.Tuple[GenericNode, GenericNode]:
        """Check if the current node qualifies as a 'Parent Node'."""
        kwargs = dataclasses.asdict(node)
        if node.type != NodeType.ACT:
            kwargs["parent"] = _safe_id(act)
        node = GenericNode(**kwargs)
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

    @staticmethod
    def check_direction(ctx: ParserContext, node: _PreNode) -> bool:
        """Check that a given node is not actually within a stage-direction/action/enter/exit context."""
        append = True
        if ctx.index:
            prev: GenericNode = ctx.index.generic[-1]

            if (
                prev.type
                in {NodeType.DIR, NodeType.ACTION, NodeType.EXIT, NodeType.ENTER}
                and node.type in {NodeType.DIAL, prev.type}
                and not prev.match.groupdict().get("end")
            ):
                text = f"{prev.text.strip()} {node.text.strip()}"
                match = prev.pattern.match(text)
                ctx.index[-1] = dataclasses.replace(prev, text=text, match=match)
                append = False
        return append

    def locale_handler(self, ctx: ParserContext, node: _PreNode) -> ParserContext:
        """The handler for locale-types, defined in :py:attr:`Parser.LOCALES`"""
        ctx.parent, node = self.check_parent(ctx.act, node)
        last_type = ctx.index[-1].type if ctx.index else None
        if node.type == NodeType.ACT:
            ctx.act = node
        elif node.type in {NodeType.EPIL, NodeType.PROL} and last_type != NodeType.ACT:
            ctx.scene = node
            ctx.act = node
        else:
            ctx.scene = node
        ctx.index.append(node)
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
            append = self.check_direction(ctx, node)
            if append:
                self.check_linecount(ctx, node)
                handler = self.__parser_map[node.type]
                ctx = handler(ctx=ctx, node=node)

        return ctx.index.to_tree(title=title) if tree else ctx.index

    __call__ = parse


parser = Parser()
