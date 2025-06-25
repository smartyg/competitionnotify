#!/bin/python

import typing
import typeguard
import attrs
import datetime

import competitionnotify.dataclasses.base as base
import competitionnotify.utils.utils as utils

@attrs.define(frozen=True, kw_only=True, slots=False)
class TimeClass(base.BaseClass):
	_minutes: int = attrs.field(validator=attrs.validators.instance_of(int))
	_seconds: int = attrs.field(validator=attrs.validators.instance_of(int))
	_miliseconds: int = attrs.field(validator=attrs.validators.instance_of(int))

	@_minutes.validator
	def minutes_check(self, attribute: str, value: int) -> bool:
		if value < 0 or value >= 60:
			raise ValueError("value of " + str(value) + " is not a valid number of minutes.")
		return True

	@_seconds.validator
	def seconds_check(self, attribute: str, value: int) -> bool:
		if value < 0 or value >= 60:
			raise ValueError("value of " + str(value) + " is not a valid number of seconds.")
		return True

	@_miliseconds.validator
	def miliseconds_check(self, attribute: str, value: int) -> bool:
		if value < 0 or value >= 1000:
			raise ValueError("value of " + str(value) + " is not a valid number of miliseconds.")
		return True

	def __str__(self) -> str:
		ms = self._miliseconds
		s = self._seconds
		m = self._minutes
		if self._minutes == 0:
			return str(f"{s}.{ms:03}")
		else:
			return str(f"{m}:{s:02}.{ms:03}")

	def getTime(self) -> float:
		return (self._minutes * 60) + self._seconds + (self._miliseconds / 1000)

	@classmethod
	def from_string(cls, time: str) -> "TimeClass":
		s1 = time.split(",")
		if len(s1) != 2:
			raise ValueError("string (\"" + time + "\") is not a valid time representation.")

		if len(s1[1]) == 1:
			miliseconds = int(s1[1]) * 100
		elif len(s1[1]) == 2:
			miliseconds = int(s1[1]) * 10
		elif len(s1[1]) == 3:
			miliseconds = int(s1[1])
		else:
			raise ValueError("string (\"" + time + "\") is not a valid time representation.")

		s2 = s1[0].split(".")
		if len(s2) == 1:
			minutes = 0
			seconds = int(s2[0])
		elif len(s2) == 2:
			minutes = int(s2[0])
			seconds = int(s2[1])
		else:
			raise ValueError("string (\"" + time + "\") is not a valid time representation.")

		return cls(minutes=minutes, seconds=seconds, miliseconds=miliseconds)

@typeguard.typechecked
def TimeClass_converter(time: TimeClass|str) -> TimeClass:
	if isinstance(time, TimeClass):
		return time
	else:
		return TimeClass.from_string(time)