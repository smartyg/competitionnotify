#!/bin/python

from typing import Any
import attrs
import logging
import uuid
from datetime import datetime, timedelta, timezone
from utils import class_factory, class_converter_none, class_converter_except
import base

logger = logging.getLogger(__name__)

def uuid_converter(data: str) -> uuid.UUID:
	return uuid.UUID(data, version=4)

def datetime_converter(data: str) -> datetime:
	return datetime.fromisoformat(data)

#TODO: do not use strings, but index the type
@attrs.define(frozen=True, kw_only=True, slots=False)
class DisciplineClass(base.BaseClass):
	_discipline:str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))

def DisciplineClass_converter(data: str|None) -> DisciplineClass:
	return DisciplineClass(discipline=data)

@attrs.define(frozen=True, kw_only=True, slots=False)
class SeriesClass(base.BaseClass):
	_competitionsCount: int = attrs.field(validator=attrs.validators.instance_of(int))
	_discipline: DisciplineClass = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.instance_of(DisciplineClass))
	_id: uuid.UUID = attrs.field(converter=uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))

def SeriesClass_converter(data: dict[str, Any]|None) -> type[SeriesClass]|None:
	return class_converter_none(data, SeriesClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class AdressClass(base.BaseClass):
	_city: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_countryCode: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_line1: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_line2: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_postalCode: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_stateOrProvince: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))

def AdressClass_converter(data: dict[str, Any]|None) -> type[AdressClass]|None:
	return class_converter_none(data, AdressClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class TrackClass(base.BaseClass):
	_venueCode: str = attrs.field(validator=attrs.validators.instance_of(str))
	_length: float = attrs.field(validator=attrs.validators.instance_of(float))
	_discipline: DisciplineClass = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.instance_of(DisciplineClass))

@attrs.define(frozen=True, kw_only=True, slots=False)
class VenueClass(base.BaseClass):
	_address: AdressClass|None = attrs.field(default=None, converter=AdressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(AdressClass)))
	_code: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_continentCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_disciplines: list[DisciplineClass] = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DisciplineClass),
            iterable_validator=attrs.validators.instance_of(list)))
	_tracks: list[TrackClass] = attrs.field(default=list, converter=TrackClass_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(TrackClass),
            iterable_validator=attrs.validators.instance_of(list)))

	def AddDiscipline(self, discipline: DisciplineClass) -> "VenueClass":
		if self.hasDiscipline(discipline):
			return self
		else:
			l = self._disciplines
			l.add(discipline)
			return attrs.evolve(self, disciplines=l)

	def AddTrack(self, track: TrackClass) -> "VenueClass":
		if self.hasTrack(track):
			return self
		else:
			l = self._tracks
			l.add(track)
			return attrs.evolve(self, tracks=l)

	def hasDiscipline(discipline: DisciplineClass) -> bool:
		return (discipline in self._disciplines)

	def hasTrack(track: TrackClass) -> bool:
		return (track in self._tracks)

def VenueClass_converter(data: dict[str, Any]|None) -> type[VenueClass]|None:
	return class_converter_none(data, VenueClass)

def name_converter(data: dict[str, str]|None) -> str|None:
	if data is None:
		return None
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
	_address: AdressClass|None = attrs.field(default=None, converter=AdressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(AdressClass)))
	_extra: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_url: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

def ContactClass_converter(data: dict[str, Any]|None) -> type[ContactClass]|None:
	return class_converter_none(data, ContactClass)

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

def SettingClass_converter(data: dict[str, Any]) -> type[SettingClass]:
	return class_converter_except(data, SettingClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionClass(base.BaseClass):
	_settings: SettingClass = attrs.field(converter=SettingClass_converter, validator=attrs.validators.instance_of(SettingClass))
	_isLive: bool = attrs.field(default=False, validator=attrs.validators.instance_of(bool))
	_serie: SeriesClass|None = attrs.field(default=None, converter=SeriesClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(SeriesClass)))
	_venue: VenueClass|None = attrs.field(default=None, converter=VenueClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(VenueClass)))
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
	_discipline: DisciplineClass = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.instance_of(DisciplineClass))
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

def CompetitionClass_converter(data: dict[str, Any]) -> type[CompetitionClass]:
	return class_converter_except(data, CompetitionClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistanceClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(converter=uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_discipline: DisciplineClass = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.instance_of(DisciplineClass))
	_number: int = attrs.field(validator=attrs.validators.instance_of(int))
	_value: int = attrs.field(validator=attrs.validators.instance_of(int))
	_valueQuantity: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_starts: datetime = attrs.field(converter=datetime_converter, validator=attrs.validators.instance_of(datetime))

def DistanceClass_converter(data: list[dict[str, Any]]) -> list[type[DistanceClass]]:
	ret: list[type[DistanceClass]] = []
	for d in data:
		c = class_factory(d, DistanceClass)
		if c is not None:
			ret.append(c)
	return ret

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(converter=uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_number: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_classFilter: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_categoryFilter: CategoryFilterClass = attrs.field(converter=CategoryFilterClass_converter, validator=attrs.validators.instance_of(CategoryFilterClass))
	_classificationWeight: int = attrs.field(validator=attrs.validators.instance_of(int))
	_distances: list[DistanceClass] = attrs.field(converter=DistanceClass_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DistanceClass),
            iterable_validator=attrs.validators.instance_of(list)))
	_starts: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_competitorsTotal: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsPending: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsConfirmed: int = attrs.field(validator=attrs.validators.instance_of(int))
	_competitorsWithdrawn: int = attrs.field(validator=attrs.validators.instance_of(int))
	_onlyCountFastestDistanceWhenSameLength: bool = attrs.field(validator=attrs.validators.instance_of(bool))

