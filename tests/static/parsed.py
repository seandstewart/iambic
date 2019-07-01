from iambic.ast import *

PARSED = Play(
    children=(
        NodeTree(
            node=Prologue(index=0, text="Prologue", setting=None, act=None),
            children=(
                Entrance(
                    index=1,
                    text="Enter FOO",
                    scene=Prologue(index=0, text="Prologue", setting=None, act=None),
                    personae=(),
                ),
                Speech(
                    persona=Persona(index=35, text="FOO", name="Foo", short=None),
                    scene=Prologue(index=0, text="Prologue", setting=None, act=None),
                    speech=(
                        Dialogue(
                            line="Bar.",
                            persona=Persona(
                                index=35, text="FOO", name="Foo", short=None
                            ),
                            scene=Prologue(
                                index=0, text="Prologue", setting=None, act=None
                            ),
                            index=3,
                            lineno=1,
                            linepart=0,
                        ),
                    ),
                    index=3,
                ),
                Speech(
                    persona=Persona(index=4, text="A Bar", name="A Bar", short=None),
                    scene=Prologue(index=0, text="Prologue", setting=None, act=None),
                    speech=(
                        Dialogue(
                            line="Bar!",
                            persona=Persona(
                                index=4, text="A Bar", name="A Bar", short=None
                            ),
                            scene=Prologue(
                                index=0, text="Prologue", setting=None, act=None
                            ),
                            index=5,
                            lineno=2,
                            linepart=0,
                        ),
                    ),
                    index=5,
                ),
                Speech(
                    persona=Persona(
                        index=6, text="Bar's Foo", name="Bar'S Foo", short=None
                    ),
                    scene=Prologue(index=0, text="Prologue", setting=None, act=None),
                    speech=(
                        Dialogue(
                            line="Foo!",
                            persona=Persona(
                                index=6, text="Bar's Foo", name="Bar'S Foo", short=None
                            ),
                            scene=Prologue(
                                index=0, text="Prologue", setting=None, act=None
                            ),
                            index=7,
                            lineno=3,
                            linepart=0,
                        ),
                    ),
                    index=7,
                ),
                Exit(
                    index=8,
                    text="Exeunt",
                    scene=Prologue(index=0, text="Prologue", setting=None, act=None),
                    personae=(),
                ),
            ),
            personae=(
                Persona(index=4, text="A Bar", name="A Bar", short=None),
                Persona(index=6, text="Bar's Foo", name="Bar'S Foo", short=None),
                Persona(index=35, text="FOO", name="Foo", short=None),
            ),
        ),
        NodeTree(
            node=Act(index=9, text="ACT I", num=1),
            children=(
                NodeTree(
                    node=Prologue(
                        index=10,
                        text="Prologue",
                        setting=None,
                        act=Act(index=9, text="ACT I", num=1),
                    ),
                    children=(
                        Entrance(
                            index=11,
                            text="Enter BAR",
                            scene=Prologue(
                                index=10,
                                text="Prologue",
                                setting=None,
                                act=Act(index=9, text="ACT I", num=1),
                            ),
                            personae=(),
                        ),
                        Speech(
                            persona=Persona(
                                index=25, text="BAR", name="Bar", short=None
                            ),
                            scene=Prologue(
                                index=10,
                                text="Prologue",
                                setting=None,
                                act=Act(index=9, text="ACT I", num=1),
                            ),
                            speech=(
                                Action(
                                    action="Aside",
                                    persona=Persona(
                                        index=25, text="BAR", name="Bar", short=None
                                    ),
                                    scene=Prologue(
                                        index=10,
                                        text="Prologue",
                                        setting=None,
                                        act=Act(index=9, text="ACT I", num=1),
                                    ),
                                    index=13,
                                ),
                                Dialogue(
                                    line="Foo.",
                                    persona=Persona(
                                        index=25, text="BAR", name="Bar", short=None
                                    ),
                                    scene=Prologue(
                                        index=10,
                                        text="Prologue",
                                        setting=None,
                                        act=Act(index=9, text="ACT I", num=1),
                                    ),
                                    index=14,
                                    lineno=4,
                                    linepart=0,
                                ),
                            ),
                            index=13,
                        ),
                    ),
                    personae=(Persona(index=25, text="BAR", name="Bar", short=None),),
                ),
                Intermission(
                    index=15, text="INTERMISSION", act=Act(index=9, text="ACT I", num=1)
                ),
                NodeTree(
                    node=Scene(
                        index=16,
                        text="SCENE I",
                        num=1,
                        act=Act(index=9, text="ACT I", num=1),
                        setting=None,
                    ),
                    children=(
                        Entrance(
                            index=17,
                            text="Enter FOO and BAR",
                            scene=Scene(
                                index=16,
                                text="SCENE I",
                                num=1,
                                act=Act(index=9, text="ACT I", num=1),
                                setting=None,
                            ),
                            personae=(),
                        ),
                        Speech(
                            persona=Persona(
                                index=35, text="FOO", name="Foo", short=None
                            ),
                            scene=Scene(
                                index=16,
                                text="SCENE I",
                                num=1,
                                act=Act(index=9, text="ACT I", num=1),
                                setting=None,
                            ),
                            speech=(
                                Action(
                                    action="To BAR",
                                    persona=Persona(
                                        index=35, text="FOO", name="Foo", short=None
                                    ),
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=19,
                                ),
                                Dialogue(
                                    line="Bar.",
                                    persona=Persona(
                                        index=35, text="FOO", name="Foo", short=None
                                    ),
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=20,
                                    lineno=5,
                                    linepart=0,
                                ),
                            ),
                            index=19,
                        ),
                        Speech(
                            persona=Persona(
                                index=25, text="BAR", name="Bar", short=None
                            ),
                            scene=Scene(
                                index=16,
                                text="SCENE I",
                                num=1,
                                act=Act(index=9, text="ACT I", num=1),
                                setting=None,
                            ),
                            speech=(
                                Dialogue(
                                    line="Foo.",
                                    persona=Persona(
                                        index=25, text="BAR", name="Bar", short=None
                                    ),
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=22,
                                    lineno=6,
                                    linepart=0,
                                ),
                            ),
                            index=22,
                        ),
                        Speech(
                            persona=Persona(
                                index=35, text="FOO", name="Foo", short=None
                            ),
                            scene=Scene(
                                index=16,
                                text="SCENE I",
                                num=1,
                                act=Act(index=9, text="ACT I", num=1),
                                setting=None,
                            ),
                            speech=(
                                Dialogue(
                                    line="Bar. ...",
                                    persona=Persona(
                                        index=35, text="FOO", name="Foo", short=None
                                    ),
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=24,
                                    lineno=7,
                                    linepart=0,
                                ),
                            ),
                            index=24,
                        ),
                        Speech(
                            persona=Persona(
                                index=25, text="BAR", name="Bar", short=None
                            ),
                            scene=Scene(
                                index=16,
                                text="SCENE I",
                                num=1,
                                act=Act(index=9, text="ACT I", num=1),
                                setting=None,
                            ),
                            speech=(
                                Dialogue(
                                    line="... Foo. ...",
                                    persona=Persona(
                                        index=25, text="BAR", name="Bar", short=None
                                    ),
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=26,
                                    lineno=7,
                                    linepart=0,
                                ),
                            ),
                            index=26,
                        ),
                        Speech(
                            persona=Persona(
                                index=35, text="FOO", name="Foo", short=None
                            ),
                            scene=Scene(
                                index=16,
                                text="SCENE I",
                                num=1,
                                act=Act(index=9, text="ACT I", num=1),
                                setting=None,
                            ),
                            speech=(
                                Dialogue(
                                    line="... Bar.",
                                    persona=Persona(
                                        index=35, text="FOO", name="Foo", short=None
                                    ),
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=28,
                                    lineno=7,
                                    linepart=0,
                                ),
                                Direction(
                                    action="A long stage direction that goes on forever and says far to much to be reasonable. So much so that it takes up more than two lines, which is just ridiculous. I mean seriously, why? Why write so much for one stage direction? For what purpose?",
                                    scene=Scene(
                                        index=16,
                                        text="SCENE I",
                                        num=1,
                                        act=Act(index=9, text="ACT I", num=1),
                                        setting=None,
                                    ),
                                    index=29,
                                    stop=True,
                                ),
                            ),
                            index=28,
                        ),
                    ),
                    personae=(
                        Persona(index=35, text="FOO", name="Foo", short=None),
                        Persona(index=25, text="BAR", name="Bar", short=None),
                    ),
                ),
                NodeTree(
                    node=Epilogue(
                        index=33,
                        text="EPILOGUE",
                        setting=None,
                        act=Act(index=9, text="ACT I", num=1),
                    ),
                    children=(
                        Entrance(
                            index=34,
                            text="Enter FOO",
                            scene=Epilogue(
                                index=33,
                                text="EPILOGUE",
                                setting=None,
                                act=Act(index=9, text="ACT I", num=1),
                            ),
                            personae=(),
                        ),
                        Speech(
                            persona=Persona(
                                index=35, text="FOO", name="Foo", short=None
                            ),
                            scene=Epilogue(
                                index=33,
                                text="EPILOGUE",
                                setting=None,
                                act=Act(index=9, text="ACT I", num=1),
                            ),
                            speech=(
                                Action(
                                    action="Reads",
                                    persona=Persona(
                                        index=35, text="FOO", name="Foo", short=None
                                    ),
                                    scene=Epilogue(
                                        index=33,
                                        text="EPILOGUE",
                                        setting=None,
                                        act=Act(index=9, text="ACT I", num=1),
                                    ),
                                    index=36,
                                ),
                                Dialogue(
                                    line="Foo.",
                                    persona=Persona(
                                        index=35, text="FOO", name="Foo", short=None
                                    ),
                                    scene=Epilogue(
                                        index=33,
                                        text="EPILOGUE",
                                        setting=None,
                                        act=Act(index=9, text="ACT I", num=1),
                                    ),
                                    index=37,
                                    lineno=8,
                                    linepart=0,
                                ),
                            ),
                            index=36,
                        ),
                    ),
                    personae=(Persona(index=35, text="FOO", name="Foo", short=None),),
                ),
            ),
            personae=(),
        ),
    ),
    personae=(
        Persona(index=35, text="FOO", name="Foo", short=None),
        Persona(index=4, text="A Bar", name="A Bar", short=None),
        Persona(index=6, text="Bar's Foo", name="Bar'S Foo", short=None),
        Persona(index=25, text="BAR", name="Bar", short=None),
    ),
    meta=MetaData(),
)
