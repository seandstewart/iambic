#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import json
import pathlib

from .frozendict import frozendict
from .dataschema import dataschema

SCHEMA_PATH = pathlib.Path(__file__).resolve().parent / "schema.json"
SCHEMA = json.loads(SCHEMA_PATH.read_text())
