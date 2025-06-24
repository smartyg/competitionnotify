#!/bin/python

import typing
import typeguard
import attrs
import logging
import uuid

import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.classes as classes
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.dataclasses.categories as categories
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(converter=classes.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_number: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_classFilter: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_categoryFilter: categories.CategoryFilterClass = attrs.field(converter=categories.CategoryFilterClass_converter, validator=attrs.validators.instance_of(categories.CategoryFilterClass))
	_classificationWeight: int = attrs.field(validator=attrs.validators.instance_of(int))
	_distances: tuple[DistanceClass] = attrs.field(converter=distance.DistanceClassTuple_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DistanceClass),
            iterable_validator=attrs.validators.instance_of(tuple)))
	_starts: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_competitorsTotal: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsPending: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsConfirmed: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsWithdrawn: int = attrs.field(validator=attrs.validators.instance_of(int))
	_onlyCountFastestDistanceWhenSameLength: bool = attrs.field(validator=attrs.validators.instance_of(bool))

@typeguard.typechecked
def DistancecombinationClass_converter(data: DistancecombinationClass|dict[str, typing.Any]) -> DistancecombinationClass:
	return utils.class_factory_except(data, DistancecombinationClass)

@typeguard.typechecked
def DistancecombinationClassTuple_converter(data: tuple[DistancecombinationClass,...]|list[dict[str, typing.Any]]) -> tuple[DistancecombinationClass,...]:
	return utils.ClassTuple_converter(data, DistancecombinationClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationsClass(base.BaseClass):
	_distancecombinations: tuple[DistancecombinationClass] = attrs.field(converter=DistancecombinationClassTuple_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DistancecombinationClass),
            iterable_validator=attrs.validators.instance_of(tuple)))

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationsettingClass(base.BaseClass):
	_distanceCombinationId: uuid.UUID = attrs.field(converter=classes.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_isClosed: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_opens: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_allowedRegistrations: int = attrs.field(validator=attrs.validators.instance_of(int))
	_invitees: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_requireSerieRegistration: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_maxCompetitors: int = attrs.field(validator=attrs.validators.instance_of(int))
	_requireVenueSubscription: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_limitTimeDistanceDiscipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass))
	_limitTimeDistanceValue: int = attrs.field(validator=attrs.validators.instance_of(int))
	#_limitTime: "00:00:50",
	_thresholdTimeDistanceDiscipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass))
	_thresholdTimeDistanceValue: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_thresholdTime: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_clubCodeFilter: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_homeVenueFilter: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_seriePaymentOption: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	#_competitionPaymentOption

@typeguard.typechecked
def DistancecombinationsettingClassTuple_converter(data: tuple[DistancecombinationsettingClass,...]|list[dict[str, typing.Any]]|dict[str, typing.Any]) -> tuple[DistancecombinationsettingClass,...]:
	return utils.ClassTuple_converter(data, DistancecombinationsettingClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationsettingsClass(base.BaseClass):
	_distancecombinationsettings: tuple[DistancecombinationsettingClass] = attrs.field(converter=ClassTuple_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DistancecombinationsettingClass),
            iterable_validator=attrs.validators.instance_of(tuple)))
