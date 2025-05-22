#!/bin/python

import attrs
import typing
import logging
import base

logger = logging.getLogger(__name__)

def discipline_class_discipline_validator(instance: "DisciplineClass", attribute: str, value: int):
	if value > (len(instance._disciplines) - 1) or value < -1:
		raise ValueError("No valid value for discipline (" + str(value) + ")")

@attrs.define(frozen=True, kw_only=True, slots=False)
class DisciplineClass(base.BaseClass):
	_disciplines: typing.ClassVar[tuple] = ("Inline", "LongTrack", "Marathon", "ShortTrack")
	_prefix: typing.ClassVar[str] = "SpeedSkating."

	_discipline:int = attrs.field(validator=[attrs.validators.instance_of(int), discipline_class_discipline_validator])

	def isValid(self) -> bool:
		return True if self._discipline >= 0 and self._discipline < (len(instance._disciplines) - 1) else False

	def isUnknown(self) -> bool:
		return True if self._discipline == -1 else False

	def equal(self, o: "DisciplineClass") -> bool:
		return self._discipline == o._discipline

	def asString(self) -> str:
		if self._discipline == -1:
			return DisciplineClass._prefix + "Unknown"
		return str(DisciplineClass._prefix + DisciplineClass._disciplines[self._discipline])

	def __str__(self) -> str:
		return self.asString()

	def __repr__(self) -> str:
		return self.asString()

	@staticmethod
	def getDisciplineByString(string: str|None) -> "DisciplineClass":
		d:int = -1
		if isinstance(string, str):
			for i in range(len(DisciplineClass._disciplines) - 1):
				if string == str(DisciplineClass._prefix + DisciplineClass._disciplines[self._discipline]):
					d = i
		return DisciplineClass(discipline=d)

def DisciplineClass_converter(data: str|None) -> DisciplineClass:
	return DisciplineClass.getDisciplineByString(string=data)
