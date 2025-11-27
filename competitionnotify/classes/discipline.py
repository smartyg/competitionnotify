#!/bin/python

import attrs
import typeguard
import typing
import re
import logging
import collections.abc

import competitionnotify.classes.base as base

logger = logging.getLogger(__name__)

@typeguard.typechecked
def discipline_class_discipline_validator(instance: "DisciplineClass", attribute: attrs.Attribute, value: int):
	if value > (len(instance._disciplines) - 1) or value < -1:
		raise ValueError("No valid value for discipline (" + str(value) + ")")

@attrs.define(frozen=True, kw_only=True, slots=False)
class DisciplineClass(base.BaseClass):
	_disciplines: typing.ClassVar[tuple] = ("Inline", "LongTrack", "Marathon", "ShortTrack")
	_prefix: typing.ClassVar[str] = "SpeedSkating"
	#_subtypes1: typing.ClassVar[tuple] = ("MassStartDistance", "PairsDistance", "PointToPoint", "Track")
	#_subtypes2: typing.ClassVar[tuple] = ("MarathonDistance", "EliminationDistance", "OneLapDistance", "PointsDistance", "RelayDistance", "SprintDistance", "TimeTrialDistance", "Individual", "TeamPursuit", "TeamRelay", "TeamSprint")

	_discipline:int = attrs.field(validator=[attrs.validators.instance_of(int), discipline_class_discipline_validator])
	_subtype1:str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_subtype2:str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def isValid(self) -> bool:
		return True if self._discipline >= 0 and self._discipline < len(self._disciplines) else False

	def isUnknown(self) -> bool:
		return True if self._discipline == -1 else False

	def equal(self, o: "DisciplineClass") -> bool:
		return self._discipline == o._discipline

	def asString(self) -> str:
		if self._discipline == -1:
			return DisciplineClass._prefix + ".Unknown"
		return_string: str = DisciplineClass._prefix + "." + DisciplineClass._disciplines[self._discipline]
		if self._subtype1 is not None and len(self._subtype1) > 0:
			return_string += "." + self._subtype1
			if self._subtype2 is not None and len(self._subtype2) > 0:
				return_string += "." + self._subtype2
		return return_string

	def __str__(self) -> str:
		return self.asString()

	def __repr__(self) -> str:
		return self.asString()

	def __eq__(self, o: object) -> bool:
		if o is attrs.NOTHING:
			return False
		if not isinstance(o, DisciplineClass):
			raise TypeError('Can only use comparison on two DisciplineClass objects')
		return self.equal(o)

	@staticmethod
	def getDisciplineByString(string: str|None) -> "DisciplineClass":
		d:int = -1
		subtype1: str|None = None
		subtype2: str|None = None
		if isinstance(string, str):
			parts = re.split(r'[.]', string)
			if parts[0] != DisciplineClass._prefix:
				print(parts)
				raise ValueError('String is not a valid discipline text ("' + string + '").')
			for i in range(len(DisciplineClass._disciplines)):
				if parts[1] == DisciplineClass._disciplines[i]:
					d = i
			if len(parts) > 2:
				subtype1 = parts[2]
			if len(parts) > 3:
				subtype2 = parts[3]
		return DisciplineClass(discipline=d, subtype1=subtype1, subtype2=subtype2)

@typeguard.typechecked
def DisciplineClass_converter(data: DisciplineClass|str|None) -> DisciplineClass:
	if isinstance(data, DisciplineClass):
		return data
	else:
		return DisciplineClass.getDisciplineByString(string=data)

@typeguard.typechecked
def DisciplineClassTuple_converter(data: tuple[DisciplineClass, ...]|collections.abc.Sequence[DisciplineClass|str]|str|None) -> tuple[DisciplineClass, ...]:
	if isinstance(data, tuple):
		return typeguard.check_type(data, tuple[DisciplineClass, ...])
	elif isinstance(data, str):
		return tuple([DisciplineClass.getDisciplineByString(string=data)])
	elif isinstance(data, collections.abc.Sequence):
		data = typeguard.check_type(data, collections.abc.Sequence[DisciplineClass|str])
		if len(data) == 0:
			return tuple()
		elif isinstance(data[0], str):
			data = typeguard.check_type(data, collections.abc.Sequence[str])
			return tuple([DisciplineClass.getDisciplineByString(string=e) for e in data])
		return tuple(typeguard.check_type(data, collections.abc.Sequence[DisciplineClass]))
	else:
		return tuple()