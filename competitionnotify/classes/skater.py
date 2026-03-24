#!/bin/python

import typing
import typeguard
import attrs
import logging
import datetime

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.categories as categories

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class PersonNameClass(base.BaseClass):
	_firstName: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_surname: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_surnamePrefix: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_initials: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def getFullName(self) -> str:
		name: str = self._surname
		if self._surnamePrefix is not None:
			name = self._surnamePrefix + " " + name
		if self._firstName is not None:
			name = self._firstName + " " + name
		return name

	def getSurename(self) -> str:
		return self._surname

	def getSurenameWithPrefix(self) -> str:
		name: str = self._surname
		if self._surnamePrefix is not None:
			name = self._surnamePrefix + " " + name
		return name

	def getFirstName(self) -> str:
		return self._firstName

	def getInitials(self) -> str:
		if self._initials is None:
			return str()
		return self._initials

	def getPrefix(self) -> str:
		if self._surnamePrefix is None:
			return str()
		return self._surnamePrefix

	def equal(self, o: object) -> bool:
		if not isinstance(o, type(self)):
			raise TypeError(f'Can only use comparison on two objects of the same type (given: {type(self).__name__}, {type(o).__name__}).')
		else:
			return self._firstName == o._firstName and self._surname == o._surname and self._surnamePrefix == o._surnamePrefix

@typeguard.typechecked
def PersonNameClass_converter(data: PersonNameClass|dict[str, typing.Any]|None) -> PersonNameClass:
	return utils.class_converter_except(data, PersonNameClass)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class MailOptionsClass(base.BaseClass):
	_emailAddress: str = attrs.field(validator=attrs.validators.instance_of(str))
	_homeVenue: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_venues: tuple[str,...] = attrs.field(converter=utils.StrTuple_convertor, validator=attrs.validators.deep_iterable( # type: ignore [misc]
			member_validator=attrs.validators.instance_of(str),
			iterable_validator=attrs.validators.instance_of(tuple)))
	_disciplines: tuple[discipline.DisciplineClass,...] = attrs.field(converter=discipline.DisciplineClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
			member_validator=attrs.validators.instance_of(discipline.DisciplineClass),
			iterable_validator=attrs.validators.instance_of(tuple)))

	def getEmailAddress(self) -> str:
		return self._emailAddress

	def getVenues(self) -> tuple[str,...]:
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
		club = data.get('code')
		if isinstance(club, int):
			return club
		elif isinstance(club, str):
			return int(club)
		else:
			return -1

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class SkaterClass(base.BaseClass):
	_category: categories.CategoryClass = base.BaseClass.serializable(True, converter=categories.CategoryClass_converter, validator=attrs.validators.instance_of(categories.CategoryClass)) # type: ignore [misc]
	_club: int = base.BaseClass.serializable(True, converter=club_converter, validator=attrs.validators.instance_of(int)) # type: ignore [misc]
	_flags: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_key: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_personName: PersonNameClass = base.BaseClass.serializable(True, converter=PersonNameClass_converter, validator=attrs.validators.instance_of(PersonNameClass)) # type: ignore [misc]
	_season: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_validFrom: datetime.datetime = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_validTo: datetime.datetime = base.BaseClass.serializable(True, converter=utils.datetime_converter, validator=attrs.validators.instance_of(datetime.datetime)) # type: ignore [misc]
	_legNumber: int|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_number: int|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_sponsor: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder1: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder2: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_venueCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_mailOptions: MailOptionsClass|None = base.BaseClass.serializable(True, default=None, converter=MailOptionsClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(MailOptionsClass))) # type: ignore [misc]

	def isLicenseValid(self, date: datetime.datetime = datetime.datetime.now()) -> bool:
		return (self._validFrom <= date and self._validTo >= date)

	def getName(self) -> str:
		return self._personName.getFullName()

	def getSurename(self) -> str:
		return self._personName.getSurename()

	def getFirstName(self) -> str:
		return self._personName.getFirstName()

	def getInitials(self) -> str:
		return self._personName.getInitials()

	def getPrefix(self) -> str:
		return self._personName.getPrefix()

	def getClub(self) -> int:
		return self._club

	def getCategory(self) -> categories.CategoryClass:
		return self._category

	def getCategoryString(self) -> str:
		return str(self._category)

	def isCategory(self, categories: list[str]) -> bool:
		return (self._category in categories)

	def getOptions(self) -> MailOptionsClass|None:
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

	def getEmailAddress(self) -> str:
		if isinstance(self._mailOptions, MailOptionsClass):
			return self._mailOptions.getEmailAddress()
		return str()

	def getId(self) -> str:
		return self._key

	def getHomeVenue(self) -> str|None:
		return self._venueCode

	def sqlDict(self) -> dict[str, str|int|bool]:
		o = self.getOptions()
		if o is None:
			o = MailOptionsClass(emailAddress="", homeVenue=False, venues=[], disciplines=[])
		data: dict[str, str|int|bool] = {
			'number': self._key,
			'email': o._emailAddress,
			'home_venue': o.homeVenue(),
			'venues': ",".join(o.getVenues()),
			'disciplines': 0,
			'team': 0,
		}
		return data

	def equal(self, o: object) -> bool:
		if not isinstance(o, type(self)):
			raise TypeError(f'Can only use comparison on two objects of the same type (given: {type(self).__name__}, {type(o).__name__}).')
		else:
			return self._category == o._category and self._club == o._club and self._key == o._key and self._personName == o._personName

@typeguard.typechecked
def SkaterClass_converter(data: SkaterClass|dict[str, typing.Any]|None) -> SkaterClass:
	return utils.class_converter_except(data, SkaterClass)