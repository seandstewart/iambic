#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Tuple

import pytest
import typic

from iambic import ast, parse
from iambic.parse.text import ParserContext, _PreNode

generic_act = ast.GenericNode("act", "Act I", 0, 0)
generic_scene = ast.GenericNode(
    "scene", "Scene II", 0, 0, parent=generic_act.resolved.id
)
generic_persona = ast.GenericNode("persona", "Bar", 0, 0)


@pytest.mark.parametrize(
    argnames=("value", "expected"),
    argvalues=[
        ("## ACT I", ast.NodeType.ACT),
        ("### act I", ast.NodeType.ACT),
        ("### scene i", ast.NodeType.SCENE),
        ("## scene i", ast.NodeType.SCENE),
        ("# scene i", ast.NodeType.SCENE),
        ("# scene i. a foo in the forest.", ast.NodeType.SCENE),
        ("# epilogue", ast.NodeType.EPIL),
        ("## PROLOGUE", ast.NodeType.PROL),
        ("# Intermission", ast.NodeType.INTER),
        ("**FOO**", ast.NodeType.PERS),
        ("**Foo's Bar**", ast.NodeType.PERS),
        ("**Foobar 1**", ast.NodeType.PERS),
        ("**Another Foobar 1**", ast.NodeType.PERS),
        ("**Foo Bar Baz Buzz**", ast.NodeType.PERS),
        ("**Foo-Bar Hyph. the Third**", ast.NodeType.PERS),
        ("_Foo does a thing._", ast.NodeType.DIR),
        ("_Foo does", ast.NodeType.DIR),
        ("a thing._", ast.NodeType.DIR),
        ("_[Aside]_", ast.NodeType.ACTION),
        ("_[Stabs foo.]_", ast.NodeType.ACTION),
        ("_Enter Foo, bar._", ast.NodeType.ENTER),
        ("_Exit Foo, bar._", ast.NodeType.EXIT),
        ("_Exeunt severally._", ast.NodeType.EXIT),
        ("Literally anything else.", ast.NodeType.DIAL),
    ],
)
def test_text_match(value: str, expected: ast.NodeType):
    assert parse.text.match(value, 1).type == expected


@pytest.mark.parametrize(
    argnames=("ctx", "node", "expected_parent_text", "expected_node"),
    argvalues=[
        (
            ParserContext(),
            _PreNode(type=ast.NodeType.ACT, text="Act I"),
            "Act I",
            ast.GenericNode(
                type=ast.NodeType.ACT, text="Act I", index=0, lineno=0, linepart=0
            ),
        ),
        (
            ParserContext(act=generic_act),
            _PreNode(type=ast.NodeType.SCENE, text="Scene I"),
            "Scene I",
            ast.GenericNode(
                type=ast.NodeType.SCENE,
                text="Scene I",
                index=0,
                lineno=0,
                linepart=0,
                parent=generic_act.resolved.id,
            ),
        ),
        (
            ParserContext(),
            _PreNode(type=ast.NodeType.EPIL, text="Epilogue"),
            "Epilogue",
            ast.GenericNode(
                type=ast.NodeType.EPIL, text="Epilogue", index=0, lineno=0, linepart=0
            ),
        ),
        (
            ParserContext(),
            _PreNode(type=ast.NodeType.PROL, text="Prologue"),
            "Prologue",
            ast.GenericNode(
                type=ast.NodeType.PROL, text="Prologue", index=0, lineno=0, linepart=0
            ),
        ),
    ],
)
def test_locale_handler(
    ctx: ParserContext,
    node: _PreNode,
    expected_parent_text: str,
    expected_node: ast.GenericNode,
):
    ctx = parse.text.locale_handler(ctx, node)
    assert ctx.parent.text == expected_parent_text
    ctx_node = getattr(ctx, node.type, ctx.act)
    assert ctx_node == expected_node


@pytest.mark.parametrize(
    argnames=("ctx", "node"),
    argvalues=[(ParserContext(), _PreNode(type=ast.NodeType.PERS, text="Foo"))],
)
def test_persona_handler(ctx: ParserContext, node: _PreNode):
    ctx = parse.text.persona_handler(ctx, node)
    assert ctx.character == node.to_generic()


@pytest.mark.parametrize(
    argnames=("ctx", "node", "expected"),
    argvalues=[
        (
            ParserContext(generic_persona, generic_act, generic_scene, generic_persona),
            _PreNode(ast.NodeType.DIAL, text=""),
            ast.GenericNode(
                ast.NodeType.DIAL,
                text="",
                index=0,
                lineno=0,
                linepart=0,
                scene=generic_scene.resolved.id,
                parent="bar",
            ),
        ),
        (
            ParserContext(generic_act, generic_act, generic_scene),
            _PreNode(ast.NodeType.INTER),
            ast.GenericNode(
                ast.NodeType.INTER,
                text="",
                index=0,
                lineno=0,
                linepart=0,
                parent=generic_act.resolved.id,
            ),
        ),
    ],
)
def test_default_handler(ctx: ParserContext, node: _PreNode, expected):
    assert parse.text.default_handler(ctx, node).index.generic.popitem()[-1] == expected


@pytest.mark.parametrize(
    argnames=("ctx", "node", "expected"),
    argvalues=[
        # a normal line.
        (ParserContext(), _PreNode(ast.NodeType.DIAL, text="Foo."), (1, 0, 1, 0)),
        # start of a line, up lineno & linepart.
        (ParserContext(), _PreNode(ast.NodeType.DIAL, text="Foo. ..."), (1, 1, 1, 1)),
        # within a line-continuation, up only linepart.
        (
            ParserContext(),
            _PreNode(ast.NodeType.DIAL, text="... Foo. ..."),
            (0, 1, 0, 1),
        ),
        # end of a line-continuation, up only linepart and reset linepart in context.
        (ParserContext(), _PreNode(ast.NodeType.DIAL, text="... Foo."), (0, 0, 0, 1)),
    ],
)
def test_check_linecount(
    ctx: ParserContext, node: _PreNode, expected: Tuple[int, int, int, int]
):
    parse.text.check_linecount(ctx, node)
    assert (ctx.lineno, ctx.linepart, node.lineno, node.linepart) == expected


def test_check_direction():
    ctx = ParserContext(index=ast.Index())
    gen = ast.GenericNode(
        type="direction",
        text="_Foo",
        index=0,
        match=typic.FrozenDict({"start": "_", "direction": "Foo"}),
        parent="Bar",
    )
    ctx.add(gen)
    node = _PreNode(type=ast.NodeType.DIAL, text="foo")
    append = parse.text.check_direction(ctx, node)
    assert not append
    assert ctx.index.generic.popitem()[-1].text == "_Foo foo"
