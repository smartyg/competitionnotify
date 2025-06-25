#!/bin/python

import typing
import typeguard
import attrs
import logging
import uuid
from datetime import datetime

import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.time as time
import competitionnotify.dataclasses.classes as classes
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistanceValueClass(base.BaseClass):
	_distances: typing.ClassVar[tuple[int, ...]] = (100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000)

	_distance: int = attrs.field(validator=attrs.validators.instance_of(int))

	@_distance.validator
	def distance_check(self, attribute: str, value: int) -> bool:
		if value not in self._distances:
			raise ValueError("value of " + str(value) + " is not a valid distance.")
		return True

	@staticmethod
	def allDistances() -> list["DistanceValueClass"]:
		res = []
		for i in DistanceValueClass._distances:
			res.append(DistanceValueClass(distance=i))

		return res

	def __str__(self) -> str:
		return str(str(self._distance) + " meter")

	def getPoints(self, time_cls: time.TimeClass) -> float:
		return (time_cls.getTime() * 500 / self._distance)

	def getValue(self) -> int:
		return self._distance

@typeguard.typechecked
def DistanceValueClass_converter(d: DistanceValueClass|int) -> DistanceValueClass:
	if isinstance(d, DistanceValueClass):
		return d
	else:
		return DistanceValueClass(distance=d)

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistanceClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(converter=classes.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_discipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass))
	_number: int = attrs.field(validator=attrs.validators.instance_of(int))
	_value: DistanceValueClass = attrs.field(converter=DistanceValueClass_converter, validator=attrs.validators.instance_of(DistanceValueClass))
	_valueQuantity: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_starts: datetime = attrs.field(converter=classes.datetime_converter, validator=attrs.validators.instance_of(datetime))

	def getDistanceValue(self) -> int:
		return self._distance.getValue()

@typeguard.typechecked
def DistanceClass_converter(data: DistanceClass|dict[str, typing.Any]) -> DistanceClass:
	return utils.class_converter_except(d, DistanceClass)

@typeguard.typechecked
def DistanceClassTuple_converter(data: tuple[DistanceClass,...]|list[dict[str, typing.Any]]) -> tuple[DistanceClass,...]:
	return utils.ClassTuple_converter(data, DistanceClass)
