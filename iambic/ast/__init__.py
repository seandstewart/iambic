#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# flake8: noqa
import enum

import typic

from .base import *
from .node import *
from .index import *


class InputType(str, enum.Enum):
    HTML = "html"
    MD = "markdown"
    DATA = "data"


typic.register(deserializer=node_coercer, check=isnodetype)
typic.resolve()
