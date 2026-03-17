#!/bin/python

import typing
import collections.abc
import typeguard
import attrs
import pickle
import zlib
import json
import datetime

import competitionnotify.utils.utils as utils

@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class BaseClass:
	_SERIALIZE_TYPE = '__serialize_type'

	@staticmethod
	def deserialize(compressed_data: bytes) -> "BaseClass":
		decompressed = zlib.decompress(compressed_data)
		obj = pickle.loads(decompressed)
		obj_type = type(obj)
		if issubclass(obj_type, BaseClass):
			return obj
		raise ValueError(f'Deserializing resulted in an object of type {obj_type!s} which is not supported.')

	def serialize(self) -> bytes:
		data = pickle.dumps(self, pickle.DEFAULT_PROTOCOL)
		compressed = zlib.compress(data, level=9)
		return compressed

	@staticmethod
	def jsonSerial(obj):
		"""JSON serializer for objects not serializable by default json code"""

		if isinstance(obj, (datetime.datetime, datetime.date)):
			return obj.isoformat()
		elif isinstance(obj, BaseClass):
			return obj.asdict()
		raise TypeError("Type %s not serializable" % type(obj))

	def json (self) -> str:
		return json.dumps(self.asdict(), default=BaseClass.jsonSerial)

	def asdict(self) -> dict[str, typing.Any]:
		fields = attrs.fields(type(self))
		d: dict[str, typing.Any] = {}
		for field in fields:
			field_type: int|None = field.metadata.get(BaseClass._SERIALIZE_TYPE, None)
			#print(field)
			if not field.init:
				continue
			if field_type is None:
				continue
			d[field.alias] = self.__getattribute__(field.name)

		return d

	def __eq__(self, o: object) -> bool:
		if not self._hasCallableMethod("equal"):
			cls_name = type(self).__name__
			raise TypeError(f'Class `{cls_name}` does provide an `equal` method and is therefor not comparable.')
		if o is attrs.NOTHING:
			return False
		if not isinstance(o, type(self)):
			self_cls_name = type(self).__name__
			o_cls_name = type(o).__name__
			raise TypeError(f'Can only use comparison on two objects of the same type (given: {self_cls_name}, {o_cls_name}).')
		return self.equal(o) # type: ignore [attr-defined]

	def __nq__(self, o: object) -> bool:
		if not self._hasCallableMethod("equal"):
			cls_name = type(self).__name__
			raise TypeError(f'Class `{cls_name}` does provide an `equal` method and is therefor not comparable.')
		if o is attrs.NOTHING:
			return False
		if not isinstance(o, type(self)):
			self_cls_name = type(self).__name__
			o_cls_name = type(o).__name__
			raise TypeError(f'Can only use comparison on two objects of the same type (given: {self_cls_name}, {o_cls_name}).')
		return not self.equal(o) # type: ignore [attr-defined]

	def _hasCallableMethod(self, method_name: str) -> bool:
		test = getattr(self, method_name, None)
		if test is None:
			return False
		return callable(test)

	def raiseNotSameObject(self, o: object) -> bool:
		if o is attrs.NOTHING:
			return False
		if not isinstance(o, type(self)):
			self_cls_name = type(self).__name__
			o_cls_name = type(o).__name__
			raise TypeError(f'Objects are not of the same type (given: {self_cls_name}, {o_cls_name}).')
		else:
			return True

	@staticmethod
	def serializable(serialize_func: collections.abc.Callable[["BaseClass", str, typing.Any], typing.Any]|None|bool, default=attrs.NOTHING, validator=None, repr=True, hash=None, init=True, metadata=None, type=None, converter=None, factory=None, kw_only=False, eq=None, order=None, on_setattr=None, alias=None):
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
			cmp_type: int|None = field.metadata.get(ComparableClass._COMPARE_TYPE, None)
			if cmp_type is None:
				continue
			if cmp_type == ComparableClass.NO_COMPARE:
				continue

			if cmp_type == ComparableClass.COMPARE_DEEP:
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
		return getFirstFieldName(type(self))

	@staticmethod
	def comparable(cmp_type: int = -1, default=attrs.NOTHING, validator=None, repr=True, hash=None, init=True, metadata=None, type=None, converter=None, factory=None, kw_only=False, eq=None, order=None, on_setattr=None, alias=None):
		metadata = metadata or {}
		metadata[ComparableClass._COMPARE_TYPE] = cmp_type
		return attrs.field(default=default, validator=validator, repr=repr, hash=hash, init=init, metadata=metadata, type=type, converter=converter, factory=factory, kw_only=kw_only, eq=eq, order=order, on_setattr=on_setattr, alias=alias)

@typeguard.typechecked
def getFirstFieldName(c: type) -> str|None:
	if not utils.testAttrsClass(c):
		return None
	fields = attrs.fields(c)
	if (len(fields)) >= 1:
		return fields[0].alias
	else:
		return None