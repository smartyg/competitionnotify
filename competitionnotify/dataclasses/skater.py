#!/bin/python

import typing
import attrs
import logging
from datetime import datetime, timedelta, timezone

import competitionnotify.utils.utils as utils
import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.classes as dataclasses
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.dataclasses.categories as categories
import competitionnotify.dataclasses.venue as venue

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class PersonNameClass(base.BaseClass):
	_firstName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_initials: str = attrs.field(validator=attrs.validators.instance_of(str))
	_surname: str = attrs.field(validator=attrs.validators.instance_of(str))
	_surnamePrefix: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

@attrs.define(frozen=True, kw_only=True, slots=False)
class MailOptionsClass(base.BaseClass):
	_emailAddress: str = attrs.field(validator=attrs.validators.instance_of(str))
	_homeVenue: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_venues: list[venue.VenueRefClass] = attrs.field(converter=..., validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(venue.VenueRefClass),
			iterable_validator=attrs.validators.instance_of(list)))
	_disciplines: list[discipline.DisciplineClass] = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(discipline.DisciplineClass),
			iterable_validator=attrs.validators.instance_of(list)))

	def getVenue(self) -> list[venue.VenueRefClass]:
		return self._venues

	def getDisciplines(self) -> list[discipline.DisciplineClass]:
		return self._disciplines

	def homeVenue(self) -> bool:
		return self._homeVenue

def club_converter(data: int|dict[str, typing.Any]) -> int:
	if isinstance(data, int):
		return data
	elif isinstance(data, dict):
		return data.get('code')

@attrs.define(frozen=True, kw_only=True, slots=False)
class SkaterClass(base.BaseClass):
	_category: categories.CategoryClass = attrs.field(converter=categories.CategoryClass_converter, validator=attrs.validators.instance_of(categories.CategoryClass))
	_club: int = attrs.field(converter=club_converter, validator=attrs.validators.instance_of(int))
	_flags: int = attrs.field(validator=attrs.validators.instance_of(int))
	_key: str = attrs.field(validator=attrs.validators.instance_of(str))
	_legNumber: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_number: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_personName: PersonNameClass
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))
	_sponsor: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder1: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder2: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_validFrom: datetime = attrs.field(converter=dataclasses.datetime_converter, validator=attrs.validators.instance_of(datetime))
	_validTo: datetime = attrs.field(converter=dataclasses.datetime_converter, validator=attrs.validators.instance_of(datetime))
	#_venueCode: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_venueCode: venue.VenueRefClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(venue.VenueRefClass)))
	_mailOptions: MailOptionsClass

	def isLicenseValid(self, date: datetime = datetime.now()) -> bool:
		return (self._validFrom <= date and self._validTo >= date)

	def getName(self) -> str:
		return self._personName._firstName + " " + self._personName._surname

	def getClub(self) -> int:
		return self._club

	def getCategory(self) -> str:
		return self._category

	def isCategory(self, categories: list[str]) -> bool:
		return (self._category in categories)

	def getOptions(self) -> MailOptionsClass:
		return self._mailOptions

	def getFlags(self) -> int:
		return self._flags

	def getTranspoders(self) -> list[str]:
		ret: list[str] = []
		if self._transponder1 is not None:
			ret.append(self._transponder1)
		if self._transponder2 is not None:
			ret.append(self._transponder2)
		return ret

	def getEmail(self) -> str:
		return self._emailAddress
