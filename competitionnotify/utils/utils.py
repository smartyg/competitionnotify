#!/bin/python

from typing import Any, TypeVar
import attrs
import logging

logger = logging.getLogger(__name__)

def sanitize(fields: dict[str, "attrs.Attribute[Any]"], d: dict[str, Any]) -> dict[str, Any]|None:
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

U = TypeVar('U', bound=type[attrs.AttrsInstance]) # Declare type variable "U"

def class_factory(d: dict[str, Any], c: U) -> U|None:
	e = sanitize(attrs.fields_dict(c), d)
	if e is None:
		return None
	return c(**e)

def class_converter_none(data: dict[str, Any]|None, c: U) -> U|None:
	if data is not None:
		res = class_factory(data, c)
		if res is not None:
			return res
	return None

def class_converter_except(data: dict[str, Any]|None, c: U) -> U:
	if data is not None:
		res = class_factory(data, c)
		if res is not None:
			return res
	raise ValueError('error in SettingClass_converter')
