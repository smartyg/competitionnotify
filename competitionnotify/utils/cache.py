#!/usr/bin/python

import typing
import typeguard
import logging
import attrs
import datetime
#import uuid
import pickle
import zlib
import inspect

import competitionnotify.classes.base as base

logger = logging.getLogger(__name__)

@typeguard.typechecked
def _container_data_converter(data: base.BaseClass|bytes) -> bytes:
	if isinstance(data, base.BaseClass):
		return data.serialize()
	elif isinstance(data, bytes):
		return data
	else:
		raise ValueError(f'Variable `data` is of type `{type(data)}` while an instance of `base.BaseClass` is expected.')

@typeguard.typechecked
def _container_data_validator(instance, attribute, value):
	cls = base.BaseClass.deserialize(value)
	if not isinstance(cls, base.BaseClass):
		raise ValueError(f'Value is of type `{type(value)}` while an instance of `base.BaseClass` is expected.')

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=False, slots=False)
class _Container:
	_data: bytes = base.BaseClass.serializable(True, converter=_container_data_converter, validator=[attrs.validators.instance_of(bytes), _container_data_validator])
	_date: datetime.datetime = base.BaseClass.serializable(True, default=datetime.datetime.now(), validator=attrs.validators.instance_of(datetime.datetime))

	def isValid(self, experation: int) -> bool:
		return datetime.datetime.now() < (self._date + datetime.timedelta(seconds=experation))

	def data(self) -> base.BaseClass:
		return base.BaseClass.deserialize(self._data)

	def date(self) -> datetime.datetime:
		return self._date

@typeguard.typechecked
class Cache:
	_cache: dict[tuple, _Container] = {}
	_cache_file: str|None = None
	_max_elements: int|None = 100
	_max_time: int|None = None

	def __init__(self, max_elements: int|None = None, max_time: int|None = None, cache_file: str|None = None):
		self._max_elements = max_elements
		self._max_time = max_time
		self._cache_file = cache_file
		if self._cache_file is not None:
			self._cache = Cache._loadCache(self._cache_file)
			print(f'items loaded: {len(self._cache)}')

	def get(self, key, experation: int|None = None) -> typing.Any|None:
		max_cache_time: int = self._max_time
		if experation is not None:
			max_cache_time = min(max_cache_time, experation)
		if key in self._cache:
			storage_container = self._cache[key]
			if storage_container.isValid(max_cache_time):
				return storage_container.data()
		return None

	def add(self, key, data: base.BaseClass) -> None:
		storage_container = _Container(data)
		self._cache[key] = storage_container
		self._checkCache()
		if self._cache_file is not None:
			self._saveCache()

	def remove(self, key) -> None:
		if key in self._cache:
			self._cache.pop(key)

	def stats(self) -> str:
		part2: str = ""
		if self._cache_file is not None:
			cache_file_stats = os.stat(self._cache_file)
			part2: str = f"\nSize of cache file on disk {utils.human_readable_filesize(cache_file_stats.st_size)}\nLast cache save: {datetime.fromtimestamp(cache_file_stats.st_mtime).isoformat(' ')}"
		part: str = f"Number of cached items: {len(self._cache)}" + part2
		return part
		
	def _checkCache(self):
		for key, storage_container in self._cache.items():
			if not storage_container.isValid(self._max_time):
				self._cache.pop(key)
		while len(self._cache.items()) > self._max_elements:
			oldest_id: tuple|None = None
			age: datetime.datetime|None = None
			for key, storage_container in self._cache.items():
				if oldest_id is None:
					oldest_id = key
					age = storage_container.date()
				elif storage_container.date() < age:
					oldest_id = key
					age = storage_container.date()
			if oldest_id is not None:
				self._cache.pop(oldest_id)

	def _saveCache(self) -> None:
		data = pickle.dumps(self._cache, pickle.DEFAULT_PROTOCOL)
		compressed = zlib.compress(data, level=9)
		with open(self._cache_file, "wb") as f:
  			f.write(compressed)

	@staticmethod
	def _loadCache(cache_file: str) -> dict[tuple, _Container]:
		try:
			print("load stored cache")
			with open(cache_file, "rb") as f:
				compressed_data: bytes = f.read()
				decompressed = zlib.decompress(compressed_data)
				obj = pickle.loads(decompressed)
				obj_type = type(obj)
				if not issubclass(obj_type, dict):
					ValueError("Can not read data from cache file")
				return obj
		except:
			return {}
		
_cache_data: dict[str, Cache] = {}

@typeguard.typechecked
def cache(max_elements: int|None = 10, max_time: int|None = None, cache_file: str|None = None):
	def cache(func):
		index_name: str = str(func.__qualname__)

		if index_name not in _cache_data:
			#logger.info (f'Init cache for function `{index_name}`.')
			print (f'Init cache for function `{index_name}`.')
			_cache_data[index_name] = Cache(max_elements, max_time, cache_file)

		async def wrapper(*args, **kwargs):
			cache_invalidate: bool = False
			cache_disabled: bool = False
			r: base.BaseClass|None = None

			if 'cache_invalidate' in kwargs:
				cache_invalidate = kwargs['cache_invalidate']
				kwargs.pop('cache_invalidate')

			if 'cache_disabled' in kwargs:
				cache_disabled = kwargs['cache_disabled']
				kwargs.pop('cache_disabled')

			kwtuple = tuple((key, kwargs[key]) for key in sorted(kwargs.keys()))
			key = (args, kwtuple)

			if cache_invalidate == True:
				_cache_data[index_name].remove(key)
			elif cache_disabled == False:
				r = _cache_data[index_name].get(key)

			if r is not None:
				#logger.debug (f'Retrieve stored data for id `{id}`.')
				return r
			else:
				#logger.debug (f'No stored data for id `{id}` availible.')
				r = await func(*args, **kwargs)
				if cache_disabled == False:
					_cache_data[index_name].add(key, r)
			return r
		return wrapper
	return cache

@typeguard.typechecked
def cache_stats(func) -> None:
	index_name: str = str(func.__qualname__)
	if index_name in _cache_data:
		print (_cache_data[index_name].stats())
	
