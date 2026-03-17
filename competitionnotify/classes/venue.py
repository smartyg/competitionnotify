#!/bin/python

import typing
import typeguard
import attrs
import logging

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=True, order=False)
class AddressClass(base.BaseClass):
	_city: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_countryCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_line1: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_line2: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_postalCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_stateOrProvince: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def __str__(self) -> str:
		return f'{self._line1}, {self._line2}, {self._postalCode}, {self._city}, {self._stateOrProvince}, {self._countryCode}'

@typeguard.typechecked
def AddressClass_converter(data: AddressClass|dict[str, typing.Any]|None) -> AddressClass|None:
	return utils.class_converter_none(data, AddressClass)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class TrackClass(base.BaseClass):
	_venueCode: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_length: float = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(float))
	_venueDiscipline: discipline.DisciplineClass = base.BaseClass.serializable(True, converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore[misc]

	def getDiscipline(self) -> discipline.DisciplineClass:
		return self._venueDiscipline

	def getLength(self) -> float:
		return self._length

	def equal(self, o: "TrackClass") -> bool:
		return (self._venueCode == o._venueCode and
		  self._length == o._length and
		  self._venueDiscipline == o._venueDiscipline)

@typeguard.typechecked
def TrackClass_converter(data: TrackClass|dict[str, typing.Any]|None) -> TrackClass:
	return utils.class_converter_except(data, TrackClass)

@typeguard.typechecked
def TrackClassTuple_converter(data: tuple[TrackClass, ...]|list[dict[str, typing.Any]]|None) -> tuple[TrackClass, ...]:
	return utils.ClassTuple_converter(data, TrackClass);

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class VenueClass(base.BaseClass):
	_code: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_name: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_discipline: tuple[discipline.DisciplineClass,...] = base.BaseClass.serializable(True, converter=discipline.DisciplineClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore[misc]
            member_validator=attrs.validators.instance_of(discipline.DisciplineClass),
            iterable_validator=attrs.validators.instance_of(tuple)))
	_tracks: tuple[TrackClass, ...] = base.BaseClass.serializable(True, default=tuple(), converter=TrackClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore[misc]
            member_validator=attrs.validators.instance_of(TrackClass),
            iterable_validator=attrs.validators.instance_of(tuple)))
	_continentCode: str|None = base.BaseClass.serializable(True, default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_address: AddressClass|None = base.BaseClass.serializable(True, default=None, converter=AddressClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(AddressClass))) # type: ignore[misc]

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

	def equal(self, o: "VenueClass") -> bool:
		return (self._code == o._code and
			self._name == o._name and
			self._discipline == o._discipline and
			self._continentCode == o._continentCode)

@typeguard.typechecked
def VenueClass_converter(data: VenueClass|dict[str, typing.Any]|None) -> VenueClass|None:
	return utils.class_converter_none(data, VenueClass)
