#!/usr/bin/python

from typing import Any, TypeVar, Literal, TYPE_CHECKING
import datetime
import aiohttp
import asyncio
import traceback
import attrs

if TYPE_CHECKING:
	from _typeshed import DataclassInstance

@attrs.define(frozen=True, kw_only=True, slots=False)
class TimeClass:
	_minutes: int = attrs.field(validator=attrs.validators.instance_of(int))
	_seconds: int = attrs.field(validator=attrs.validators.instance_of(int))
	_miliseconds: int = attrs.field(validator=attrs.validators.instance_of(int))

	@_minutes.validator
	def minutes_check(self, attribute: str, value: int) -> bool:
		if value < 0 or value >= 60:
			raise ValueError("value of " + str(value) + " is not a valid number of minutes.")
		return True

	@_seconds.validator
	def seconds_check(self, attribute: str, value: int) -> bool:
		if value < 0 or value >= 60:
			raise ValueError("value of " + str(value) + " is not a valid number of seconds.")
		return True

	@_miliseconds.validator
	def miliseconds_check(self, attribute: str, value: int) -> bool:
		if value < 0 or value >= 1000:
			raise ValueError("value of " + str(value) + " is not a valid number of miliseconds.")
		return True

	def __str__(self) -> str:
		ms = self._miliseconds
		s = self._seconds
		m = self._minutes
		if self._minutes == 0:
			return str(f"{s}.{ms:03}")
		else:
			return str(f"{m}:{s:02}.{ms:03}")

	def getTime(self) -> float:
		return (self._minutes * 60) + self._seconds + (self._miliseconds / 1000)

	@classmethod
	def from_string(cls, time: str) -> "TimeClass":
		s1 = time.split(",")
		if len(s1) != 2:
			raise ValueError("string (\"" + time + "\") is not a valid time representation.")

		if len(s1[1]) == 1:
			miliseconds = int(s1[1]) * 100
		elif len(s1[1]) == 2:
			miliseconds = int(s1[1]) * 10
		elif len(s1[1]) == 3:
			miliseconds = int(s1[1])
		else:
			raise ValueError("string (\"" + time + "\") is not a valid time representation.")

		s2 = s1[0].split(".")
		if len(s2) == 1:
			minutes = 0
			seconds = int(s2[0])
		elif len(s2) == 2:
			minutes = int(s2[0])
			seconds = int(s2[1])
		else:
			raise ValueError("string (\"" + time + "\") is not a valid time representation.")

		return cls(minutes=minutes, seconds=seconds, miliseconds=miliseconds)

@attrs.define(frozen=True, slots=False)
class DistanceClass:
	value: int = attrs.field(validator=attrs.validators.instance_of(int), alias="distance")
	distances = [100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000]

	@value.validator
	def distance_check(self, attribute: str, value: int) -> bool:
		if value not in self.distances:
			raise ValueError("value of " + str(value) + " is not a valid distance.")
		return True

	@staticmethod
	def allDistances() -> list["DistanceClass"]:
		res = []
		for i in DistanceClass.distances:
			res.append(DistanceClass(i))

		return res

	def __str__(self) -> str:
		return str(str(self.value) + " meter")

	def getPoints(self, time: TimeClass) -> float:
		return (time.getTime() * 500 / self.value)

def sanitize(fields: dict[str, attrs.Attribute], d: dict[str, Any]) -> dict[str, Any]|None:
	e={}
	for f in fields.values():
		if f.name in d:
			e[f.name] = d[f.name]
		elif f.default == attrs.NOTHING:
			print("Error, no value for " + str(f.name))
			return None
	return e

U = TypeVar('U', bound=type[attrs.AttrsInstance]) # Declare type variable "U"

def class_factory(d: dict[str, Any], c: U) -> U|None:
	e = sanitize(attrs.fields_dict(c), d)
	if e is None:
		return None
	return c(**e)

def convert_to_distance(d: int) -> DistanceClass:
	return DistanceClass(d)

def convertDate(date_str: str) -> datetime.date:
	return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

def convertTime(time_str: str) -> TimeClass:
	return TimeClass.from_string(time_str)

@attrs.define(frozen=True, kw_only=True, slots=False)
class BaseSkaterClass:
	skater: int = attrs.field(validator=attrs.validators.instance_of(int))

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultClass:
	distance: DistanceClass = attrs.field(converter=convert_to_distance, validator=attrs.validators.instance_of(DistanceClass))
	time: TimeClass = attrs.field(converter=convertTime, validator=attrs.validators.instance_of(TimeClass))
	date: datetime.date = attrs.field(converter=convertDate, validator=attrs.validators.instance_of(datetime.date))
	location: str = attrs.field(validator=attrs.validators.instance_of(str))
	name: str = attrs.field(factory=str, validator=attrs.validators.instance_of(str))
	link: str = attrs.field(factory=str, validator=attrs.validators.instance_of(str))

	def getPoints(self) -> float:
		return self.distance.getPoints(self.time)

