#!/bin/python

import typing
import attrs
import logging
from datetime import datetime

import competitionnotify.utils.utils as utils
import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.dataclasses.categories as categories
import competitionnotify.dataclasses.venue as venue
import competitionnotify.dataclasses.skater as skater

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class FilterClass(base.BaseClass):
	_venue: venue.VenueRefClass
	_discipline: discipline.DisciplineClass
	_clubs: list[int]|int|None = None
	_flags: int|None = None
	_transponder: bool|None = None
	_validLicense: datetime|None = None
	_categories: categories.CategoryFilterClass|None = None

	def _testVenue(self, skater: skater.SkaterClass) -> bool:
		mail_options = skater.getOptions()
		home_venue = skater.getHomeVenue()
		if mail_options.homeVenue() and self._venue == home_venue:
			return True
		if self._venue in mail_options.getVenues():
			return True
		return False

	def _testDiscipline(self, disciplines: list[discipline.DisciplineClass]) -> bool:
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

	def _testTransponder(self, transponders: list[str|None]) -> bool:
		if self._transponder is None:
			return True
		elif self._transponder:
			for t in transponders:
				if t is not None:
					if len(t) > 0:
						return True
			return False
		else:
			return True

	def _testLicense(self, skater: skater.SkaterClass) -> bool:
		if self._validLicense is not None:
			return skater.isLicenseValid(self._validLicense)
		else:
			return True

	def _testCategorie(self, category: categories.CategoryClass) -> bool:
		if self._categories is None:
			return True
		else:
			return self._categories(category)

	def testSkater(skater: skater.SkaterClass) -> bool:
		# Get mailOptions
		mail_options = skater.getOptions()

		return self._testCategorie(skater.getCategory()) and \
			self._testVenue(skater) and \
			self._testDiscipline(mail_options.getDisciplines()) and \
			self._testClub(skater.getClub()) and \
			self._testFlags(skater.getFlags()) and \
			self._testTransponder(skater.getTranspoders()) and \
			self._testLicense(skater)
