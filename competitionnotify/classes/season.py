#!/bin/python

import typing
import typeguard
import attrs
import logging
import datetime
import re

import competitionnotify.classes.base as base
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

def _season_validator(instance, attribute, value):
	if value < 1950 or value > 9999:
		raise ValueError(f'Value of {value} does not repesend a valid season.')

@attrs.define(frozen=True, kw_only=False, slots=False, hash=True, str=False, eq=False, order=False)
class SeasonClass(base.BaseClass):
	_season: int = base.BaseClass.serializable(True, validator=[attrs.validators.instance_of(int), _season_validator])

	def getSeasonStart(self) -> datetime.date:
		return datetime.date(self._season, 7, 1)

	def getSeasonEnd(self) -> datetime.date:
		return datetime.date(self._season + 1, 6, 30)

	def getSeason(self) -> int:
		return self._season

	def isInSeason(self, date: datetime.date) -> bool:
		return date >= self.getSeasonStart() and date <= self.getSeasonEnd()

	def equal(self, o: "DistanceClass") -> bool:
		return self._season == o._season

	def __str__(self) -> str:
		return str(self._season) + "/" + str(self._season + 1)

	def __repr__(self) -> str:
		return self.__str__()

	@staticmethod
	def getCurrentSeason() -> "SeasonClass":
		current_date = datetime.datetime.now()
		current_season = current_date.year
		if current_date.month < 7:
			current_season -= 1
		return SeasonClass(season=current_season)

	@staticmethod
	def getSeasonFromString(text: str) -> "SeasonClass":
		try:
			m = re.fullmatch('([0-9]{4})/([0-9]{4})', text)
			if m is not None:
				start: int = int(m.group(1))
				end: int = int(m.group(2))
				if end == start + 1:
					return SeasonClass(season=int(m.group(1)))
			raise ValueError('')
		except:
			raise ValueError(f'Text `{text}` is not a valid season indication')

@typeguard.typechecked
def SeasonClass_convertor_except(data: int|str|SeasonClass) -> SeasonClass:
	if isinstance(data, SeasonClass):
		return data
	if isinstance(data, int):
		return SeasonClass(season=data)
	else:
		return SeasonClass.getSeasonFromString(data)
