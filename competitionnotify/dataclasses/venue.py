#!/bin/python

import typing
import attrs
import logging

import competitionnotify.utils.utils as utils
import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.discipline as discipline

#import competitionnotify.providers.venues as venues

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class AdressClass(base.BaseClass):
	_city: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_countryCode: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_line1: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_line2: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_postalCode: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))
	_stateOrProvince: str = attrs.field(default=str(), validator=attrs.validators.instance_of(str))

def AdressClass_converter(data: AdressClass|dict[str, typing.Any]|None) -> type[AdressClass]|None:
	if isinstance(data, AdressClass):
		return data
	return utils.class_converter_none(data, AdressClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class TrackClass(base.BaseClass):
	_venueCode: str = attrs.field(validator=attrs.validators.instance_of(str))
	_length: float = attrs.field(validator=attrs.validators.instance_of(float))
	_venueDiscipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass))

	def getDiscipline(self) -> discipline.DisciplineClass:
		return self._venueDiscipline

def TrackClass_converter(data: list[TrackClass]|list[dict[str, typing.Any]]|None) -> list[TrackClass]:
	if isinstance(data, list):
		if len(data) > 0 and isinstance(data[0], TrackClass):
			return data

	ret: list[TrackClass] = []
	for d in data:
		cls = utils.class_converter_none(d, TrackClass)
		if cls is not None:
			ret.append(cls)
	return ret

@attrs.define(frozen=True, kw_only=True, slots=False)
class VenueClass(base.BaseClass):
	_address: AdressClass|None = attrs.field(default=None, converter=AdressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(AdressClass)))
	_code: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_continentCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_discipline: list[discipline.DisciplineClass] = attrs.field(converter=discipline.DisciplineClassList_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(discipline.DisciplineClass),
            iterable_validator=attrs.validators.instance_of(list)))
	_tracks: list[TrackClass] = attrs.field(default=list, converter=TrackClass_converter, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(TrackClass),
            iterable_validator=attrs.validators.instance_of(list)))

	def AddDiscipline(self, discipline: discipline.DisciplineClass) -> "VenueClass":
		if self.hasDiscipline(discipline):
			return self
		else:
			l = self._discipline
			l.append(discipline)
			return attrs.evolve(self, discipline=l)

	def AddTrack(self, track: TrackClass) -> "VenueClass":
		if self.hasTrack(track):
			return self
		else:
			l = self._tracks
			l.append(track)
			return attrs.evolve(self, tracks=l)

	def getCode(self) -> str:
		return self._code

	def hasDiscipline(self, discipline: discipline.DisciplineClass) -> bool:
		return (discipline in self._discipline)

	def hasTrack(self, track: TrackClass) -> bool:
		return (track in self._tracks)

def VenueClass_converter(data: dict[str, typing.Any]|None) -> type[VenueClass]|None:
	return utils.class_converter_none(data, VenueClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class VenueRefClass(base.BaseClass):
	_venueNumber: int = attrs.field(validator=attrs.validators.instance_of(int))
	#_venueProvider: venues.Venues = attrs.field(validator=attrs.validators.instance_of(venues.Venues))

	def getVenue(self) -> VenueClass:
		pass
		#return self._venueProvider.getVenueByNumber(self._venueNumber)
