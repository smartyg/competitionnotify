#!/bin/python

import typing
import typeguard
import attrs
import datetime
import dateutil.relativedelta

import competitionnotify.dataclasses.base as base
import competitionnotify.utils.utils as utils

@attrs.define(frozen=True, kw_only=True, slots=False)
class TimeClass(base.BaseClass):
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

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistanceClass(base.BaseClass):
	_distances: typing.ClassVar[tuple[int, ...]] = (100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000)

	_distance: int = attrs.field(validator=attrs.validators.instance_of(int))

	@_distance.validator
	def distance_check(self, attribute: str, value: int) -> bool:
		if value not in self._distances:
			raise ValueError("value of " + str(value) + " is not a valid distance.")
		return True

	@staticmethod
	def allDistances() -> list["DistanceClass"]:
		res = []
		for i in DistanceClass._distances:
			res.append(DistanceClass(distance=i))

		return res

	def __str__(self) -> str:
		return str(str(self._distance) + " meter")

	def getPoints(self, time: TimeClass) -> float:
		return (time.getTime() * 500 / self._distance)

@typeguard.typechecked
def convert_to_distance(d: int) -> DistanceClass:
	return DistanceClass(distance=d)

@typeguard.typechecked
def convertDate(date_str: str) -> datetime.date:
	return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

@typeguard.typechecked
def convertTime(time_str: str) -> TimeClass:
	return TimeClass.from_string(time_str)

@attrs.define(frozen=True, kw_only=True, slots=False)
class BaseSkaterClass(base.BaseClass):
	_skater: int = attrs.field(validator=attrs.validators.instance_of(int))

	def getSkater(self) -> int:
		return self._skater

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultClass(base.BaseClass):
	_distance: DistanceClass = attrs.field(converter=convert_to_distance, validator=attrs.validators.instance_of(DistanceClass))
	_time: TimeClass = attrs.field(converter=convertTime, validator=attrs.validators.instance_of(TimeClass))
	_date: datetime.date = attrs.field(converter=convertDate, validator=attrs.validators.instance_of(datetime.date))
	_location: str = attrs.field(validator=attrs.validators.instance_of(str))
	_name: str = attrs.field(factory=str, validator=attrs.validators.instance_of(str))
	_link: str = attrs.field(factory=str, validator=attrs.validators.instance_of(str))

	def getPoints(self) -> float:
		return self.distance.getPoints(self._time)

	def getDistance(self) -> DistanceClass:
		return self._distance

	def getTime(self) -> TimeClass:
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
def convert_to_ResultClass_dict(data: list[dict[str, typing.Any]]) -> dict[DistanceClass, ResultClass]:
	result: dict[DistanceClass, ResultClass] = {}
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
	_season: int = attrs.field(default=-1, validator=attrs.validators.instance_of(int))
	_records: dict[DistanceClass, ResultClass] = attrs.field(converter=convert_to_ResultClass_dict, validator=attrs.validators.deep_mapping(
			key_validator=attrs.validators.instance_of(DistanceClass),
            value_validator=attrs.validators.instance_of(ResultClass),
            mapping_validator=attrs.validators.instance_of(dict)))

	def isPersonalBest(self) -> bool:
		if self._season == -1:
			return True
		return False

	def getDistanceTime(self, distance: DistanceClass) -> TimeClass|None:
		d = self._records.get(distance, None)
		if d is not None:
			return d.getTime()
		return None

	def getDistancePoints(self, distance: DistanceClass) -> float|None:
		d = self._records.get(distance, None)
		if d is not None:
			return d.getPoints()
		return None

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultsClass(BaseSkaterClass):
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))
	_distance: DistanceClass = attrs.field(converter=convert_to_distance, validator=attrs.validators.instance_of(DistanceClass))
	_results: list[ResultClass] = attrs.field(converter=convert_to_ResultClass_list, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(ResultClass),
			iterable_validator=attrs.validators.instance_of(list)))

	def hasResults(self) -> bool:
		if len(self._results) < 1:
			return False
		return True

	def getSeason(self) -> int:
		return self._season

	def getDistance(self) -> DistanceClass:
		return self._distance

	def getResults(self) -> list[ResultClass]:
		return self._results

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionClass:
	_id: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_startdate: datetime.date = attrs.field(converter=convertDate, validator=attrs.validators.instance_of(datetime.date))
	_enddate: datetime.date = attrs.field(converter=convertDate, validator=attrs.validators.instance_of(datetime.date))
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
	_gender: str = attrs.field(validator=attrs.validators.instance_of(str))
	_category: str = attrs.field(factory=str, converter=str, validator=attrs.validators.instance_of(str))

	def getId(self) -> int:
		return self._id

	def getFullName(self) -> str:
		return str(self._givenname + " " + self._familyname)

	def getCountry(self) -> str:
		return self._country

	def getGender(self) -> str:
		return self._gender

	def getCategory(self) -> str:
		return self._category
