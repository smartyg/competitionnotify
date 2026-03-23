#!/bin/python

import typing
import typeguard
import attrs
import logging
import uuid
import datetime

import competitionnotify.classes.base as base
import competitionnotify.classes.time as time
import competitionnotify.classes.discipline as discipline
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=False, slots=False, hash=True, str=False, eq=False, order=False)
class DistanceValueClass(base.BaseClass):
	_distances: typing.ClassVar[tuple[int, ...]] = (100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000)

	_distance: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))

	#@_distance.validator
	# def _distance_check(self, attribute: attrs.Attribute, value: int) -> bool:
	# 	if value not in self._distances:
	# 		raise ValueError("value of " + str(value) + " is not a valid distance.")
	# 	return True

	@staticmethod
	def allDistances() -> list["DistanceValueClass"]:
		res = []
		for i in DistanceValueClass._distances:
			res.append(DistanceValueClass(distance=i))

		return res

	def isValidDistance(self) -> bool:
		return (self._distance in self._distances)

	def getPoints(self, time_cls: time.TimeClass) -> float:
		return (time_cls.getTime() * 500 / self._distance)

	def getValue(self) -> int:
		return self._distance

	def equal(self, o: "DistanceValueClass|float") -> bool:
		if isinstance(o, float):
			return self._distance == o
		else:
			return self._distance == o._distance

	def __str__(self) -> str:
		return str(str(self._distance) + " meter")

	def __repr__(self) -> str:
		return str(self._distance)

	def __lt__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self._distance < o
		else:
			o = typeguard.check_type(o, type(self))
			return self._distance < o._distance

	def __le__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self._distance <= o
		else:
			o = typeguard.check_type(o, type(self))
			return self._distance <= o._distance

	def __gt__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self._distance > o
		else:
			o = typeguard.check_type(o, type(self))
			return self._distance > o._distance

	def __ge__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self._distance >= o
		else:
			o = typeguard.check_type(o, type(self))
			return self._distance >= o._distance

@typeguard.typechecked
def DistanceValueClass_converter(data: DistanceValueClass|int) -> DistanceValueClass:
	if isinstance(data, DistanceValueClass):
		return data
	else:
		return DistanceValueClass(distance=data)

@typeguard.typechecked
def DistanceValueClass_converter_none(data: DistanceValueClass|int|None) -> DistanceValueClass|None:
	if isinstance(data, DistanceValueClass):
		return data
	if isinstance(data, int):
		return DistanceValueClass(distance=data)
	return None

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistanceClass(base.BaseClass):
	_id: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_discipline: discipline.DisciplineClass = base.BaseClass.serializable(True, converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore [misc]
	_number: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_value: DistanceValueClass = base.BaseClass.serializable(True, converter=DistanceValueClass_converter, validator=attrs.validators.instance_of(DistanceValueClass)) # type: ignore [misc]
	_valueQuantity: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_name: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_starts: datetime.datetime = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]

	def getId(self) -> uuid.UUID:
		return self._id

	def getDiscipline(self) -> discipline.DisciplineClass:
		return self._discipline

	def getNumber(self) -> int:
		return self._number

	def getDistance(self) -> DistanceValueClass:
		return self._value

	def getDistanceValue(self) -> int:
		return self._value.getValue()

	def getQuantity(self) -> int:
		return self._valueQuantity

	def getName(self) -> str:
		return self._name

	def getStartDate(self) -> datetime.datetime:
		return self._starts

	def equal(self, o: "DistanceClass") -> bool:
		return (self._id == o._id and
		  self._discipline == o._discipline and
		  self._number == o._number and
		  self._value == o._value and
		  self._valueQuantity == o._valueQuantity and
		  self._name == o._name and
		  self._starts == o._starts)

	def __str__(self) -> str:
		return str(str(self._name) + " - " + str(self._value))

	def __repr__(self) -> str:
		return self.__str__()

@typeguard.typechecked
def DistanceClass_converter(data: DistanceClass|dict[str, typing.Any]) -> DistanceClass:
	return utils.class_converter_except(data, DistanceClass)

@typeguard.typechecked
def DistanceClassTuple_converter(data: tuple[DistanceClass,...]|list[dict[str, typing.Any]]) -> tuple[DistanceClass,...]:
	return utils.ClassTuple_converter(data, DistanceClass)
