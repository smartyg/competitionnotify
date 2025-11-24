#!/bin/python

import abc
import typeguard
import logging

import competitionnotify.classes.skater as skater
import competitionnotify.classes.distance as distance
import competitionnotify.classes.time as time
import competitionnotify.classes.searchresults as searchresults

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ResultProviderInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, 'get') and
				callable(subclass.get) and
				hasattr(subclass, 'search_skater') and
				callable(subclass.search_skater) and
				hasattr(subclass, 'convertNumber2SkaterId') and
				callable(subclass.convertNumber2SkaterId) and
				hasattr(subclass, 'getBests') and
				callable(subclass.getBests) and
				hasattr(subclass, 'getAllResults') and
				callable(subclass.getAllResults) and
				hasattr(subclass, 'getCompetitionList') and
				callable(subclass.getCompetitionList) or
				NotImplemented)

	@abc.abstractmethod
	def get(self) -> str:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def search_skater(self, first_name: str|None = None, last_name: str|None = None) -> list[searchresults.SearchResultsClass]:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def convertNumber2SkaterId(self, number: str|int) -> skater.PersonNameClass:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getBests(self, skater_id, distance, season: int) -> list[time.TimeClass]:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getAllResults(self, skater_id, distance: distance.DistanceValueClass, season_start: int, season_end: int) -> list[time.TimeClass]:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getCompetitionList(self, skater_id, season: int) -> list[object]:
		"""Load in the data set"""
		raise NotImplementedError
