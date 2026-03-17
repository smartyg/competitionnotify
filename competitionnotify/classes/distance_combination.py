#!/bin/python

import typing
import typeguard
import attrs
import logging
import datetime
import uuid

import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.categories as categories
import competitionnotify.classes.distance as distance
import competitionnotify.classes.payment as payment
import competitionnotify.classes.time as time
import competitionnotify.classes.timefilter as timefilter
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistancecombinationClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_number: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_classFilter: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_categoryFilter: categories.CategoryFilterClass = attrs.field(converter=categories.CategoryFilterClass_converter, validator=attrs.validators.instance_of(categories.CategoryFilterClass)) # type: ignore [misc]
	_classificationWeight: int = attrs.field(validator=attrs.validators.instance_of(int))
	_distances: tuple[distance.DistanceClass, ...] = attrs.field(converter=distance.DistanceClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(distance.DistanceClass),
		iterable_validator=attrs.validators.instance_of(tuple)))
	_starts: datetime.datetime|None = attrs.field(default=None, converter=utils.datetime_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(datetime.datetime))) # type: ignore [misc]
	_competitorsTotal: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsPending: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsConfirmed: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsWithdrawn: int = attrs.field(validator=attrs.validators.instance_of(int))
	_onlyCountFastestDistanceWhenSameLength: bool = attrs.field(validator=attrs.validators.instance_of(bool))

	def getId(self) -> uuid.UUID:
		return self._id

	def getName(self) -> str:
		return self._name

	def getCategoryFilter(self) -> categories.CategoryFilterClass:
		return self._categoryFilter

@typeguard.typechecked
def DistancecombinationClass_converter(data: DistancecombinationClass|dict[str, typing.Any]) -> DistancecombinationClass:
	return utils.class_converter_except(data, DistancecombinationClass)

@typeguard.typechecked
def DistancecombinationClassTuple_converter(data: tuple[DistancecombinationClass,...]|list[dict[str, typing.Any]]) -> tuple[DistancecombinationClass,...]:
	return utils.ClassTuple_converter(data, DistancecombinationClass)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistancecombinationsClass(base.BaseClass):
	_distancecombinations: tuple[DistancecombinationClass, ...] = attrs.field(converter=DistancecombinationClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(DistancecombinationClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	def getTuple(self) -> tuple[DistancecombinationClass, ...]:
		return self._distancecombinations

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistancecombinationsettingClass(base.BaseClass):
	_distanceCombinationId: uuid.UUID = attrs.field(converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_isClosed: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_opens: datetime.datetime|None = attrs.field(converter=utils.datetime_converter_none,validator=attrs.validators.optional(attrs.validators.instance_of(datetime.datetime))) # type: ignore [misc]
	_allowedRegistrations: int = attrs.field(validator=attrs.validators.instance_of(int))
	_invitees: list[float] = attrs.field(default=[], validator=attrs.validators.deep_iterable(
		member_validator=attrs.validators.instance_of(float),
		iterable_validator=attrs.validators.instance_of(list))) #TODO: fix type
	_requireSerieRegistration: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_maxCompetitors: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_requireVenueSubscription: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_limitTimeDistanceDiscipline: discipline.DisciplineClass|None = attrs.field(default=None, converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore [misc]
	_limitTimeDistanceValue: distance.DistanceValueClass|None = attrs.field(default=None, converter=distance.DistanceValueClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(distance.DistanceValueClass))) # type: ignore [misc]
	_limitTime: time.TimeClass|None = attrs.field(default=None, converter=time.TimeClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(time.TimeClass))) # type: ignore [misc]
	_thresholdTimeDistanceDiscipline: discipline.DisciplineClass|None = attrs.field(default=None, converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore [misc]
	_thresholdTimeDistanceValue: distance.DistanceValueClass|None = attrs.field(default=None, converter=distance.DistanceValueClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(distance.DistanceValueClass))) # type: ignore [misc]
	_thresholdTime: time.TimeClass|None = attrs.field(default=None, converter=time.TimeClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(time.TimeClass))) # type: ignore [misc]
	_clubCodeFilter: tuple[int,...] = attrs.field(default=tuple(), converter=utils.string_to_tuple_int_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(int),
		iterable_validator=attrs.validators.instance_of(tuple)))
	_homeVenueFilter: tuple[str,...]|None = attrs.field(default=None, converter=utils.string_to_tuple_str_converter, validator=attrs.validators.optional(attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(tuple))))
	_seriePaymentOption: payment.PaymentClass|None = attrs.field(default=None, converter=payment.PaymentClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(payment.PaymentClass))) # type: ignore [misc]
	_competitionPaymentOption: payment.PaymentClass|None = attrs.field(default=None, converter=payment.PaymentClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(payment.PaymentClass))) # type: ignore [misc]
	#_competitionPaymentOption: float|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	#_competitionPaymentOption

	def getId(self) -> uuid.UUID:
		return self._distanceCombinationId

	def getClubCodes(self) -> tuple[int, ...]|None:
		return self._clubCodeFilter

	def getHomeVenueFilter(self) -> tuple[str,...]|None:
		return self._homeVenueFilter

	def getInvitees(self) -> typing.Any:
		return self._invitees

	def getTimeFilter(self) -> timefilter.TimeFilterClass:
		return timefilter.TimeFilterClass(
			limitTimeDistanceDiscipline=self._limitTimeDistanceDiscipline,
			limitTimeDistanceValue=self._limitTimeDistanceValue,
			limitTime=self._limitTime,
			thresholdTimeDistanceDiscipline=self._thresholdTimeDistanceDiscipline,
			thresholdTimeDistanceValue=self._thresholdTimeDistanceValue,
			thresholdTime=self._thresholdTime
		)

@typeguard.typechecked
def DistancecombinationsettingClass_converter(data: DistancecombinationsettingClass|dict[str, typing.Any]) -> DistancecombinationsettingClass:
	return utils.class_converter_except(data, DistancecombinationsettingClass)

@typeguard.typechecked
def DistancecombinationsettingClassTuple_converter(data: tuple[DistancecombinationsettingClass,...]|list[dict[str, typing.Any]]|dict[str, typing.Any]) -> tuple[DistancecombinationsettingClass,...]:
	return utils.ClassTuple_converter(data, DistancecombinationsettingClass)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistancecombinationsettingsClass(base.BaseClass):
	_distancecombinationsettings: tuple[DistancecombinationsettingClass, ...] = attrs.field(converter=DistancecombinationsettingClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(DistancecombinationsettingClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	def getTuple(self) -> tuple[DistancecombinationsettingClass, ...]:
		return self._distancecombinationsettings
