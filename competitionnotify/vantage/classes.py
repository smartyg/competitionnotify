#!/usr/bin/python

import typing
import typeguard
import logging
import attrs
import datetime
import uuid

import competitionnotify.classes.base as base
import competitionnotify.classes.distance as distance
import competitionnotify.classes.time as time
import competitionnotify.classes.result as result
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class VantageSkaterClass(base.BaseClass):
	_id: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_firstName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_lastName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_fullName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_namePreposition: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_birthDateDisplay: int|None = base.BaseClass.serializable(True, default=None, converter=utils.str2int_converter, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_initials: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_iocCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_gender: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

@typeguard.typechecked
def VantageSkaterClass_converter_except(data: VantageSkaterClass|dict[str, typing.Any]) -> VantageSkaterClass:
	return utils.class_converter_except(data, VantageSkaterClass)

@typeguard.typechecked
def VantageSkaterClass_converter_none(data: VantageSkaterClass|dict[str, typing.Any]|None) -> VantageSkaterClass|None:
	if isinstance(data, VantageSkaterClass):
		return data
	if isinstance(data, dict):
		try:
			return utils.class_converter_none(data, VantageSkaterClass)
		except:
			return None
	return None

@typeguard.typechecked
def VantageSkaterClassTuple_converter(data: tuple[VantageSkaterClass,...]|list[dict[str, typing.Any]]) -> tuple[VantageSkaterClass,...]:
	return utils.ClassTuple_converter(data, VantageSkaterClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class VantageDistanceResultClass(base.BaseClass):
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
def VantageDistanceResultClass_converter_except(data: VantageDistanceResultClass|dict[str, typing.Any]) -> VantageDistanceResultClass:
	return utils.class_converter_except(data, VantageDistanceResultClass)

@typeguard.typechecked
def VantageDistanceResultClass_converter_none(data: VantageDistanceResultClass|dict[str, typing.Any]|None) -> VantageDistanceResultClass|None:
	if isinstance(data, VantageDistanceResultClass):
		return data
	if isinstance(data, dict):
		try:
			return utils.class_converter_none(data, VantageDistanceResultClass)
		except:
			return None
	return None

@typeguard.typechecked
def VantageDistanceResultClassTuple_converter(data: tuple[VantageDistanceResultClass,...]|list[dict[str, typing.Any]]) -> tuple[VantageDistanceResultClass,...]:
	return utils.ClassTuple_converter(data, VantageDistanceResultClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class VantageRacesClass(base.BaseClass):
	_distance: distance.DistanceValueClass = base.BaseClass.serializable(True, converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_races: tuple[VantageDistanceResultClass, ...] = base.BaseClass.serializable(True, converter=VantageDistanceResultClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(VantageDistanceResultClass),
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
def VantageRacesClass_converter_except(data: VantageRacesClass|dict[str, typing.Any]) -> VantageRacesClass:
	return utils.class_converter_except(data, VantageRacesClass)

@typeguard.typechecked
def VantageRacesClass_converter_none(data: VantageRacesClass|dict[str, typing.Any]|None) -> VantageRacesClass|None:
	if isinstance(data, VantageRacesClass):
		return data
	if isinstance(data, dict):
		try:
			return utils.class_converter_none(data, VantageRacesClass)
		except:
			return None
	return None

@typeguard.typechecked
def VantageRacesClassTuple_converter(data: tuple[VantageRacesClass,...]|list[dict[str, typing.Any]]) -> tuple[VantageRacesClass,...]:
	return utils.ClassTuple_converter(data, VantageRacesClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class VantageResultsClass(base.BaseClass):
	_skater: VantageSkaterClass = base.BaseClass.serializable(True, converter=VantageSkaterClass_converter_except, validator=attrs.validators.instance_of(VantageSkaterClass))
	_races: tuple[VantageRacesClass, ...] = base.BaseClass.serializable(True, converter=VantageRacesClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(VantageRacesClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	@staticmethod
	def _getSeasonString(season: int) -> str:
		return str(season) + "/" + str(season + 1)

	def getFullName(self) -> str:
		return self._skater._fullName

	def countRaces(self, season: int) -> int:
		season_str = VantageResultsClass._getSeasonString(season)
		number_of_races: int = 0

		for r1 in self._races:
			for r2 in r1._races:
				if r2._season == season_str:
					number_of_races += 1
		return number_of_races

	def countDays(self, season: int) -> int:
		season_str = VantageResultsClass._getSeasonString(season)

		days: set[datetime.date] = set()
		for r1 in self._races:
			for r2 in r1._races:
				if r2._season == season_str:
					days.add(r2._raceDate.date())
		return len(days)

	def getSeasonBest(self, distance_value: distance.DistanceValueClass, season: int) -> result.ResultClass|None:
		season_str = VantageResultsClass._getSeasonString(season)
		for r in self._races:
			if r._distance.equal(distance_value):
				return r.getSeasonBest(season_str)

	def getPersonalBest(self, distance_value: distance.DistanceValueClass) -> result.ResultClass|None:
		for r in self._races:
			if r._distance.equal(distance_value):
				return r.getPersonalBest()


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class VantageSearchResultClass(base.BaseClass):
	_id: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_birthDateDisplay: int = base.BaseClass.serializable(True, converter=utils.str2int_converter, validator=attrs.validators.instance_of(int))
	_gender: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_firstName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_lastName: str = base.BaseClass.serializable(True, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_fullName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_namePreposition: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_initials: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_isoCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def match(self, firstName: str, lastName: str, prefix: str|None, birthYear: int) -> bool:
		if prefix == '':
			prefix = None
		return self._firstName == firstName and self._lastName == lastName and self._namePreposition == prefix and self._birthDateDisplay == birthYear
	
	def getId(self) -> uuid.UUID:
		return self._id

	def getName(self) -> str:
		return self._fullName

	def getBirthYear(self) -> int:
		return self._birthDateDisplay