def convert_to_ResultClass_dict(data: list[dict[str, Any]]) -> dict[DistanceClass, ResultClass]:
	result: dict[DistanceClass, ResultClass] = {}
	for e in data:
		r = class_factory(e, ResultClass)
		if isinstance(r, ResultClass):
			result[r.distance] = r
	return result

def convert_to_ResultClass_list(data: list[dict[str, Any]]) -> list[ResultClass]:
	result: list[ResultClass] = []
	for e in data:
		r = class_factory(e, ResultClass)
		if isinstance(r, ResultClass):
			result.append(r)
	return result

@attrs.define(frozen=True, kw_only=True, slots=False)
class BestTimesClass(BaseSkaterClass):
	#skater: int = attrs.field(validator=attrs.validators.instance_of(int))
	season: int = attrs.field(default=-1, validator=attrs.validators.instance_of(int))
	records: dict[DistanceClass, ResultClass] = attrs.field(converter=convert_to_ResultClass_dict, validator=attrs.validators.deep_mapping(
			key_validator=attrs.validators.instance_of(DistanceClass),
            value_validator=attrs.validators.instance_of(ResultClass),
            mapping_validator=attrs.validators.instance_of(dict)))

	def isPersonalBest(self) -> bool:
		if self.season == -1:
			return True
		return False

	def getDistanceTime(self, distance: DistanceClass) -> TimeClass|None:
		d = self.records.get(distance, None)
		if d is not None:
			return d.time
		return None

	def getDistancePoints(self, distance: DistanceClass) -> float|None:
		d = self.records.get(distance, None)
		if d is not None:
			return d.getPoints()
		return None

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultsClass(BaseSkaterClass):
	#skater: int = attrs.field(validator=attrs.validators.instance_of(int))
	season: int = attrs.field(validator=attrs.validators.instance_of(int))
	#distance: Distances = attrs.field(validator=attrs.validators.instance_of(int))
	distance: DistanceClass = attrs.field(converter=convert_to_distance, validator=attrs.validators.instance_of(DistanceClass))
	results: list[ResultClass] = attrs.field(converter=convert_to_ResultClass_list, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(ResultClass),
			iterable_validator=attrs.validators.instance_of(list)))

	def hasResults(self) -> bool:
		if len(self.results) < 1:
			return False
		return True

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionClass:
	id: int = attrs.field(validator=attrs.validators.instance_of(int))
	name: str = attrs.field(validator=attrs.validators.instance_of(str))
	startdate: datetime.date = attrs.field(converter=convertDate, validator=attrs.validators.instance_of(datetime.date))
	enddate: datetime.date = attrs.field(converter=convertDate, validator=attrs.validators.instance_of(datetime.date))
	link: str = attrs.field(validator=attrs.validators.instance_of(str))

def convert_to_CompetitionClass(data: list[dict[str, Any]]) -> list[CompetitionClass]:
	result: list[CompetitionClass] = []
	for e in data:
		r = class_factory(e, CompetitionClass)
		if isinstance(r, CompetitionClass):
			result.append(r)
	return result

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionsClass(BaseSkaterClass):
	#skater: int = attrs.field(validator=attrs.validators.instance_of(int))
	season: int = attrs.field(validator=attrs.validators.instance_of(int))
	competitions: list[CompetitionClass] = attrs.field(converter=convert_to_CompetitionClass, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(CompetitionClass),
			iterable_validator=attrs.validators.instance_of(list)))

	def hasCompetitions(self) -> bool:
		if len(self.competitions) > 0:
			return True
		return False

@attrs.define(frozen=True, kw_only=True, slots=False)
class NameClass:
	id: int = attrs.field(validator=attrs.validators.instance_of(int))
	familyname: str = attrs.field(validator=attrs.validators.instance_of(str))
	givenname: str = attrs.field(validator=attrs.validators.instance_of(str))
	country: str = attrs.field(validator=attrs.validators.instance_of(str))
	gender: str = attrs.field(validator=attrs.validators.instance_of(str))
	category: str = attrs.field(factory=str, converter=str, validator=attrs.validators.instance_of(str))

	def getFullName(self) -> str:
		return str(self.givenname + " " + self.familyname)

