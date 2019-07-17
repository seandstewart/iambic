#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import enum

import typic

from .base import *  # noqa: F403 (we've defined __all__)
from .node import *  # noqa: F403 (we've defined __all__)
from .index import *  # noqa: F403 (we've defined __all__)


class InputType(str, enum.Enum):
    HTML = "html"
    MD = "markdown"
    DATA = "data"


typic.register(coercer=node_coercer, check=isnodetype, check_origin=False)
typic.resolve()
