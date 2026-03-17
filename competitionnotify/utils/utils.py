#!/bin/python

import typing
import collections.abc
import typeguard
import attrs
import logging
import uuid
import datetime
import re

logger = logging.getLogger(__name__)

@typeguard.typechecked
def testAttrsClass(cls: typing.Any) -> bool:
	if isinstance(cls, type):
		return attrs.has(cls)
	return attrs.has(cls.__class__)

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
T = typing.TypeVar('T') # Declare type variable "U"

@typeguard.typechecked
def class_factory(d: dict[str, typing.Any], c: type[U], t: type[T]|None = None) -> U|None:
	e = sanitize(attrs.fields_dict(c), d)
	if e is None:
		return None
	if t is None:
		return c(**e)
	else:
		return c[T](**e) # type: ignore [index,misc]

# @typeguard.typechecked
# def class_factory(d: dict[str, typing.Any], c: type[U]) -> U|None:
# 	e = sanitize(attrs.fields_dict(c), d)
# 	if e is None:
# 		return None
# 	return c(**e)

@typeguard.typechecked
def class_converter_none(data: U|dict[str, typing.Any]|None, c: type[U], t: type[T]|None = None) -> U|None:
	if isinstance(data, c):
		typeguard.check_type(data, c)
		return data
	elif data is not None:
		res = class_factory(data, c, t) # type: ignore[arg-type]
		if res is not None:
			return res
	return None

@typeguard.typechecked
def class_converter_except(data: U|dict[str, typing.Any]|None, c: type[U], t: type[T]|None = None) -> U:
	if isinstance(data, c):
		typeguard.check_type(data, c)
		return data
	elif data is not None:
		res = class_factory(data, c, t) # type: ignore[arg-type]
		if res is not None:
			return res
	raise ValueError('error in SettingClass_converter')

@typeguard.typechecked
def ClassTuple_converter(data: tuple[U,...]|list[dict[str, typing.Any]]|dict[str, typing.Any]|None, c: type[U]) -> tuple[U,...]:
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

@typeguard.typechecked
def uuid_converter(data: uuid.UUID|str) -> uuid.UUID:
	if isinstance(data, uuid.UUID):
		return data
	else:
		return uuid.UUID(data, version=4)

@typeguard.typechecked
def datetime_converter(data: datetime.datetime|str) -> datetime.datetime:
	if isinstance(data, datetime.datetime):
		return data
	else:
		return datetime.datetime.fromisoformat(data)

@typeguard.typechecked
def datetime_converter_none(data: datetime.datetime|str|None) -> datetime.datetime|None:
	if data is None:
		return None
	else:
		return datetime_converter(data)

@typeguard.typechecked
def date_converter(date_str: str) -> datetime.date:
	return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

@typeguard.typechecked
def string_to_tuple_int_converter(string: collections.abc.Sequence[int]|str|None) -> tuple[int, ...]:
	if isinstance(string, tuple):
		typeguard.check_type(string, tuple[int, ...])
		return string
	l: list[int] = []
	if isinstance(string, str):
		parts = re.split(r'[,;|\s]+', string)
		for p in parts:
			if len(p) == 0:
				continue
			value: int
			try:
				value = int(p)
				if str(value) != p:
					continue
			except ValueError:
				continue

			l.append(value)

	return tuple(l)

@typeguard.typechecked
def string_to_tuple_str_converter(data: collections.abc.Sequence[str]|str|None) -> tuple[str, ...]:
	if data is None:
		return tuple()
	elif isinstance(data, tuple):
		return typeguard.check_type(data, tuple[str, ...])
	elif isinstance(data, collections.abc.Sequence):
		return tuple([p for p in data if (isinstance(p, str) and len(p) > 0)])
	elif isinstance(data, str):
		parts = re.split(r'[,;|\s]+', data)
		return tuple([p for p in parts if len(p) > 0])
	else:
		return tuple()
