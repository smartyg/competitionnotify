#!/bin/python

import attrs
import pickle
import zlib
import json
from typing import Any
from collections.abc import Callable

@attrs.define(frozen=True, kw_only=True, slots=False)
class BaseClass:
	_SERIALIZE_TYPE = '__serialize_type'

	@staticmethod
	def deserialize(compressed_data: bytes):
		decompressed = zlib.decompress(compressed_data)
		obj = pickle.loads(decompressed)
		if issubclass(type(obj), BaseClass):
			return obj
		else:
			print("error")

	def serialize(self) -> bytes:
		data = pickle.dumps(self, pickle.DEFAULT_PROTOCOL)
		compressed = zlib.compress(data, level=9)
		return compressed

	def json (self) -> str:
		return json.dumps(self.asdict())

	def asdict(self) -> dict[str, Any]:
		fields = attrs.fields(type(self))
		d: dict[str, Any] = {}
		for field in fields:
			field_type: int|None = field.metadata.get(BaseClass._SERIALIZE_TYPE, None)
			#print(field)
			if not field.init:
				continue
			if field_type is None:
				continue
			d[field.alias] = self.__getattribute__(field.name)

		return d

	@staticmethod
	def serializable(serialize_func: Callable[["BaseClass", str, Any], Any]|None|bool, default=attrs.NOTHING, validator=None, repr=True, hash=None, init=True, metadata=None, type=None, converter=None, factory=None, kw_only=False, eq=None, order=None, on_setattr=None, alias=None):
		metadata = metadata or {}
		metadata[BaseClass._SERIALIZE_TYPE] = serialize_func
		return attrs.field(default=default, validator=validator, repr=repr, hash=hash, init=init, metadata=metadata, type=type, converter=converter, factory=factory, kw_only=kw_only, eq=eq, order=order, on_setattr=on_setattr, alias=alias)

@attrs.define(frozen=True, kw_only=True, slots=False)
class ComparableClass(BaseClass):
	_COMPARE_TYPE = '__compare_type'
	COMPARE_DEEP = -2
	NO_COMPARE = -1

	def compare(self, c: "BaseClass") -> int:
		if type(self) is not type(c):
			print("Can not compare")
			return -1

		result:int = 0
		fields = attrs.fields(type(self))
		for field in fields:
			cmp_type: int|None = field.metadata.get(BaseClass._COMPARE_TYPE, None)
			#print(field)
			if cmp_type is None:
				continue
			if cmp_type == BaseClass.NO_COMPARE:
				continue

			if cmp_type == BaseClass.COMPARE_DEEP:
				a = self.__getattribute__(field.name)
				result |= a.compare(c.__getattribute__(field.name))
			elif field.eq:
				if callable(field.eq_key):
					func = field.eq_key
					a = func(self.__getattribute__(field.name))
					b = func(c.__getattribute__(field.name))
					if a == b:
						continue
					else:
						print("fields " + field.name + " are not equal")
						result |= cmp_type
				else:
					a = self.__getattribute__(field.name)
					b = c.__getattribute__(field.name)
					if a == b:
						continue
					else:
						print("fields " + field.name + " are not equal")
						result |= cmp_type
			else:
				print("fields are not comparable")
				return -1
		return result

	def getFirstFieldName(self) -> str|None:
		return BaseClass.getFirstFieldName(type(self))

	@staticmethod
	def getFirstFieldName(c: "BaseClass") -> str|None:
		fields = attrs.fields(c)
		if (len(fields)) >= 1:
			return fields[0].alias
		else:
			return None

	@staticmethod
	def comparable(cmp_type: int = -1, default=attrs.NOTHING, validator=None, repr=True, hash=None, init=True, metadata=None, type=None, converter=None, factory=None, kw_only=False, eq=None, order=None, on_setattr=None, alias=None):
		metadata = metadata or {}
		metadata[BaseClass._COMPARE_TYPE] = cmp_type
		return attrs.field(default=default, validator=validator, repr=repr, hash=hash, init=init, metadata=metadata, type=type, converter=converter, factory=factory, kw_only=kw_only, eq=eq, order=order, on_setattr=on_setattr, alias=alias)