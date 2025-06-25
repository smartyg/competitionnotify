#!/bin/python

import typing
import typeguard
import attrs
import logging
import uuid
from datetime import date, datetime

import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.dataclasses.categories as categories
import competitionnotify.dataclasses.venue as venue
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
def uuid_converter(data: uuid.UUID|str) -> uuid.UUID:
	if isinstance(data, uuid.UUID):
		return data
	else:
		return uuid.UUID(data, version=4)

@typeguard.typechecked
def datetime_converter(data: datetime|str) -> datetime:
	if isinstance(data, datetime):
		return data
	else:
		return datetime.fromisoformat(data)

@typeguard.typechecked
def date_converter(date_str: str) -> datetime.date:
	return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

@attrs.define(frozen=True, kw_only=True, slots=False)
class SeriesClass(base.BaseClass):
	_competitionsCount: int = attrs.field(validator=attrs.validators.instance_of(int))
	_discipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass))
	_id: uuid.UUID = attrs.field(converter=uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))

@typeguard.typechecked
def SeriesClass_converter(data: SeriesClass|dict[str, typing.Any]|None) -> SeriesClass|None:
	return utils.class_converter_none(data, SeriesClass)

@typeguard.typechecked
def name_converter(data: str|dict[str, str|None]|None) -> str|None:
	if data is None:
		return None
	elif isinstance(data, str):
		return data
	else:
		initials = data.get('initials', None)
		firstName = data.get('firstName', initials)
		surnamePrefix = data.get('surnamePrefix', None)
		surname = data.get('surname', None)
		name: str = str()
		if surname is not None:
			name = surname
			if surnamePrefix is not None:
				name = surnamePrefix + " " + name
		if firstName is not None:
			name = firstName + " " + name
		return name

@attrs.define(frozen=True, kw_only=True, slots=False)
class ContactClass(base.BaseClass):
	_organizationName: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str|None = attrs.field(default=None, converter=name_converter, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_email: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_phone: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_address: venue.AddressClass|None = attrs.field(default=None, converter=venue.AddressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(venue.AddressClass)))
	_extra: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_url: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

@typeguard.typechecked
def ContactClass_converter(data: ContactClass|dict[str, typing.Any]|None) -> ContactClass|None:
	return utils.class_converter_none(data, ContactClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class SettingClass(base.BaseClass):
	_opens: datetime = attrs.field(converter=datetime_converter, validator=attrs.validators.instance_of(datetime))
	_closes: datetime = attrs.field(converter=datetime_converter, validator=attrs.validators.instance_of(datetime))
	_withdrawUntil: datetime = attrs.field(converter=datetime_converter, validator=attrs.validators.instance_of(datetime))
	_isClosed: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_isRegularOpen: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_isLateOpen: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_maxCompetitors: int = attrs.field(default=-1, validator=attrs.validators.instance_of(int))
	#_distanceCombinations: DistanceCombinationsClass = attrs.field(converter=DistanceCombinationsClass_converter, validator=attrs.validators.instance_of(DistanceCombinationsClass))
	_extra: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_currency: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_contact: ContactClass|None = attrs.field(converter=ContactClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(ContactClass)))

@typeguard.typechecked
def SettingClass_converter(data: SettingClass|dict[str, typing.Any]) -> SettingClass:
	return utils.class_converter_except(data, SettingClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionClass(base.BaseClass):
	_settings: SettingClass = attrs.field(converter=SettingClass_converter, validator=attrs.validators.instance_of(SettingClass))
	_isLive: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
	_serie: SeriesClass|None = attrs.field(default=None, converter=SeriesClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(SeriesClass)))
	_venue: venue.VenueClass|None = attrs.field(default=None, converter=venue.VenueClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(venue.VenueClass)))
	_code: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_test: bool = attrs.field(default=True, validator=attrs.validators.instance_of(bool))
	_defaultStarter: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_defaultReferee1: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_defaultReferee2: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_isuId: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_allowToSendLive: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
	_location: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_locationFlags: int = attrs.field(default=0, validator=attrs.validators.instance_of(int))
	_extra: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_id: uuid.UUID = attrs.field(converter=uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_discipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass))
	_sponsor: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_starts: datetime = attrs.field(converter=datetime_converter, validator=attrs.validators.instance_of(datetime))
	_ends: datetime = attrs.field(converter=datetime_converter, validator=attrs.validators.instance_of(datetime))

	def getName(self) -> str:
		name = "Task " + str(self._id)
		if self._code is not None:
			if len(self._code) > 0:
				name += " (" + self._code + ")"
		return name

	def getId(self) -> uuid.UUID:
		return self._id

	def opens(self) -> datetime:
		return self._settings._opens

	def closes(self) -> datetime:
		return self._settings._closes

	def withdraw(self) -> datetime:
		return self._settings._withdrawUntil

	def isTest(self) -> bool:
		return self._test

@typeguard.typechecked
def CompetitionClass_converter(data: CompetitionClass|dict[str, typing.Any]) -> CompetitionClass:
	return utils.class_converter_except(data, CompetitionClass)
