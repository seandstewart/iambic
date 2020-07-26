#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum
from typing import Union, Mapping

import inflection

from iambic import ast

import yattag


class HTMLTag(str, enum.Enum):
    A = "a"
    BODY = "body"
    BR = "br"
    DIV = "div"
    DTYPE = "<!DOCTYPE html>"
    EM = "em"
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    H4 = "h4"
    H5 = "h5"
    HDR = "header"
    HEAD = "head"
    HREF = "href"
    HTML = "html"
    LI = "li"
    META = "meta"
    MTR = "meter"
    NAV = "nav"
    OL = "ol"
    P = "p"
    SECT = "section"
    SPAN = "span"
    STR = "strong"
    TITLE = "title"


class TOC:
    tag = HTMLTag.H2
    title = "Table of Contents"
    klass = inflection.parameterize(title)


class HTMLRenderer:
    """The Renderer for an HTML document.

    This is a callable class which accepts a :class:`ast.PlayTree` and generates an
    HTML document with attached metadata for easy querying and CSS styling (not
    provided by default).
    """

    tag = HTMLTag

    def render_speech(
        self,
        speech: ast.Speech,
        personae: Mapping[str, ast.Persona],
        doc: yattag.SimpleDoc,
    ):
        """Render a "speech" node.

        A :class:`ast.SpeechNode` is a container for all lines of dialogue, character
        action, or stage direction which can be attributed to an individual section of
        speech for a character.

        Parameters
        ----------
        speech
            The speech node to render to html.
        doc
            The document object which the spech will be rendered to.
        personae
            A mapping of :py:attr:`Persona.id` -> :py:class:`Persona`
        """
        persona = personae[speech.persona]
        doc.line(
            self.tag.STR.value,
            persona.name,
            klass=persona.klass,
            id=f"{persona.id}-{speech.id}",
        )
        doc.stag(self.tag.BR.value)
        last_line = None
        for line in speech.body:
            with doc.tag(self.tag.SPAN.value, klass=line.klass, id=line.id):
                doc.data(index=line.index)
                if isinstance(line, ast.Action):
                    if last_line:
                        doc.stag(self.tag.BR.value)
                    doc.line(self.tag.EM.value, f"[{line.action}]")
                elif isinstance(line, ast.Direction):
                    doc.stag(self.tag.BR.value)
                    doc.line(self.tag.EM.value, line.action)
                    doc.stag(self.tag.BR.value)
                else:
                    doc.data(lineno=line.lineno)
                    doc.text(line.line)
                doc.stag(self.tag.BR.value)
            last_line = line

    def render_scene(
        self,
        scene: ast.ActNodeT,
        doc: yattag.SimpleDoc,
        personae: Mapping[str, ast.Persona],
        *,
        as_act: bool = False,
    ):
        """Render a "scene". This could be either a :class:`ast.NodeTree` or
        :class:`ast.Intermission`

        Parameters
        ----------
        scene
            A child of the higher-level "act" - which could be a :class:`ast.Act`,
            :class:`ast.Epilogue`, or :class:`ast.Prologue`
        doc
            The initialized document object.
        personae
            A mapping of :py:attr:`Persona.id` -> :py:class:`Persona`
        as_act : default False
            Optionally render this scene at the "act" level (:class:`HTMLTag.H1`)
        """
        if isinstance(scene, ast.Intermission):
            with doc.tag(self.tag.H2.value, klass=scene.klass, id=scene.id):
                doc.text(scene.text)
                doc.data(index=scene.index)
        else:
            text = scene.text
            tag = self.tag.H2.value if as_act else self.tag.H3.value
            with doc.tag(tag, klass=scene.klass, id=scene.id):
                doc.text(text)
                doc.data(index=scene.index)
            node: ast.SceneNodeT
            for node in scene.body:  # type: ignore
                with doc.tag(self.tag.P.value, klass=node.klass, id=node.id):
                    if isinstance(node, (ast.Direction, ast.Exit, ast.Entrance)):
                        with doc.tag(self.tag.EM.value):
                            doc.text(
                                node.action
                                if isinstance(node, ast.Direction)
                                else node.text
                            )
                            doc.data(index=node.index)
                        continue
                    self.render_speech(node, personae, doc)

    def render_play(self, tree: ast.Play) -> yattag.SimpleDoc:
        doc = yattag.SimpleDoc()
        persona_map = {x.id: x for x in tree.personae}
        for act in tree.body:
            if isinstance(act, (ast.Prologue, ast.Epilogue)) and not act.as_act:
                self.render_scene(act, doc, persona_map, as_act=True)
                continue
            with doc.tag(self.tag.H2.value, klass=act.klass, id=act.id):
                doc.data(index=act.index)
                doc.text(act.text)
            scene: ast.ActNodeT
            for scene in act.body:  # type: ignore
                if isinstance(scene, ast.Intermission):
                    with doc.tag(self.tag.H2.value, klass=scene.klass, id=scene.id):
                        doc.data(index=scene.index)
                        doc.text(scene.text)
                    continue
                self.render_scene(scene, doc, persona_map)
        return doc

    def render_toc(self, tree: ast.Play) -> yattag.SimpleDoc:
        toc = yattag.SimpleDoc()
        with toc.tag(
            self.tag.NAV.value,
            klass=TOC.klass,
            id=f"{inflection.parameterize(str(tree.meta.title))}-{TOC.klass}",
            role="navigation",
        ):
            toc.line(TOC.tag.value, TOC.title)
            with toc.tag(self.tag.OL.value):
                for act in tree.body:
                    with toc.tag(self.tag.LI.value):
                        toc.line(self.tag.A.value, act.text, href=f"#{act.id}")
                        if isinstance(act, ast.Act) or act.as_act:
                            with toc.tag(self.tag.OL.value):
                                scene: ast.ActNodeT
                                for scene in act.body:  # type: ignore
                                    with toc.tag(self.tag.LI.value):
                                        toc.line(
                                            self.tag.A.value,
                                            scene.text,
                                            href=f"#{scene.id}",
                                        )
        return toc

    def render_head(self, tree: ast.Play) -> yattag.SimpleDoc:
        head = yattag.SimpleDoc()
        with head.tag(self.tag.HEAD.value):
            head.line(self.tag.TITLE.value, tree.meta.title or "")
            head.stag(self.tag.META.value, name="language", content=tree.meta.language)
            head.stag(
                self.tag.META.value, name="publisher", content=tree.meta.publisher
            )
            head.stag(self.tag.META.value, name="rights", content=tree.meta.rights)
            head.stag(self.tag.META.value, name="author", content=tree.meta.author)
            head.stag(self.tag.META.value, name="edition", content=tree.meta.edition)
            head.stag(
                self.tag.META.value, name="editors", content=",".join(tree.meta.editors)
            )
            head.stag(
                self.tag.META.value, name="keywords", content=",".join(tree.meta.tags)
            )
            head.stag(
                self.tag.META.value,
                name="viewport",
                content="width=device-width, initial-scale=1.0",
            )

        return head

    def render(
        self, tree: ast.Play, as_text: bool = True, with_toc: bool = True
    ) -> Union[yattag.SimpleDoc, str]:
        """Render a :class:`ast.PlayTree` into an HTML document.

        Parameters
        ----------
        tree :
            The play tree, as loaded via :func:`~iambic.parser.parse` or
            :func:`~iambic.loader.load`
        as_text : default True
            Optionally return the raw :class:`yattag.SimpleDoc` if set to False.
        with_toc : default True
            Optionally turn off TOC rendering.
        """
        head = self.render_head(tree)
        play = self.render_play(tree)
        toc = self.render_toc(tree) if with_toc else yattag.SimpleDoc()
        doc = yattag.SimpleDoc()
        doc.asis(self.tag.DTYPE)
        with doc.tag(self.tag.HTML.value, lang="en"):
            doc.result.extend(head.result)
            with doc.tag(self.tag.BODY.value):
                doc.result.extend(toc.result)
                doc.result.extend(play.result)

        return yattag.indent(doc.getvalue()) if as_text else doc

    # Assign the highest-level method to the public API
    __call__ = render


# Pin the callable as the public API
render_html = HTMLRenderer()
