#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# flake8: noqa
import enum
from typing import Union

import typic

from .base import *
from .index import *
from .node import *


class InputType(str, enum.Enum):
    HTML = "html"
    MD = "markdown"
    DATA = "data"


protocol = typic.protocol(Union[Play, ResolvedNodeT])  # type: ignore
