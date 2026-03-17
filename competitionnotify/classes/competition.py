#!/bin/python

import typing
import typeguard
import attrs
import logging
import uuid
import  datetime

import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.categories as categories
import competitionnotify.classes.venue as venue
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class SeriesClass(base.BaseClass):
	_competitionsCount: int = attrs.field(validator=attrs.validators.instance_of(int))
	_discipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore [misc]
	_id: uuid.UUID = attrs.field(converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))

	def equal(self, o: "SeriesClass") -> bool:
		return (self._competitionsCount == o._competitionsCount and
			self._discipline == o._discipline and
			self._id == o._id and
			self._name == o._name and
			self._season == o._season)

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

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class ContactClass(base.BaseClass):
	_organizationName: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str|None = attrs.field(default=None, converter=name_converter, validator=attrs.validators.optional(attrs.validators.instance_of(str))) # type: ignore [misc]
	_email: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_phone: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_address: venue.AddressClass|None = attrs.field(default=None, converter=venue.AddressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(venue.AddressClass))) # type: ignore [misc]
	_extra: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_url: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def equal(self, o: "ContactClass") -> bool:
		return (self._organizationName == o._organizationName and
			self._name == o._name and
			self._email == o._email and
			self._phone == o._phone and
			self._address == o._address and
			self._extra == o._extra and
			self._url == o._url)

@typeguard.typechecked
def ContactClass_converter(data: ContactClass|dict[str, typing.Any]|None) -> ContactClass|None:
	return utils.class_converter_none(data, ContactClass)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class SettingClass(base.BaseClass):
	_opens: datetime.datetime = attrs.field(converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_closes: datetime.datetime = attrs.field(converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_withdrawUntil: datetime.datetime = attrs.field(converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_isClosed: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_isRegularOpen: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_isLateOpen: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_maxCompetitors: int = attrs.field(default=-1, validator=attrs.validators.instance_of(int))
	#_distanceCombinations: DistanceCombinationsClass = attrs.field(converter=DistanceCombinationsClass_converter, validator=attrs.validators.instance_of(DistanceCombinationsClass))
	_extra: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_currency: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_contact: ContactClass|None = attrs.field(converter=ContactClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(ContactClass))) # type: ignore [misc]

	def equal(self, o: "SettingClass") -> bool:
		return (self._opens == o._opens and
			self._closes == o._closes and
			self._withdrawUntil == o._withdrawUntil and
			self._isClosed == o._isClosed and
			self._isRegularOpen == o._isRegularOpen and
			self._isLateOpen == o._isLateOpen and
			self._maxCompetitors == o._maxCompetitors and
			self._extra == o._extra and
			self._currency == o._currency and
			self._contact == o._contact)

@typeguard.typechecked
def SettingClass_converter(data: SettingClass|dict[str, typing.Any]) -> SettingClass:
	return utils.class_converter_except(data, SettingClass)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class CompetitionClass(base.BaseClass):
	_settings: SettingClass = attrs.field(converter=SettingClass_converter, validator=attrs.validators.instance_of(SettingClass)) # type: ignore [misc]
	_isLive: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
	_serie: SeriesClass|None = attrs.field(default=None, converter=SeriesClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(SeriesClass))) # type: ignore [misc]
	_venue: venue.VenueClass|None = attrs.field(default=None, converter=venue.VenueClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(venue.VenueClass))) # type: ignore [misc]
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
	_id: uuid.UUID = attrs.field(converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_discipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore [misc]
	_sponsor: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_starts: datetime.datetime = attrs.field(converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_ends: datetime.datetime = attrs.field(converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]

	def getName(self) -> str:
		name = "Task " + str(self._id)
		if self._code is not None:
			if len(self._code) > 0:
				name += " (" + self._code + ")"
		return name

	def getId(self) -> uuid.UUID:
		return self._id

	def opens(self) -> datetime.datetime:
		return self._settings._opens

	def closes(self) -> datetime.datetime:
		return self._settings._closes

	def withdraw(self) -> datetime.datetime:
		return self._settings._withdrawUntil

	def isTest(self) -> bool:
		return self._test

	def getVenueCode(self) -> str:
		if isinstance(self._venue, venue.VenueClass):
			return self._venue.getCode()
		return str()

	def getDiscipline(self) -> discipline.DisciplineClass:
		return self._discipline

	def equal(self, o: "CompetitionClass") -> bool:
		return (self._settings == o._settings and
			self._isLive == o._isLive and
			self._serie == o._serie and
			self._venue == o._venue and
			self._code == o._code and
			self._test == o._test and
			self._defaultStarter == o._defaultStarter and
			self._defaultReferee1 == o._defaultReferee1 and
			self._defaultReferee2 == o._defaultReferee2 and
			self._isuId == o._isuId and
			self._allowToSendLive == o._allowToSendLive and
			self._location == o._location and
			self._locationFlags == o._locationFlags and
			self._extra == o._extra and
			self._id == o._id and
			self._discipline == o._discipline and
			self._sponsor == o._sponsor and
			self._name == o._name and
			self._starts == o._starts and
			self._ends == o._ends)


@typeguard.typechecked
def CompetitionClass_converter(data: CompetitionClass|dict[str, typing.Any]) -> CompetitionClass:
	return utils.class_converter_except(data, CompetitionClass)
