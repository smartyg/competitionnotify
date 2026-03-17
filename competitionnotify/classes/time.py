#!/bin/python

import typing
import typeguard
import attrs
import datetime
import re

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class TimeClass(base.BaseClass):
	_hours: int = base.BaseClass.serializable(True, default=0, validator=attrs.validators.instance_of(int))
	_minutes: int = base.BaseClass.serializable(True, default=0, validator=attrs.validators.instance_of(int))
	_seconds: int = base.BaseClass.serializable(True, default=0, validator=attrs.validators.instance_of(int))
	_miliseconds: int = base.BaseClass.serializable(True, default=0, validator=attrs.validators.instance_of(int))

	@_hours.validator
	def hours_check(self, attribute: attrs.Attribute, value: int) -> bool:
		if value < 0 or value > 23:
			raise ValueError(f'value of {value!s} is not a valid number of hours.')
		return True

	@_minutes.validator
	def minutes_check(self, attribute: attrs.Attribute, value: int) -> bool:
		if value < 0 or value > 59:
			raise ValueError(f'value of {value!s} is not a valid number of minutes.')
		return True

	@_seconds.validator
	def seconds_check(self, attribute: attrs.Attribute, value: int) -> bool:
		if value < 0 or value > 59:
			raise ValueError(f'value of {value!s} is not a valid number of seconds.')
		return True

	@_miliseconds.validator
	def miliseconds_check(self, attribute: attrs.Attribute, value: int) -> bool:
		if value < 0 or value > 999:
			raise ValueError(f'value of {value!s} is not a valid number of miliseconds.')
		return True

	def getTime(self) -> float:
		return (self._hours * 3600) + (self._minutes * 60) + self._seconds + (self._miliseconds / 1000)

	def getHours(self) -> int:
		return self._hours

	def getMinutes(self) -> int:
		return self._minutes

	def getSeconds(self) -> int:
		return self._seconds

	def getMiliseconds(self) -> int:
		return self._miliseconds

	def equal(self, o: "TimeClass|float") -> bool:
		if isinstance(o, float):
			return self.getTime() == o
		else:
			return (self._hours == o._hours and
				self._minutes == o._minutes and
				self._seconds == o._seconds and
				self._miliseconds == o._miliseconds)

	def __str__(self) -> str:
		ms = self._miliseconds
		s = self._seconds
		m = self._minutes
		h = self._hours
		if self._hours > 0:
			return str(f'{h}:{m:02}:{s:02}.{ms:03}')
		elif self._minutes > 0:
			return str(f'{m}:{s:02}.{ms:03}')
		else:
			return str(f'{s}.{ms:03}')

	def __repr__(self) -> str:
		return self.__str__()

	def __lt__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self.getTime() < o
		else:
			o = typeguard.check_type(o, type(self))
			return self.getTime() < o.getTime()

	def __le__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self.getTime() <= o
		else:
			o = typeguard.check_type(o, type(self))
			return self.getTime() <= o.getTime()

	def __gt__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self.getTime() > o
		else:
			o = typeguard.check_type(o, type(self))
			return self.getTime() > o.getTime()

	def __ge__(self, o: object|float) -> bool:
		if isinstance(o, float):
			return self.getTime() >= o
		else:
			o = typeguard.check_type(o, type(self))
			return self.getTime() >= o.getTime()

	@staticmethod
	def _getMiliseconds(string: str) -> int:
		miliseconds: int
		if len(string) == 1:
			miliseconds = int(string) * 100
		elif len(string) == 2:
			miliseconds = int(string) * 10
		elif len(string) == 3:
			miliseconds = int(string)
		elif len(string) > 3:
			miliseconds = int(string[0:3])
		else:
			raise ValueError(f'string ({string!r}) is not a valid time representation.')
		return miliseconds

	@staticmethod
	def from_string(time: str) -> "TimeClass":
		hours:int = 0
		minutes:int = 0
		seconds:int = 0
		miliseconds:int = 0

		# There are different time notations:
		# - hh:mm:ss(.sss)
		# - ((hh:)mm:)ss(.sss)
		notation1 = re.compile(r'^((?P<minutes>[0-9]+)[:,.])?(?P<seconds>[0-9]+)[.,](?P<miliseconds>[0-9]+)$')
		notation2 = re.compile(r'^(?P<hours>[0-9]+):(?P<minutes>[0-9]+):(?P<seconds>[0-9]+)([.,](?P<miliseconds>[0-9]+))?$')

		notation1_match = notation1.match(time)
		notation2_match = notation2.match(time)
		if notation1_match is not None and bool(notation1_match):
			if notation1_match['minutes'] is not None:
				minutes = int(notation1_match['minutes'])
			seconds = int(notation1_match['seconds'])
			miliseconds = TimeClass._getMiliseconds(notation1_match['miliseconds'])

		elif notation2_match is not None and bool(notation2.match(time)):
			hours = int(notation2_match['hours'])
			minutes = int(notation2_match['minutes'])
			seconds = int(notation2_match['seconds'])
			if notation2_match['miliseconds'] is not None:
				miliseconds = TimeClass._getMiliseconds(notation2_match['miliseconds'])
		else:
			raise ValueError(f'String is not an time representation ({time!r}).')

		return TimeClass(hours=hours, minutes=minutes, seconds=seconds, miliseconds=miliseconds)

@typeguard.typechecked
def TimeClass_converter(time: TimeClass|str) -> TimeClass:
	if isinstance(time, TimeClass):
		return time
	else:
		return TimeClass.from_string(time)

@typeguard.typechecked
def TimeClass_converter_none(time: TimeClass|str|None) -> TimeClass|None:
	if isinstance(time, TimeClass):
		return time
	elif isinstance(time, str):
		try:
			return TimeClass.from_string(time)
		except:
			return None
	return None