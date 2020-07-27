# flake8: noqa
from iambic.ast import *

PARSED = Play(
    body=(
        Prologue(
            index=0,
            text="Prologue",
            setting=None,
            act=None,
            body=(
                Entrance(
                    index=1,
                    text="Enter FOO",
                    scene=NodeID("prologue"),
                    personae=(NodeID("foo"),),
                ),
                Speech(
                    persona=NodeID("foo"),
                    scene=NodeID("prologue"),
                    body=(
                        Dialogue(
                            line="Bar.",
                            persona=NodeID("foo"),
                            scene=NodeID("prologue"),
                            index=3,
                            lineno=1,
                            linepart=0,
                        ),
                    ),
                    index=3,
                ),
                Speech(
                    persona=NodeID("a-bar"),
                    scene=NodeID("prologue"),
                    body=(
                        Dialogue(
                            line="Bar!",
                            persona=NodeID("a-bar"),
                            scene=NodeID("prologue"),
                            index=5,
                            lineno=2,
                            linepart=0,
                        ),
                    ),
                    index=5,
                ),
                Speech(
                    persona=NodeID("bar-s-foo"),
                    scene=NodeID("prologue"),
                    body=(
                        Dialogue(
                            line="Foo!",
                            persona=NodeID("bar-s-foo"),
                            scene=NodeID("prologue"),
                            index=7,
                            lineno=3,
                            linepart=0,
                        ),
                    ),
                    index=7,
                ),
                Exit(index=8, text="Exeunt", scene=NodeID("prologue"), personae=()),
            ),
            personae=(NodeID("bar-s-foo"), NodeID("a-bar"), NodeID("foo")),
        ),
        Act(
            index=9,
            text="ACT I",
            num=1,
            body=(
                Prologue(
                    index=10,
                    text="Prologue",
                    setting=None,
                    act=NodeID("act-i"),
                    body=(
                        Entrance(
                            index=11,
                            text="Enter BAR",
                            scene=NodeID("act-i-prologue"),
                            personae=(NodeID("bar"),),
                        ),
                        Speech(
                            persona=NodeID("bar"),
                            scene=NodeID("act-i-prologue"),
                            body=(
                                Action(
                                    action="Aside",
                                    persona=NodeID("bar"),
                                    scene=NodeID("act-i-prologue"),
                                    index=13,
                                ),
                                Dialogue(
                                    line="Foo.",
                                    persona=NodeID("bar"),
                                    scene=NodeID("act-i-prologue"),
                                    index=14,
                                    lineno=4,
                                    linepart=0,
                                ),
                            ),
                            index=13,
                        ),
                    ),
                    personae=(NodeID("bar"),),
                ),
                Intermission(index=15, text="INTERMISSION", act=NodeID("act-i")),
                Scene(
                    index=16,
                    text="SCENE I",
                    num=1,
                    act=NodeID("act-i"),
                    setting=None,
                    body=(
                        Entrance(
                            index=17,
                            text="Enter FOO and BAR",
                            scene=NodeID("act-i-scene-i"),
                            personae=(NodeID("foo"), NodeID("bar")),
                        ),
                        Speech(
                            persona=NodeID("foo"),
                            scene=NodeID("act-i-scene-i"),
                            body=(
                                Action(
                                    action="To BAR",
                                    persona=NodeID("foo"),
                                    scene=NodeID("act-i-scene-i"),
                                    index=19,
                                ),
                                Dialogue(
                                    line="Bar.",
                                    persona=NodeID("foo"),
                                    scene=NodeID("act-i-scene-i"),
                                    index=20,
                                    lineno=5,
                                    linepart=0,
                                ),
                            ),
                            index=19,
                        ),
                        Speech(
                            persona=NodeID("bar"),
                            scene=NodeID("act-i-scene-i"),
                            body=(
                                Dialogue(
                                    line="Foo.",
                                    persona=NodeID("bar"),
                                    scene=NodeID("act-i-scene-i"),
                                    index=22,
                                    lineno=6,
                                    linepart=0,
                                ),
                            ),
                            index=22,
                        ),
                        Speech(
                            persona=NodeID("foo"),
                            scene=NodeID("act-i-scene-i"),
                            body=(
                                Dialogue(
                                    line="Bar. ...",
                                    persona=NodeID("foo"),
                                    scene=NodeID("act-i-scene-i"),
                                    index=24,
                                    lineno=7,
                                    linepart=1,
                                ),
                            ),
                            index=24,
                        ),
                        Speech(
                            persona=NodeID("bar"),
                            scene=NodeID("act-i-scene-i"),
                            body=(
                                Dialogue(
                                    line="... Foo. ...",
                                    persona=NodeID("bar"),
                                    scene=NodeID("act-i-scene-i"),
                                    index=26,
                                    lineno=7,
                                    linepart=2,
                                ),
                            ),
                            index=26,
                        ),
                        Speech(
                            persona=NodeID("foo"),
                            scene=NodeID("act-i-scene-i"),
                            body=(
                                Dialogue(
                                    line="... Bar.",
                                    persona=NodeID("foo"),
                                    scene=NodeID("act-i-scene-i"),
                                    index=28,
                                    lineno=7,
                                    linepart=3,
                                ),
                                Direction(
                                    action="A long stage direction that goes on forever and says far to much to be reasonable. So much so that it takes up more than two lines, which is just ridiculous. I mean seriously, why? Why write so much for one stage direction? For what purpose?",
                                    scene=NodeID("act-i-scene-i"),
                                    index=29,
                                    stop=True,
                                ),
                            ),
                            index=28,
                        ),
                    ),
                    personae=(NodeID("foo"), NodeID("bar")),
                ),
                Epilogue(
                    index=33,
                    text="EPILOGUE",
                    setting=None,
                    act=NodeID("act-i"),
                    body=(
                        Entrance(
                            index=34,
                            text="Enter FOO and BAR",
                            scene=NodeID("act-i-epilogue"),
                            personae=(NodeID("foo"), NodeID("bar")),
                        ),
                        Speech(
                            persona=NodeID("foo"),
                            scene=NodeID("act-i-epilogue"),
                            body=(
                                Action(
                                    action="Reads",
                                    persona=NodeID("foo"),
                                    scene=NodeID("act-i-epilogue"),
                                    index=36,
                                ),
                                Dialogue(
                                    line="Foo.",
                                    persona=NodeID("foo"),
                                    scene=NodeID("act-i-epilogue"),
                                    index=37,
                                    lineno=8,
                                    linepart=0,
                                ),
                            ),
                            index=36,
                        ),
                    ),
                    personae=(NodeID("foo"),),
                ),
            ),
        ),
    ),
    personae=(
        Persona(index=2, text="FOO", name="Foo", short=None),
        Persona(index=4, text="A Bar", name="A Bar", short=None),
        Persona(index=6, text="Bar's Foo", name="Bar's Foo", short=None),
        Persona(index=12, text="BAR", name="Bar", short=None),
    ),
    meta=Metadata(),
)