class SpeedSkatingResults:
	@attrs.define(frozen=True, kw_only=True, slots=False)
	class apiClass:
		base_url: str = attrs.field(validator=attrs.validators.instance_of(str))
		parameters: list[str] = attrs.field(validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(str),
            iterable_validator=attrs.validators.instance_of(list)))

	_api_base: str = "https://speedskatingresults.com/api/"
	_api_calls: dict[str, apiClass] = {
		"skater_id": apiClass(base_url="/skater_lookup.php", parameters=["familyname", "givenname", "country", "gender"]),
		"competition_list": apiClass(base_url="/skater_competitions.php", parameters=["skater", "season"]),
		"personal_records": apiClass(base_url="/personal_records.php", parameters=["skater", "distance"]),
		"season_bests": apiClass(base_url="/season_bests.php", parameters=["skater", "distance", "start"]),
		"distance_results": apiClass(base_url="/skater_results.php", parameters=["skater", "distance", "season"]),
		}

	@staticmethod
	def construct_url(key: str, parameters: dict[str, Any], type: str = "json") -> str:
		api = SpeedSkatingResults._api_calls.get(key, None)
		if api is not None:
			pp: list[str] = []
			for p in api.parameters:
				if p in parameters and parameters[p] is not None:
					pp.append(p + "=" + str(parameters[p]))
			url: str = SpeedSkatingResults._api_base + type + api.base_url + "?" + "&".join(pp)
			return url
		return str()

	@staticmethod
	async def _apiSkaterId(session: aiohttp.ClientSession, name: dict[str, str]) -> type[NameClass]:
		url = SpeedSkatingResults.construct_url("skater_id", name)
		async with session.get(url) as response:
			result = await response.json()
			skaters = result.get('skaters', None)
			if len(skaters) == 1:
				res = class_factory(skaters[0], NameClass)
				if res is not None:
					return res
			else:
				raise ValueError('Found ' + str(len(skaters)) + ' skaters that meet the search criteria')
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiPersonalRecord(session: aiohttp.ClientSession, skater: int|type[NameClass], distance: int|None) -> type[BestTimesClass]:
		if isinstance(skater, NameClass):
			skater_id = skater.id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("personal_records", {'skater': skater_id, 'distance': distance})

		async with session.get(url) as response:
			result = await response.json()
			res = class_factory(result, BestTimesClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiSeasonBests(session: aiohttp.ClientSession, skater: int|type[NameClass], distance: int|None = None, start: int|None = None) -> type[BestTimesClass]:
		if isinstance(skater, NameClass):
			skater_id = skater.id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("season_bests", {'skater': skater_id, 'distance': distance, 'start': start})

		async with session.get(url) as response:
			result = await response.json()
			seasons = result.get('seasons', None)
			if seasons is not None and len(seasons) == 1:
				result['season'] = seasons[0].get('start', None)
				result['records'] = seasons[0].get('records', None)

			res = class_factory(result, BestTimesClass)
			if res is not None:
				return res
		raise ValueError('No season best found for this skater (id=' + str(skater_id) + ')')

	@staticmethod
	async def _apiCompetitionList(session: aiohttp.ClientSession, skater: int|type[NameClass], start: int|None = None) -> type[CompetitionsClass]:
		if isinstance(skater, NameClass):
			skater_id = skater.id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("competition_list", {'skater': skater_id, 'season': start})

		async with session.get(url) as response:
			result = await response.json()
			res = class_factory(result, CompetitionsClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')


	@staticmethod
	async def _apiDistanceResult(session: aiohttp.ClientSession, skater: int|type[NameClass], distance: int, season: int|None = None) -> type[ResultsClass]:
		if isinstance(skater, NameClass):
			skater_id = skater.id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("distance_results", {'skater': skater_id, 'distance': distance, 'season': season})

		async with session.get(url) as response:
			result = await response.json()

			if "results" in result:
				for r in result["results"]:
					r['distance'] = result['distance']
			res = class_factory(result, ResultsClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def getId(names: list[dict[str, str]]|dict[str, str]) -> list[type[NameClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(names, list):
					tasks = [SpeedSkatingResults._apiSkaterId(session, skater_name) for skater_name in names]
				else:
					tasks = [SpeedSkatingResults._apiSkaterId(session, names)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getPersonalRecord(skaters: list[int]|list[type[NameClass]]|int|type[NameClass], distance: DistanceClass|int|None = None) -> list[type[BestTimesClass]]:
		distance_value: int|None
		if isinstance(distance, int):
			distance_value = DistanceClass(distance).value
		elif isinstance(distance, DistanceClass):
			distance_value = distance.value
		else:
			distance_value = distance

		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiPersonalRecord(session, skater, distance_value) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiPersonalRecord(session, skaters, distance_value)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getSeasonBest(skaters: list[int]|list[type[NameClass]]|int|type[NameClass], distance: DistanceClass|int|None = None, season: int|None = None) -> list[type[BestTimesClass]]:
		distance_value: int|None
		if isinstance(distance, int):
			distance_value = DistanceClass(distance).value
		elif isinstance(distance, DistanceClass):
			distance_value = distance.value
		else:
			distance_value = distance

		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiSeasonBests(session, skater, distance_value, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiSeasonBests(session, skaters, distance_value, season)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getCompetitionList(skaters: list[int]|list[type[NameClass]]|int|type[NameClass], season: int|None = None) -> list[type[CompetitionsClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skater, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skaters, season)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getDistanceResult(skaters: list[int]|list[type[NameClass]]|int|type[NameClass], distance: DistanceClass|int, season: int|None = None) -> list[type[ResultsClass]]:
		distance_value: int
		if isinstance(distance, int):
			distance_value = DistanceClass(distance).value
		elif isinstance(distance, DistanceClass):
			distance_value = distance.value
		else:
			distance_value = distance

		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiDistanceResult(session, skater, distance_value, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiDistanceResult(session, skaters, distance_value, season)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]