#!/usr/bin/python

import typing
import typeguard
import logging
import attrs
import datetime
import uuid
import pickle
import zlib

import competitionnotify.classes.base as base

logger = logging.getLogger(__name__)

@typeguard.typechecked
def _container_data_converter(data: base.BaseClass|bytes) -> bytes:
	if isinstance(data, base.BaseClass):
		return data.serialize()
	elif isinstance(data, bytes):
		return data
	else:
		raise ValueError(f'variable `data` is of type `{type(data)}` while an instance of `base.BaseClass` is expected.')

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
	_cache_file: str|None = None
	_max_elements: int|None = 100
	_max_time: int|None = None

	def __init__(self, max_elements: int|None = None, max_time: int|None = None, cache_file: str|None = None):
		self._max_elements = max_elements
		self._max_time = max_time
		self._cache_file = cache_file
		if self._cache_file is not None:
			self._cache = Cache._loadCache(self._cache_file)

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
		if self._cache_file is not None:
			self._saveCache()

	def stats() -> str:
		part2: str = ""
		if self._cache_file is not None:
			part2: str = f"\nSize of cache file on disk {}\nLast cache save: {}"
		part: str = f"Number of cached items: {len(self._cache)}" + part2
		return part
		
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

	def _saveCache(self) -> None:
		data = pickle.dumps(self._cache, pickle.DEFAULT_PROTOCOL)
		compressed = zlib.compress(data, level=9)
		with open(self._cache_file, "wb") as f:
  			f.write(compressed)

	def _loadCache(self, cache_file: str) -> dict[uuid.UUID, Container]:
		try:
			with open(cache_file, "rb") as f:
	  			compressed_data: bytes = f.read(compressed)
			decompressed = zlib.decompress(compressed_data)
			obj = pickle.loads(decompressed)
			obj_type = type(obj)
			if not issubclass(obj_type, dict):
				ValueError("Can not read data from cache file")
			return obj
		except:
			return {}
		
_cache_data: dict[str, cache.Cache] = {}

@typeguard.typechecked
async def cache(max_elements: int|None = None, max_time: int|None = None, cache_file: str|None = None):
	def cache(func):
		index_name: str = str(func.__qualname__)
		if index_name not in _cache_data:
			logger.info (f'Init cache for function `{index_name}`.')
			_cache_data[index_name] = cache.Cache(max_elements, max_time, cache_file)
		def wrapper(**kwargs):
			id = kwargs['id']
			r: base.BaseClass|None = _cache_data[index_name].get(id)
			if r is not None:
				logger.debug (f'Retrieve stored data for id `{id}`.')
				return r
			else:
				logger.debug (f'No stored data for id `{id}` availible.')
				r = await func(**kwargs)
				_cache_data[index_name].add(id, r)
			return r
		return wrapper
	return cache

def cache_stats(func) -> None:
	index_name: str = str(func.__qualname__)
	if index_name in _cache_data:
		logger.debug(_cache_data[index_name].stats())
	
