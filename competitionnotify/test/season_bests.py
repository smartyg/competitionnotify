#!/usr/bin/python

import typeguard
import asyncio
import attrs
import logging
import datetime
import json
import uuid
import typing
import csv
import aiohttp

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.distance as distance
import competitionnotify.classes.time as time
import competitionnotify.classes.competition as competition
import competitionnotify.classes.categories as categories
import competitionnotify.classes.result as result

logger = logging.getLogger(__name__)

U = typing.TypeVar('U', bound=attrs.AttrsInstance) # Declare type variable "U"

def str_to_int_converter(data: str|int|None) -> int|None:
	if isinstance(data, int):
		return data
	if isinstance(data, str):
		try:
			return int(data)
		except:
			return None
	return None

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class SkaterClass(base.BaseClass):
	_id: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_firstName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_lastName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_fullName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_namePreposition: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_birthDateDisplay: int|None = base.BaseClass.serializable(True, default=None, converter=str_to_int_converter, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_initials: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_iocCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_gender: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

@typeguard.typechecked
def SkaterClass_converter_except(data: SkaterClass|dict[str, typing.Any]) -> SkaterClass:
	return utils.class_converter_except(data, SkaterClass)

@typeguard.typechecked
def SkaterClass_converter_none(data: SkaterClass|dict[str, typing.Any]|None) -> SkaterClass|None:
	if isinstance(data, SkaterClass):
		return data
	if isinstance(data, dict):
		try:
			return utils.class_converter_none(data, SkaterClass)
		except:
			return None
	return None

@typeguard.typechecked
def SkaterClassTuple_converter(data: tuple[SkaterClass,...]|list[dict[str, typing.Any]]) -> tuple[SkaterClass,...]:
	return utils.ClassTuple_converter(data, SkaterClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class DistanceResultClass(base.BaseClass):
	_season: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_raceDate: datetime.datetime = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_skaterId: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_raceTime: time.TimeClass = base.BaseClass.serializable(True, converter=time.TimeClass_converter, validator=attrs.validators.instance_of(time.TimeClass)) # type: ignore [misc]
	_distance: distance.DistanceValueClass = base.BaseClass.serializable(True, converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_venue: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_venueCity: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_venueCountry: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_discipline: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str))) #TODO: convert to discipline class
	_competitionName: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def getTime(self) -> time.TimeClass:
		return self._raceTime

	def getDistance(self) -> distance.DistanceValueClass:
		return self._distance

	def getResultClass(self) -> result.ResultClass:
		return result.ResultClass(
			distance=self._distance,
			time=self._raceTime,
			date=self._raceDate.date(),
			location=self._venue,
			name=self._competitionName,
			link=""
		)


@typeguard.typechecked
def DistanceResultClass_converter_except(data: DistanceResultClass|dict[str, typing.Any]) -> DistanceResultClass:
	return utils.class_converter_except(data, DistanceResultClass)

@typeguard.typechecked
def DistanceResultClass_converter_none(data: DistanceResultClass|dict[str, typing.Any]|None) -> DistanceResultClass|None:
	if isinstance(data, DistanceResultClass):
		return data
	if isinstance(data, dict):
		try:
			return utils.class_converter_none(data, DistanceResultClass)
		except:
			return None
	return None

