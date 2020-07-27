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


typic.register(deserializer=node_deserializer, check=isnodetype)
typic.register(
    deserializer=log_deserializer, check=lambda o: o == LogueBodyT  # type: ignore
)
typic.resolve()
