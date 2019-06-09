#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import iambic

from tests.static import PARSED, TABLE, MATRIX, DATASET


play = PARSED


def test_tabulate():
    assert iambic.render.table.tabulate(play) == TABLE


def test_matrix():
    assert iambic.render.table.matrix(TABLE) == MATRIX


def test_dataset():
    assert (
        iambic.render.table.dataset(TABLE).csv.rstrip("\n").replace("\r", "") == DATASET
    )
