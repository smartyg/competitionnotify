#!/bin/python

import typing
import typeguard
import attrs
import logging

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.distance as distance
import competitionnotify.classes.time as time
import competitionnotify.classes.result as result

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class TimeFilterClass(base.BaseClass):
	_limitTimeDistanceDiscipline: discipline.DisciplineClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(discipline.DisciplineClass)))
	_limitTimeDistanceValue: distance.DistanceValueClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(distance.DistanceValueClass)))
	_limitTime: time.TimeClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(time.TimeClass)))
	_thresholdTimeDistanceDiscipline: discipline.DisciplineClass|None = attrs.field(default=None, validator=attrs.validators.instance_of(discipline.DisciplineClass))
	_thresholdTimeDistanceValue: distance.DistanceValueClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(distance.DistanceValueClass)))
	_thresholdTime: time.TimeClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(time.TimeClass)))

	def isValid(self) -> bool:
		return (
			self._limitTimeDistanceDiscipline is not None or
			self._limitTimeDistanceValue is not None or
			self._limitTime is not None or
			self._thresholdTimeDistanceDiscipline is not None or
			self._thresholdTimeDistanceValue is not None or
			self._thresholdTime is not None)

	def testResult(self, test_time: result.ResultClass|result.BestTimesClass) -> bool:
		test: result.ResultClass|None = None

		if isinstance(test_time, result.ResultClass):
			if test_time.getDistance() == self._limitTimeDistanceValue or test_time.getDistance() == self._thresholdTimeDistanceValue:
				test = test_time
		elif isinstance(test_time, result.BestTimesClass):
			if self._limitTimeDistanceValue is not None:
				test = test_time.getDistance(self._limitTimeDistanceValue)

		if test is None:
			return False

		if self._limitTime is not None:
			if test.getTime() > self._limitTime:
				return False

		return True