#!/bin/python

import typing
import typeguard
import attrs
import logging
import datetime
import uuid

import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.categories as categories
import competitionnotify.classes.skater as skater
import competitionnotify.classes.timefilter as timefilter
import competitionnotify.classes.competition as competition
import competitionnotify.classes.result as result
import competitionnotify.classes.distance_combination as distance_combination

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class FilterClass(base.BaseClass):
	_competition_id: uuid.UUID = attrs.field(validator=attrs.validators.instance_of(uuid.UUID))
	_distance_id: uuid.UUID = attrs.field(validator=attrs.validators.instance_of(uuid.UUID))
	_venue: str = attrs.field(validator=attrs.validators.instance_of(str))
	_discipline: discipline.DisciplineClass = attrs.field(converter=discipline.DisciplineClass_converter, validator=attrs.validators.instance_of(discipline.DisciplineClass)) # type: ignore [misc]
	_clubs: tuple[int, ...]|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(int),
            iterable_validator=attrs.validators.instance_of(tuple))))
	_flags: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_transponder: bool|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
	_validLicense: datetime.datetime|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(datetime.datetime)))
	_categories: categories.CategoryFilterClass|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(categories.CategoryFilterClass)))
	_homeVenues: tuple[str, ...]|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(str),
            iterable_validator=attrs.validators.instance_of(tuple))))
	_invitees: None = attrs.field(default=None) # TODO: figure out how these invitees lists work and implement
	_time_filter: timefilter.TimeFilterClass = attrs.field(validator=attrs.validators.instance_of(timefilter.TimeFilterClass))

	def hasTimeFilter(self) -> bool:
		return self._time_filter.isValid()

	def _testVenue(self, test_skater: skater.SkaterClass) -> bool:
		mail_options = test_skater.getOptions()
		if isinstance(mail_options, skater.MailOptionsClass):
			home_venue = test_skater.getHomeVenue()
			if mail_options.homeVenue() and self._venue == home_venue:
				return True
			if self._venue in mail_options.getVenues():
				return True
		return False

	def _testDiscipline(self, disciplines: tuple[discipline.DisciplineClass, ...]) -> bool:
		return self._discipline in disciplines

	def _testClub(self, club: int) -> bool:
		if self._clubs is None:
			return True
		elif isinstance(self._clubs, int):
			return self._clubs == club
		else:
			return club in self._clubs

	def _testFlags(self, flags: int) -> bool:
		return True

	def _testTransponder(self, transponders: list[str]|None) -> bool:
		if self._transponder is None:
			return True
		elif isinstance(self._transponder, list):
			for t in transponders:
				if t is not None:
					if len(t) > 0:
						return True
			return False
		else:
			return True

	def _testLicense(self, test_skater: skater.SkaterClass) -> bool:
		if self._validLicense is not None:
			return test_skater.isLicenseValid(self._validLicense)
		else:
			return True

	def _testCategory(self, category: categories.CategoryClass) -> bool:
		if isinstance(self._categories, categories.CategoryFilterClass):
			return self._categories.hasCategory(category)
		return True

	def testSkater(self, test_skater: skater.SkaterClass) -> bool:
		# Get mailOptions
		mail_options = test_skater.getOptions()
		if isinstance(mail_options, skater.MailOptionsClass):
			return self._testCategory(test_skater.getCategory()) and \
				self._testVenue(test_skater) and \
				self._testDiscipline(mail_options.getDisciplines()) and \
				self._testClub(test_skater.getClub()) and \
				self._testFlags(test_skater.getFlags()) and \
				self._testTransponder(test_skater.getTranspoders()) and \
				self._testLicense(test_skater)
		return False

	def testTime(self, test_time: result.ResultClass|result.BestTimesClass) -> bool:
		return self._time_filter.testResult(test_time)

	def equal(self, o: "FilterClass") -> bool:
		pass
		return True

	def __eq__(self, o: object) -> bool:
		if o is attrs.NOTHING:
			return False
		if not isinstance(o, FilterClass):
			raise TypeError('Can only use comparison on two FilterClass objects')
		return self.equal(o)

	def __ne__(self, o: object) -> bool:
		if o is attrs.NOTHING:
			return False
		if not isinstance(o, FilterClass):
			raise TypeError('Can only use comparison on two FilterClass objects')
		return not self.equal(o)

	@staticmethod
	def fromDistanceCombination(c: competition.CompetitionClass, dc: distance_combination.DistancecombinationClass, dcs: distance_combination.DistancecombinationsettingClass) -> "FilterClass":
		tf = dcs.getTimeFilter()

		f = FilterClass(
			competition_id=c.getId(),
			distance_id=dc.getId(),
			venue=c.getVenueCode(),
			discipline=c.getDiscipline(),
			clubs=dcs.getClubCodes(),
	#_flags: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	#_transponder: bool|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
	#_validLicense: datetime.datetime|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(datetime.datetime)))
			categories=dc.getCategoryFilter(),
			homeVenues=dcs.getHomeVenueFilter(),
			invitees=dcs.getInvitees(),
			time_filter=tf)
		return f

	# @staticmethod
	# def createFilter(competition: classes.CompetitionClass, combination: distance_combination.DistancecombinationClass, settings: distance_combination.DistancecombinationsettingClass) -> "FilterClass":
 #
	# 	venue: str = competition.getVenueCode()
	# 	discipline: competition.getDiscipline()
	# 	clubs: tuple[int, ...]|None = settings.getClubCodes()
	# 	flags: int|None = None
	# 	transponder: bool|None = None
	# 	validLicense: datetime|None = None
	# 	categories: categories.CategoryFilterClass|None = combination.getCategoryFilter()
	# 	_homeVenues: tuple[str, ...]|None = None
	# 	_invitees = settings.getInvitees()
 #
	# 	FilterClass(
