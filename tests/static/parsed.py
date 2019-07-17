from iambic.ast import *

PARSED = Play(
    children=(
        NodeTree(
            node=Prologue(index=0, text="Prologue", setting=None, act=None),
            children=(
                Entrance(index=1, text="Enter FOO", scene="prologue", personae=()),
                Speech(
                    persona="foo",
                    scene="prologue",
                    speech=(
                        Dialogue(
                            line="Bar.",
                            persona="foo",
                            scene="prologue",
                            index=3,
                            lineno=1,
                            linepart=0,
                        ),
                    ),
                    index=3,
                ),
                Speech(
                    persona="a-bar",
                    scene="prologue",
                    speech=(
                        Dialogue(
                            line="Bar!",
                            persona="a-bar",
                            scene="prologue",
                            index=5,
                            lineno=2,
                            linepart=0,
                        ),
                    ),
                    index=5,
                ),
                Speech(
                    persona="bar-s-foo",
                    scene="prologue",
                    speech=(
                        Dialogue(
                            line="Foo!",
                            persona="bar-s-foo",
                            scene="prologue",
                            index=7,
                            lineno=3,
                            linepart=0,
                        ),
                    ),
                    index=7,
                ),
                Exit(index=8, text="Exeunt", scene="prologue", personae=()),
            ),
            personae=("foo", "bar-s-foo", "a-bar"),
        ),
        NodeTree(
            node=Act(index=9, text="ACT I", num=1),
            children=(
                NodeTree(
                    node=Prologue(index=10, text="Prologue", setting=None, act="act-i"),
                    children=(
                        Entrance(
                            index=11,
                            text="Enter BAR",
                            scene="act-i-prologue",
                            personae=(),
                        ),
                        Speech(
                            persona="bar",
                            scene="act-i-prologue",
                            speech=(
                                Action(
                                    action="Aside",
                                    persona="bar",
                                    scene="act-i-prologue",
                                    index=13,
                                ),
                                Dialogue(
                                    line="Foo.",
                                    persona="bar",
                                    scene="act-i-prologue",
                                    index=14,
                                    lineno=4,
                                    linepart=0,
                                ),
                            ),
                            index=13,
                        ),
                    ),
                    personae=("bar",),
                ),
                Intermission(index=15, text="INTERMISSION", act="act-i"),
                NodeTree(
                    node=Scene(
                        index=16, text="SCENE I", num=1, act="act-i", setting=None
                    ),
                    children=(
                        Entrance(
                            index=17,
                            text="Enter FOO and BAR",
                            scene="act-i-scene-i",
                            personae=(),
                        ),
                        Speech(
                            persona="foo",
                            scene="act-i-scene-i",
                            speech=(
                                Action(
                                    action="To BAR",
                                    persona="foo",
                                    scene="act-i-scene-i",
                                    index=19,
                                ),
                                Dialogue(
                                    line="Bar.",
                                    persona="foo",
                                    scene="act-i-scene-i",
                                    index=20,
                                    lineno=5,
                                    linepart=0,
                                ),
                            ),
                            index=19,
                        ),
                        Speech(
                            persona="bar",
                            scene="act-i-scene-i",
                            speech=(
                                Dialogue(
                                    line="Foo.",
                                    persona="bar",
                                    scene="act-i-scene-i",
                                    index=22,
                                    lineno=6,
                                    linepart=0,
                                ),
                            ),
                            index=22,
                        ),
                        Speech(
                            persona="foo",
                            scene="act-i-scene-i",
                            speech=(
                                Dialogue(
                                    line="Bar. ...",
                                    persona="foo",
                                    scene="act-i-scene-i",
                                    index=24,
                                    lineno=7,
                                    linepart=0,
                                ),
                            ),
                            index=24,
                        ),
                        Speech(
                            persona="bar",
                            scene="act-i-scene-i",
                            speech=(
                                Dialogue(
                                    line="... Foo. ...",
                                    persona="bar",
                                    scene="act-i-scene-i",
                                    index=26,
                                    lineno=7,
                                    linepart=0,
                                ),
                            ),
                            index=26,
                        ),
                        Speech(
                            persona="foo",
                            scene="act-i-scene-i",
                            speech=(
                                Dialogue(
                                    line="... Bar.",
                                    persona="foo",
                                    scene="act-i-scene-i",
                                    index=28,
                                    lineno=7,
                                    linepart=0,
                                ),
                                Direction(
                                    action="A long stage direction that goes on forever and says far to much to be reasonable. So much so that it takes up more than two lines, which is just ridiculous. I mean seriously, why? Why write so much for one stage direction? For what purpose?",
                                    scene="act-i-scene-i",
                                    index=29,
                                    stop=True,
                                ),
                            ),
                            index=28,
                        ),
                    ),
                    personae=("foo", "bar"),
                ),
                NodeTree(
                    node=Epilogue(index=33, text="EPILOGUE", setting=None, act="act-i"),
                    children=(
                        Entrance(
                            index=34,
                            text="Enter FOO",
                            scene="act-i-epilogue",
                            personae=(),
                        ),
                        Speech(
                            persona="foo",
                            scene="act-i-epilogue",
                            speech=(
                                Action(
                                    action="Reads",
                                    persona="foo",
                                    scene="act-i-epilogue",
                                    index=36,
                                ),
                                Dialogue(
                                    line="Foo.",
                                    persona="foo",
                                    scene="act-i-epilogue",
                                    index=37,
                                    lineno=8,
                                    linepart=0,
                                ),
                            ),
                            index=36,
                        ),
                    ),
                    personae=("foo",),
                ),
            ),
            personae=(),
        ),
    ),
    personae=(
        Persona(index=35, text="FOO", name="Foo", short=None),
        Persona(index=4, text="A Bar", name="A Bar", short=None),
        Persona(index=6, text="Bar's Foo", name="Bar's Foo", short=None),
        Persona(index=25, text="BAR", name="Bar", short=None),
    ),
    meta=MetaData(),
)
