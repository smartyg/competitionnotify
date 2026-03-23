#!/usr/bin/python

import typing
import typeguard
import logging
import attrs
import datetime
import uuid

import competitionnotify.classes.base as base
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
def _container_data_converter(data: base.BaseClass|bytes) -> bytes:
	if isinstance(data, base.BaseClass):
		return data.serialize()
	elif isinstance(data, bytes):
		return data
	else:
		raise ValueError("variable `data` is of type `" + str(type(data)) + "` while an instance of `base.BaseClass` is expected.")

@typeguard.typechecked
def _container_data_validator(instance, attribute, value):
	cls = base.BaseClass.deserialize(value)
	if not isinstance(cls, base.BaseClass):
		raise ValueError("value is of type `" + str(type(value)) + "` while an instance of `base.BaseClass` is expected.")

@typeguard.typechecked
class Cache:
	@attrs.define(frozen=True, kw_only=False, slots=False)
	class Container:
		_data: bytes = base.BaseClass.serializable(True, converter=_container_data_converter, validator=[attrs.validators.instance_of(bytes), _container_data_validator])
		_date: datetime.datetime = base.BaseClass.serializable(True, default=datetime.datetime.now(), validator=attrs.validators.instance_of(datetime.datetime))

		def isValid(self, experation: int) -> bool:
			return datetime.datetime.now() < (self._date + datetime.timedelta(seconds=experation))
			
		def data(self) -> base.BaseClass:
			return base.BaseClass.deserialize(self._data)

		def date(self) -> datetime.datetime:
			return self._date

	_cache: dict[uuid.UUID, Container] = {}
	#_cache_file: str|None = None
	_max_elements: int|None = 100
	_max_time: int|None = None

	def __init__(self, max_elements: int|None = None, max_time: int|None = None, cache_file: str|None = None):
		self._max_elements = max_elements
		self._max_time = max_time
		#self._cache_file = cache_file
		# if self._cache_file is not None:
		# 	self._data = Cache._loadCache(self._cache_file, self._max_elements, self._max_time)

	def get(self, id: uuid.UUID, experation: int = -1) -> typing.Any|None:
		if id in self._cache:
			storage_container = self._cache[id]
			if storage_container.isValid(min(self._max_time, experation)):
				return storage_container.data()
		return None

	def add(self, id: uuid.UUID, data: base.BaseClass) -> None:
		storage_container = self.Container(data)
		self._cache[id] = storage_container
		self._checkCache()

	def _checkCache(self):
		for id, storage_container in self._cache.items():
			if not storage_container.isValid(self._max_time):
				self._cache.pop(id)
		while len(self._cache.items()) > self._max_elements:
			oldest_id: uuid.UUID|None = None
			age: datetime.datetime|None = None
			for id, storage_container in self._cache.items():
				if oldest_id is None:
					oldest_id = id
					age = storage_container.date()
				elif storage_container.date() < age:
					oldest_id = id
					age = storage_container.date()
			if oldest_id is not None:
				self._cache.pop(oldest_id)

	# def _saveCache(self) -> None:
	# 	data = pickle.dumps(self._cache, pickle.DEFAULT_PROTOCOL)
	# 	compressed = zlib.compress(data, level=9)
		
