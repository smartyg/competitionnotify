#!/bin/python

import typing
import typeguard
import attrs
import logging

import competitionnotify.utils.utils as utils
import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.discipline as discipline

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class AddressClass(base.BaseClass):
	_city: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_countryCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_line1: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_line2: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_postalCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_stateOrProvince: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

@typeguard.typechecked
def AddressClass_converter(data: AddressClass|dict[str, typing.Any]|None) -> AddressClass|None:
	return utils.class_converter_none(data, AddressClass)

@attrs.define(frozen=True, kw_only=True, slots=False)
class TrackClass(base.BaseClass):
	_venueCode: str = attrs.field(validator=attrs.validators.instance_of(str))
	_length: float = attrs.field(validator=attrs.validators.instance_of(float))
	_venueDiscipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore[misc]

	def getDiscipline(self) -> discipline.DisciplineClass:
		return self._venueDiscipline

	def getLength(self) -> float:
		return self._length

@typeguard.typechecked
def TrackClass_converter(data: TrackClass|dict[str, typing.Any]|None) -> TrackClass:
	return utils.class_converter_except(data, TrackClass)

@typeguard.typechecked
def TrackClassTuple_converter(data: tuple[TrackClass, ...]|list[dict[str, typing.Any]]|None) -> tuple[TrackClass, ...]:
	return utils.ClassTuple_converter(data, TrackClass);

@attrs.define(frozen=True, kw_only=True, slots=False)
class VenueClass(base.BaseClass):
	_address: AddressClass|None = attrs.field(default=None, converter=AddressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(AddressClass))) # type: ignore[misc]
	# _code: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_code: str = attrs.field(validator=attrs.validators.instance_of(str))
	_continentCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	# _name: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_discipline: tuple[discipline.DisciplineClass,...] = attrs.field(converter=discipline.DisciplineClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore[misc]
            member_validator=attrs.validators.instance_of(discipline.DisciplineClass),
            iterable_validator=attrs.validators.instance_of(tuple)))
	_tracks: tuple[TrackClass, ...] = attrs.field(default=tuple(), converter=TrackClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore[misc]
            member_validator=attrs.validators.instance_of(TrackClass),
            iterable_validator=attrs.validators.instance_of(tuple)))

	def AddDiscipline(self, discipline: discipline.DisciplineClass) -> "VenueClass":
		if self.hasDiscipline(discipline):
			return self
		else:
			#l = self._discipline
			#l.append(discipline)
			l = self._discipline + tuple([discipline])
			return attrs.evolve(self, discipline=l)

	def AddTrack(self, track: TrackClass) -> "VenueClass":
		if self.hasTrack(track):
			return self
		else:
			#l = self._tracks
			#l.append(track)
			l = self._tracks + tuple([track])
			return attrs.evolve(self, tracks=l)

	def getCode(self) -> str:
		return self._code

	def getName(self) -> str:
		return self._name

	def hasDiscipline(self, discipline: discipline.DisciplineClass) -> bool:
		return (discipline in self._discipline)

	def hasTrack(self, track: TrackClass) -> bool:
		return (track in self._tracks)

	def getTracks(self) -> tuple[TrackClass, ...]:
		return self._tracks

	def numOfTracks(self) -> int:
		return len(self._tracks)

	def numOfDisciplines(self) -> int:
		return len(self._discipline)

	def getAddress(self) -> AddressClass|None:
		return self._address

@typeguard.typechecked
def VenueClass_converter(data: VenueClass|dict[str, typing.Any]|None) -> VenueClass|None:
	return utils.class_converter_none(data, VenueClass)
