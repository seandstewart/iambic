#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import iambic
from tests.static import MATRIX, PARSED, TABLE

play = PARSED


def test_tabulate():
    assert iambic.render.table.tabulate(play) == TABLE


def test_matrix():
    assert iambic.render.table.matrix(TABLE) == MATRIX
