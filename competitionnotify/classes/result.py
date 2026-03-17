#!/bin/python

import typing
import typeguard
import attrs
import logging
import datetime

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.time as time
import competitionnotify.classes.distance as distance
import competitionnotify.classes.categories as categories

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class BaseSkaterClass[T](base.BaseClass):
	_skater: T = base.BaseClass.serializable(True) #, validator=attrs.validators.instance_of(T))

	def getSkater(self) -> T:
		return self._skater

	def getSkaterIdType(self) -> type[T]:
		return type(self._skater)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class ResultClass(base.BaseClass):
	_distance: distance.DistanceValueClass = base.BaseClass.serializable(True, converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass)) #type: ignore [misc]
	_time: time.TimeClass = base.BaseClass.serializable(True, converter=time.TimeClass_converter, validator=attrs.validators.instance_of(time.TimeClass)) #type: ignore [misc]
	_date: datetime.date = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.date)) #type: ignore [misc]
	_location: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_name: str = base.BaseClass.serializable(True, factory=str, validator=attrs.validators.instance_of(str))
	_link: str = base.BaseClass.serializable(True, factory=str, validator=attrs.validators.instance_of(str))

	def getPoints(self) -> float:
		return self._distance.getPoints(self._time)

	def getDistance(self) -> distance.DistanceValueClass:
		return self._distance

	def getDistanceValue(self) -> int:
		return self._distance.getValue()

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
def convert_to_ResultClass_dict(data: list[dict[str, typing.Any]]) -> dict[int, ResultClass]:
	result: dict[int, ResultClass] = {}
	for e in data:
		r = utils.class_factory(e, ResultClass)
		if isinstance(r, ResultClass):
			result[r.getDistanceValue()] = r
	return result

@typeguard.typechecked
def convert_to_ResultClass_list(data: list[dict[str, typing.Any]]) -> list[ResultClass]:
	result: list[ResultClass] = []
	for e in data:
		r = utils.class_factory(e, ResultClass)
		if isinstance(r, ResultClass):
			result.append(r)
	return result

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class BestTimesClass[T](BaseSkaterClass[T]):
	_records: dict[int, ResultClass] = base.BaseClass.serializable(True, converter=convert_to_ResultClass_dict, validator=attrs.validators.deep_mapping( #type: ignore [misc]
			key_validator=attrs.validators.instance_of(int),
            value_validator=attrs.validators.instance_of(ResultClass),
            mapping_validator=attrs.validators.instance_of(dict)))
	_season: int|list[int] = base.BaseClass.serializable(True, default=-1, validator=attrs.validators.or_(attrs.validators.instance_of(int), attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(int),
			iterable_validator=attrs.validators.instance_of(list))))

	def isPersonalBest(self) -> bool:
		if self._season == -1:
			return True
		return False

	def getDistance(self, d: distance.DistanceValueClass) -> ResultClass|None:
		return self._records.get(d.getValue(), None)

	def getDistanceTime(self, d: distance.DistanceValueClass) -> time.TimeClass|None:
		d_r = self._records.get(d.getValue(), None)
		if d_r is not None:
			return d_r.getTime()
		return None

	def getDistancePoints(self, d: distance.DistanceValueClass) -> float|None:
		d_r = self._records.get(d.getValue(), None)
		if d_r is not None:
			return d_r.getPoints()
		return None
#
# @attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
# class ResultsClass[T](BaseSkaterClass[T]):
# 	_season: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
# 	_distance: distance.DistanceValueClass = base.BaseClass.serializable(True, converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass)) #type: ignore [misc]
# 	_results: list[ResultClass] = base.BaseClass.serializable(True, converter=convert_to_ResultClass_list, validator=attrs.validators.deep_iterable( #type: ignore [misc]
# 			member_validator=attrs.validators.instance_of(ResultClass),
# 			iterable_validator=attrs.validators.instance_of(list)))
#
# 	def hasResults(self) -> bool:
# 		if len(self._results) < 1:
# 			return False
# 		return True
#
# 	def getSeason(self) -> int:
# 		return self._season
#
# 	def getDistance(self) -> distance.DistanceValueClass:
# 		return self._distance
#
# 	def getResults(self) -> list[ResultClass]:
# 		return self._results
#
# @attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
# class CompetitionClass(base.BaseClass):
# 	_id: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
# 	_name: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
# 	_startdate: datetime.date = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.date)) #type: ignore [misc]
# 	_enddate: datetime.date = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.date)) #type: ignore [misc]
# 	_link: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
#
# 	def getId(self) -> int:
# 		return self._id
#
# 	def getName(self) -> str:
# 		return self._name
#
# 	def getStartdate(self) -> datetime.date:
# 		return self._startdate
#
# 	def getEnddate(self) -> datetime.date:
# 		return self._enddate
#
# 	def getLink(self) -> str:
# 		return self._link
#
# @typeguard.typechecked
# def convert_to_CompetitionClass(data: list[dict[str, typing.Any]]) -> list[CompetitionClass]:
# 	result: list[CompetitionClass] = []
# 	for e in data:
# 		r = utils.class_factory(e, CompetitionClass)
# 		if isinstance(r, CompetitionClass):
# 			result.append(r)
# 	return result
#
# @attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
# class CompetitionsClass[T](BaseSkaterClass[T]):
# 	_season: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
# 	_competitions: list[CompetitionClass] = base.BaseClass.serializable(True, converter=convert_to_CompetitionClass, validator=attrs.validators.deep_iterable( #type: ignore [misc]
# 			member_validator=attrs.validators.instance_of(CompetitionClass),
# 			iterable_validator=attrs.validators.instance_of(list)))
#
# 	def hasCompetitions(self) -> bool:
# 		if len(self._competitions) > 0:
# 			return True
# 		return False
#
# 	def getCompetitions(self) -> list[CompetitionClass]:
# 		return self._competitions

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class NameClass[T](BaseSkaterClass[T]):
	_familyname: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_givenname: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_country: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_category: categories.CategoryClass = base.BaseClass.serializable(True, converter=categories.CategoryClass_converter, validator=attrs.validators.instance_of(categories.CategoryClass)) #type: ignore [misc]

	def getId(self) -> T:
		return self.getSkater()

	def getFullName(self) -> str:
		return str(self._givenname + " " + self._familyname)

	def getCountry(self) -> str:
		return self._country

	def getGender(self) -> str:
		return self._category.getGender()

	def getCategory(self) -> str:
		return str(self._category)