def DistancecombinationClass_converter(data: list[dict[str, Any]]) -> list[type[DistancecombinationClass]]:
	ret: list[type[DistancecombinationClass]] = []
	for d in data:
		c = class_factory(d, DistancecombinationClass)
		if c is not None:
			ret.insert(c.getNumber(), c)
	return ret

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationsClass(base.BaseClass):
	_distancecombinations: list[DistancecombinationClass] = attrs.field(converter=DistancecombinationClass_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DistancecombinationClass),
            iterable_validator=attrs.validators.instance_of(list)))

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationsettingClass(base.BaseClass):
	_distanceCombinationId: uuid.UUID = attrs.field(converter=uuid_converter, validator=attrs.validators.instance_of(uuid.UUID))
	_isClosed: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_opens: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_allowedRegistrations: int = attrs.field(validator=attrs.validators.instance_of(int))
	_invitees: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_requireSerieRegistration: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_maxCompetitors: int = attrs.field(validator=attrs.validators.instance_of(int))
	_requireVenueSubscription: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_limitTimeDistanceDiscipline: DisciplineClass = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.instance_of(DisciplineClass))
	_limitTimeDistanceValue: int = attrs.field(validator=attrs.validators.instance_of(int))
	#_limitTime: "00:00:50",
	_thresholdTimeDistanceDiscipline: DisciplineClass = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.instance_of(DisciplineClass))
	_thresholdTimeDistanceValue: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_thresholdTime: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_clubCodeFilter: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_homeVenueFilter: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	_seriePaymentOption: float|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(float))) #TODO: fix type
	#_competitionPaymentOption

def DistancecombinationsettingClass_converter(data: list[dict[str, Any]]) -> list[type[DistancecombinationsettingClass]]:
	ret: list[type[DistancecombinationsettingClass]] = []
	for d in data:
		c = class_factory(d, DistancecombinationsettingClass)
		if c is not None:
			ret.insert(c.getNumber(), c)
	return ret

@attrs.define(frozen=True, kw_only=True, slots=False)
class DistancecombinationsettingsClass(base.BaseClass):
	_distancecombinationsettings: list[DistancecombinationsettingClass] = attrs.field(converter=DistancecombinationsettingClass_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(DistancecombinationsettingClass),
            iterable_validator=attrs.validators.instance_of(list)))

@attrs.define(frozen=True, kw_only=True, slots=False)
class PersonNameClass(base.BaseClass):
	_firstName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_initials: str = attrs.field(validator=attrs.validators.instance_of(str))
	_surname: str = attrs.field(validator=attrs.validators.instance_of(str))
	_surnamePrefix: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))

@attrs.define(frozen=True, kw_only=True, slots=False)
class MailOptionsClass(base.BaseClass):
	_homeVenue: bool = attrs.field(validator=attrs.validators.instance_of(bool))
	_venues: list[str] = attrs.field(converter=..., validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(str),
			iterable_validator=attrs.validators.instance_of(list)))
	_disciplines: list[DisciplineClass] = attrs.field(converter=DisciplineClass_converter, validator=attrs.validators.deep_iterable(
			member_validator=attrs.validators.instance_of(DisciplineClass),
			iterable_validator=attrs.validators.instance_of(list)))

@attrs.define(frozen=True, kw_only=True, slots=False)
class SkaterClass(base.BaseClass):
	_category: str = attrs.field(validator=attrs.validators.instance_of(str))
	_club: int = attrs.field(validator=attrs.validators.instance_of(int))
	_flags: int = attrs.field(validator=attrs.validators.instance_of(int))
	_key: str = attrs.field(validator=attrs.validators.instance_of(str))
	_legNumber: int|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_number: int|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_personName: PersonNameClass
	_season: int = attrs.field(validator=attrs.validators.instance_of(int))
	_sponsor: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder1: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder2: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_validFrom: datetime
	_validTo: datetime
	_venueCode: str|None = attrs.field(validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_emailAddress: str = attrs.field(validator=attrs.validators.instance_of(str))
	_mailOptions: MailOptionsClass

	def isLicenseValid(self, date: datetime = now) -> bool:
		return (self._validFrom <= date and self._validTo >= date)

	def getName(self) -> str:
		return self._personName._firstName + " " + self._personName._surname

	def getClub(self) -> int:
		return self._club

	def getCategory(self) -> str:
		return self._category

	def isCategory(self, categories: list[str]) -> bool:
		return (self._category in categories)

	def filter(self, club_code: int|None = None, categories: list[str]|None = None, disciplines: DisciplineClass, venue_code: str,