@typeguard.typechecked
def DistanceResultClassTuple_converter(data: tuple[DistanceResultClass,...]|list[dict[str, typing.Any]]) -> tuple[DistanceResultClass,...]:
	return utils.ClassTuple_converter(data, DistanceResultClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class RacesClass(base.BaseClass):
	_distance: distance.DistanceValueClass = base.BaseClass.serializable(True, converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_races: tuple[DistanceResultClass, ...] = base.BaseClass.serializable(True, converter=DistanceResultClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(DistanceResultClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	def getSeasonBest(self, season: str) -> result.ResultClass|None:
		best: result.ResultClass|None = None
		for race_result in self._races:
			if race_result._season == season:
				if best is None:
					best = race_result.getResultClass()
				elif race_result.getTime() < best.getTime():
					best = race_result.getResultClass()
		return best

	def getPersonalBest(self) -> result.ResultClass|None:
		best: result.ResultClass|None = None
		for race_result in self._races:
			if best is None:
				best = race_result.getResultClass()
			elif race_result.getTime() < best.getTime():
				best = race_result.getResultClass()
		return best

@typeguard.typechecked
def RacesClass_converter_except(data: RacesClass|dict[str, typing.Any]) -> RacesClass:
	return utils.class_converter_except(data, RacesClass)

@typeguard.typechecked
def RacesClass_converter_none(data: RacesClass|dict[str, typing.Any]|None) -> RacesClass|None:
	if isinstance(data, RacesClass):
		return data
	if isinstance(data, dict):
		try:
			return utils.class_converter_none(data, RacesClass)
		except:
			return None
	return None

@typeguard.typechecked
def RacesClassTuple_converter(data: tuple[RacesClass,...]|list[dict[str, typing.Any]]) -> tuple[RacesClass,...]:
	return utils.ClassTuple_converter(data, RacesClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class ResultsClass(base.BaseClass):
	_skater: SkaterClass = base.BaseClass.serializable(True, converter=SkaterClass_converter_except, validator=attrs.validators.instance_of(SkaterClass))
	_races: tuple[RacesClass, ...] = base.BaseClass.serializable(True, converter=RacesClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(RacesClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	@staticmethod
	def _getSeasonString(season: int) -> str:
		return str(season) + "/" + str(season + 1)

	def getFullName(self) -> str:
		return self._skater._fullName

	def countRaces(self, season: int) -> int:
		season_str = ResultsClass._getSeasonString(season)
		number_of_races: int = 0

		for r1 in self._races:
			for r2 in r1._races:
				if r2._season == season_str:
					number_of_races += 1
		return number_of_races

	def countDays(self, season: int) -> int:
		season_str = ResultsClass._getSeasonString(season)

		days: set[datetime.date] = set()
		for r1 in self._races:
			for r2 in r1._races:
				if r2._season == season_str:
					days.add(r2._raceDate.date())
		return len(days)

	def getSeasonBest(self, distance_value: distance.DistanceValueClass, season: int) -> result.ResultClass|None:
		season_str = ResultsClass._getSeasonString(season)
		for r in self._races:
			if r._distance.equal(distance_value):
				return r.getSeasonBest(season_str)

	def getPersonalBest(self, distance_value: distance.DistanceValueClass) -> result.ResultClass|None:
		for r in self._races:
			if r._distance.equal(distance_value):
				return r.getPersonalBest()

@typeguard.typechecked
async def apiDownload(url: str, c: type[U]) -> U:
	async with aiohttp.ClientSession() as session:
		logger.debug (f'download file: {url} ...')
		async with session.get(url) as response:
			#logger.debug ("Download competition data file for competition ...")
			data = json.loads(await response.text())
			logger.debug (f'Download completed.')
			ret = None
			if not isinstance(data, dict):
				name = base.getFirstFieldName(c)
				if name is not None:
					ret = utils.class_factory({name: data}, c)
			else:
				ret = utils.class_factory(data, c)
			if ret is None:
				raise ValueError(f'Failed to create and instance of type `{c.__name__!s}` with data: {data!s}.')
			return ret


async def getSkaterRecords(id: str, season: int) -> list[str|int]:
	url = 'https://tijden-service.schaatsen.nl/api/SkaterTimes?id=' + str(id)

	results = await apiDownload(url, ResultsClass)

	result_list: list[str|int] = []

	result_list.append(results.getFullName())
	result_list.append(results.countRaces(season))
	result_list.append(results.countDays(season))

	distances = distance.DistanceValueClass.allDistances()
	season_best_time: dict[int, result.ResultClass|None] = {}
	personal_best_time: dict[int, result.ResultClass|None] = {}
	is_personal_best_time: dict[int, bool] = {}

	for distance_value in distances:
		season_best = results.getSeasonBest(distance_value, season)
		personal_best = results.getPersonalBest(distance_value)
		season_best_time[distance_value] = "" if season_best is None else str(season_best.getTime())
		personal_best_time[distance_value] = "" if personal_best is None else str(personal_best.getTime())
		is_personal_best_time[distance_value] = 1 if season_best is not None and season_best.getTime() == personal_best.getTime() else 0

	result_list.extend(season_best_time.values())
	result_list.extend(personal_best_time.values())
	result_list.extend(is_personal_best_time.values())

	return result_list

async def runner() -> None:
	skaters: list[str] = [
		"521a5f8d-1158-4cfa-8b89-9ad196b1a7bf",
		"be52e3db-c49f-456c-aa92-c22dda3e0e98"
	]

	season = 2025

	result_list: list[list[str|int]] = [await getSkaterRecords(s, season) for s in skaters]

	#print(result_list)

	filename = "season_results.csv"
	with open(filename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile,delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)        # Create writer object
		csvwriter.writerows(result_list)

if __name__ == '__main__':
	logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG, filemode='w')
	asyncio.run(runner())