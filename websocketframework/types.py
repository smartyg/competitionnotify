#!/bin/python

import collections.abc
import typing
import uuid

DataType = None|bool|int|str|list|dict
Callback = collections.abc.Callable[[uuid.UUID, ...], DataType]|collections.abc.Callable[[uuid.UUID], DataType]
CommandList = collections.abc.Sequence[tuple[str, Callback]|tuple[str, Callback, str]]
