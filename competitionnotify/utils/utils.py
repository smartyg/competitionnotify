#!/bin/python

import typing
import collections.abc
import typeguard
import attrs
import logging
import competitionnotify.dataclasses.base as base

logger = logging.getLogger(__name__)

@typeguard.typechecked
def sanitize(fields: dict[str, attrs.Attribute], d: dict[str, typing.Any]) -> dict[str, typing.Any]|None:
	e={}
	for f in fields.values():
		name: str
		if f.alias is not None:
			name = f.alias
		else:
			name = f.name

		if f.init == False:
			continue
		elif name in d:
			if d[name] is not None:
				e[name] = d[name]
				continue
		if f.default == attrs.NOTHING:
			print("Error, no value for mandatory field '" + str(name) + "' provided")
			return None
	return e

U = typing.TypeVar('U', bound=attrs.AttrsInstance) # Declare type variable "U"

@typeguard.typechecked
def class_factory(d: dict[str, typing.Any], c: U) -> U|None:
	e = sanitize(attrs.fields_dict(c), d)
	if e is None:
		return None
	return c(**e)

@typeguard.typechecked
def class_converter_none(data: U|dict[str, typing.Any]|None, c: U) -> U|None:
	if isinstance(data, c):
		typeguard.check_type(data, U)
		return data
	elif data is not None:
		res = class_factory(data, c)
		if res is not None:
			return res
	else:
		return None

@typeguard.typechecked
def class_converter_except(data: U|dict[str, typing.Any]|None, c: U) -> U:
	if isinstance(data, c):
		typeguard.check_type(data, U)
		return data
	elif data is not None:
		res = class_factory(data, c)
		if res is not None:
			return res
	raise ValueError('error in SettingClass_converter')

@typeguard.typechecked
def ClassTuple_converter(data: tuple[U,...]|list[dict[str, typing.Any]]|dict[str, typing.Any]|None, c: U) -> tuple[U,...]:
	if isinstance(data, tuple):
		typeguard.check_type(data, tuple[U, ...])
		return data
	elif isinstance(data, list):
		ret: list[U] = []
		for d in data:
			cls = class_factory(d, c)
			if cls is not None:
				ret.append(cls)
		return tuple(ret)
	elif isinstance(data, dict):
		cls = class_factory(data, c)
		if cls is not None:
			return tuple([cls])

	return tuple()

@typeguard.typechecked
def StrTuple_convertor(data: collections.abc.Sequence[str]) -> tuple[str,...]:
	return tuple(data)