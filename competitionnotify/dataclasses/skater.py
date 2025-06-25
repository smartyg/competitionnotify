#!/bin/python

import typing
import typeguard
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
	_initials: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_surname: str = attrs.field(validator=attrs.validators.instance_of(str))
	_surnamePrefix: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def getFullName(self) -> str:
		name: str = self._surname
		if self._surnamePrefix is not None:
			name = self._surnamePrefix + " " + name
		if self._firstName is not None:
			name = self._firstName + " " + name
		return name

	def getSurename(self) -> str:
		return self._surname

@typeguard.typechecked
def PersonNameClass_converter(data: PersonNameClass|dict[str, typing.Any]|None) -> PersonNameClass:
	return utils.class_converter_except(data, PersonNameClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class MailOptionsClass(base.BaseClass):
	_emailAddress: str = attrs.field(validator=attrs.validators.instance_of(str))
	_homeVenue: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_venues: tuple[str,...] = attrs.field(converter=utils.StrTuple_convertor, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(str),
			iterable_validator=attrs.validators.instance_of(tuple)))
	_disciplines: tuple[discipline.DisciplineClass,...] = attrs.field(converter=discipline.DisciplineClassTuple_converter, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(discipline.DisciplineClass),
			iterable_validator=attrs.validators.instance_of(tuple)))

	def getVenue(self) -> tuple[str,...]:
		return self._venues

	def getDisciplines(self) -> tuple[discipline.DisciplineClass,...]:
		return self._disciplines

	def homeVenue(self) -> bool:
		return self._homeVenue

@typeguard.typechecked
def MailOptionsClass_converter(data: MailOptionsClass|dict[str, typing.Any]|None) -> MailOptionsClass|None:
	return utils.class_converter_none(data, MailOptionsClass)

@typeguard.typechecked
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
	_personName: PersonNameClass = attrs.field(converter=PersonNameClass_converter, validator=attrs.validators.instance_of(PersonNameClass))
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))
	_sponsor: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder1: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder2: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_validFrom: datetime = attrs.field(converter=dataclasses.datetime_converter, validator=attrs.validators.instance_of(datetime))
	_validTo: datetime = attrs.field(converter=dataclasses.datetime_converter, validator=attrs.validators.instance_of(datetime))
	#_venueCode: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_venueCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_mailOptions: MailOptionsClass|None = attrs.field(default=None, converter=MailOptionsClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(MailOptionsClass)))

	def isLicenseValid(self, date: datetime = datetime.now()) -> bool:
		return (self._validFrom <= date and self._validTo >= date)

	def getName(self) -> str:
		return self._personName.getFullName()

	def getClub(self) -> int:
		return self._club

	def getCategory(self) -> str:
		return str(self._category)

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

	def getId(self) -> str:
		return self._key

@typeguard.typechecked
def SkaterClass_converter(data: SkaterClass|dict[str, typing.Any]|None) -> SkaterClass:
	return utils.class_converter_except(data, SkaterClass)