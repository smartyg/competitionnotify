#!/usr/bin/python
import typing
import typeguard
import attrs
import datetime
import dateutil.relativedelta
import asyncio
import aiohttp
import json

import traceback

import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.distance as distance
import competitionnotify.utils.utils as utils


# https://tijden-service.schaatsen.nl/api/SearchSkater?name=Martijn%20Goedhart
# https://tijden-service.schaatsen.nl/api/SkaterTimes?id=521a5f8d-1158-4cfa-8b89-9ad196b1a7bf

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultClass(base.BaseClass):
	_season: int
	_raceDate: datetime.date = attrs.field(converter=classes.datetime_converter, validator=attrs.validators.instance_of(datetime.date))
	_venue: str = attrs.field(validator=attrs.validators.instance_of(str))
	_venueCity: str = attrs.field(validator=attrs.validators.instance_of(str))
	_venueCountry: str = attrs.field(validator=attrs.validators.instance_of(str))
	_raceTime: time.TimeClass = attrs.field(converter=time.TimeClass_converter, validator=attrs.validators.instance_of(time.TimeClass))
	_distance: distance.DistanceValueClass = attrs.field(converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_discipline: discipline.DisciplineClass
	_competitionName: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(frozen=True, kw_only=True, slots=False)
class DistanceResults(base.BaseClass):
	_distance: distance.DistanceValueClass = attrs.field(converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_races: list[ResultClass]

@attrs.define(frozen=True, kw_only=True, slots=False)
class Nameclass(base.BaseClass):
	_id: uuid.UUID
	_name: skater.PersonNameClass
	_birthDateDisplay: str
	_iocCode: str|None
	_gender: str

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultsClass(base.BaseClass):
	_skater: Nameclass
	_races: list[DistanceResults]

@attrs.define(frozen=True, kw_only=True, slots=False)
class VantageSearchResultClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(validator=attrs.validators.instance_of(uuid.UUID))
	_birthDateDisplay: int = attrs.field(converter=utils.str2int_converter, validator=attrs.validators.instance_of(int))
	_firstName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_namePreposition: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_lastName: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_fullName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_initials: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_iocCode: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_gender: str = attrs.field(validator=attrs.validators.instance_of(str))

	def match(self, firstName: str, lastName: str, prefix: str|None = None, birthYear: int) -> bool:
		return self._firstName == firstName and self._lastName == lastName and self._namePreposition == prefix and self._birthDateDisplay == birthYear
	
	getId(self) -> uuid.UUID:
		return self._id

vantageGetLicense(number: int) -> skater.SkaterClass|None:
	url = 'https://inschrijven.schaatsen.nl/api/licenses/KNSB/SpeedSkating.LongTrack/' + str(number)
	skater_license = utils.loadData(url, skater.SkaterClass)
	if skater_license is None:
		return None
	else:
		return skater_license

vantageSearchId(skater_license: skater.SkaterClass, birth_date: datetime.date) -> uuid.UUID|None:
  url = 'https://tijden-service.schaatsen.nl/api/SearchSkater?name=' + skater_license.getName()
  skater_search_results: tuple[VantageSearchResultClass, ...] = utils.loadData_tuple(url, VantageSearchResultClass)
  for s in skater_search_results:
	  if s.match(skater.getSurename(), skater.getSurename(), skater.getSurename(), birth_date.year):
		  return s.getId()
  return None



class Cache:
	@attrs.define(frozen=True, kw_only=False, slots=False)
	class Container:
		_date: datetime.datetime = attrs.field(validator=attrs.validators.instance_of(datetime.datetime))
		_data: bytes = attrs.field(convertor=serialize, validator=attrs.validators.instance_of(bytes))

		@data_validator
		def data_validator(self, data):
			cls = results.deserialize(data)
			if not isinstance(cls, results):
				raise ValueError()

		def __init__(self, data: results, date: datetime.datetime):
			self._data = data.serialize()
			self._date = date
			
		def isValid(self, experation: int) -> bool:
			return datetime.datetime.now() < (self._date + experation)
			
		def data(self) -> results:
			return results.deserialize(self._data)
			
	_cache: dict[uuid.UUID, Container] = {}
	_cache_file: str|None
	_max_elements: int|None = None
	_max_time: int|None = None

	def __init__(self, max_elements: int|None = None, max_time: int|None = None, cache_file: str|None = None):
		self._max_elements = max_elements
		self._max_time = max_time
		self._cache_file = cache_file
		if self._cache_file is not None:
			self._data = Cache._loadCache(self._cache_file, self._max_element, self._max_time)

	def get(id: uuid.UUID, experation: int = -1) -> result|None:
		if self._cache.hasKey(id):
			storage_container = self._cache[id]
			if storage_container.isValid(min(self._experation, experation)):
				return storage_container.data()
		return None

	def add(id: uuid.UUID, result: result) -> None:
		storage_container = Container(result.serialize(), datetime.now())
		self._cache[id] = storage_container
		self._checkCache()

	def _checkCache(self):
		for id, storage_container in self._cache:
			if not storage_container.isValid(self._experation)
				self._cache.remove(id)
	def _saveCache(self) -> None:
		data = pickle.dumps(self._cache, pickle.DEFAULT_PROTOCOL)
		compressed = zlib.compress(data, level=9)
		


vantage_result_cache: Cache = Cache(150, 43200)
vantageGetAllResults(id: uuid.UUID) -> results:
	r: |None = vantage_result_cache.get(id, 43200)
	if r is not None:
		return r
	else:
		r = vantageGetAllResults_internal(id)
		vantage_result_cache.add(id, r)
		return r


vantageGetPeronalBest(id: uuid.UUID, distances: list[distance.DistanceValueClass]) -> dict[distance.DistanceValueClass, time.TimeClass]:

vantageGetSeasonalBest(id: uuid.UUID, season: int, distances: list[distance.DistanceValueClass]) -> dict[distance.DistanceValueClass, time.TimeClass]:
