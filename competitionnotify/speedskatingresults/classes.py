#!/bin/python

import typing
import typeguard
import attrs
import datetime

import competitionnotify.classes.base as base
import competitionnotify.classes.time as time
import competitionnotify.classes.distance as distance
import competitionnotify.classes.categories as categories
import competitionnotify.classes.classes as classes
import competitionnotify.utils.utils as utils

@attrs.define(frozen=True, kw_only=True, slots=False)
class BaseSkaterClass(base.BaseClass):
	_skater: int = attrs.field(validator=attrs.validators.instance_of(int))

	def getSkater(self) -> int:
		return self._skater

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultClass(base.BaseClass):
	_distance: distance.DistanceValueClass = attrs.field(converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_time: time.TimeClass = attrs.field(converter=time.TimeClass_converter, validator=attrs.validators.instance_of(time.TimeClass))
	_date: datetime.date = attrs.field(converter=classes.datetime_converter, validator=attrs.validators.instance_of(datetime.date))
	_location: str = attrs.field(validator=attrs.validators.instance_of(str))
	_name: str = attrs.field(factory=str, validator=attrs.validators.instance_of(str))
	_link: str = attrs.field(factory=str, validator=attrs.validators.instance_of(str))

	def getPoints(self) -> float:
		return self._distance.getPoints(self._time)

	def getDistance(self) -> distance.DistanceValueClass:
		return self._distance

	def getTime(self) -> time.TimeClass:
		return self._time

	def getDate(self) -> datetime.date:
		return self._date

	def getLocation(self) -> str:
		return self._location

	def getName(self) -> str:
		return self._name

	def getLink(self) -> str:
		return self._link

@typeguard.typechecked
def convert_to_ResultClass_dict(data: list[dict[str, typing.Any]]) -> dict[distance.DistanceValueClass, ResultClass]:
	result: dict[distance.DistanceValueClass, ResultClass] = {}
	for e in data:
		r = utils.class_factory(e, ResultClass)
		if isinstance(r, ResultClass):
			result[r.getDistance()] = r
	return result

@typeguard.typechecked
def convert_to_ResultClass_list(data: list[dict[str, typing.Any]]) -> list[ResultClass]:
	result: list[ResultClass] = []
	for e in data:
		r = utils.class_factory(e, ResultClass)
		if isinstance(r, ResultClass):
			result.append(r)
	return result

@attrs.define(frozen=True, kw_only=True, slots=False)
class BestTimesClass(BaseSkaterClass):
	_season: int|list[int] = attrs.field(default=-1, validator=attrs.validators.or_(attrs.validators.instance_of(int), attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(int),
			iterable_validator=attrs.validators.instance_of(list))))
	_records: dict[distance.DistanceValueClass, ResultClass] = attrs.field(converter=convert_to_ResultClass_dict, validator=attrs.validators.deep_mapping(
			key_validator=attrs.validators.instance_of(distance.DistanceValueClass),
            value_validator=attrs.validators.instance_of(ResultClass),
            mapping_validator=attrs.validators.instance_of(dict)))

	def isPersonalBest(self) -> bool:
		if self._season == -1:
			return True
		return False

	def getDistanceTime(self, distance: distance.DistanceValueClass) -> time.TimeClass|None:
		d = self._records.get(distance, None)
		if d is not None:
			return d.getTime()
		return None

	def getDistancePoints(self, distance: distance.DistanceValueClass) -> float|None:
		d = self._records.get(distance, None)
		if d is not None:
			return d.getPoints()
		return None

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultsClass(BaseSkaterClass):
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))
	_distance: distance.DistanceValueClass = attrs.field(converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_results: list[ResultClass] = attrs.field(converter=convert_to_ResultClass_list, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(ResultClass),
			iterable_validator=attrs.validators.instance_of(list)))

	def hasResults(self) -> bool:
		if len(self._results) < 1:
			return False
		return True

	def getSeason(self) -> int:
		return self._season

	def getDistance(self) -> distance.DistanceValueClass:
		return self._distance

	def getResults(self) -> list[ResultClass]:
		return self._results

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionClass:
	_id: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_startdate: datetime.date = attrs.field(converter=classes.datetime_converter, validator=attrs.validators.instance_of(datetime.date))
	_enddate: datetime.date = attrs.field(converter=classes.datetime_converter, validator=attrs.validators.instance_of(datetime.date))
	_link: str = attrs.field(validator=attrs.validators.instance_of(str))

	def getId(self) -> int:
		return self._id

	def getName(self) -> str:
		return self._name

	def getStartdate(self) -> datetime.date:
		return self._startdate

	def getEnddate(self) -> datetime.date:
		return self._enddate

	def getLink(self) -> str:
		return self._link

@typeguard.typechecked
def convert_to_CompetitionClass(data: list[dict[str, typing.Any]]) -> list[CompetitionClass]:
	result: list[CompetitionClass] = []
	for e in data:
		r = utils.class_factory(e, CompetitionClass)
		if isinstance(r, CompetitionClass):
			result.append(r)
	return result

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionsClass(BaseSkaterClass):
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitions: list[CompetitionClass] = attrs.field(converter=convert_to_CompetitionClass, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(CompetitionClass),
			iterable_validator=attrs.validators.instance_of(list)))

	def hasCompetitions(self) -> bool:
		if len(self._competitions) > 0:
			return True
		return False

	def getCompetitions(self) -> list[CompetitionClass]:
		return self._competitions

@attrs.define(frozen=True, kw_only=True, slots=False)
class NameClass:
	_id: int = attrs.field(validator=attrs.validators.instance_of(int))
	_familyname: str = attrs.field(validator=attrs.validators.instance_of(str))
	_givenname: str = attrs.field(validator=attrs.validators.instance_of(str))
	_country: str = attrs.field(validator=attrs.validators.instance_of(str))
	_category: categories.CategoryClass = attrs.field(converter=categories.CategoryClass_converter, validator=attrs.validators.instance_of(categories.CategoryClass))

	def getId(self) -> int:
		return self._id

	def getFullName(self) -> str:
		return str(self._givenname + " " + self._familyname)

	def getCountry(self) -> str:
		return self._country

	def getGender(self) -> str:
		return self._category.getGender()

	def getCategory(self) -> str:
		return str(self._category)
