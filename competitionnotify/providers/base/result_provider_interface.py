#!/bin/python

import abc
import logging

logger = logging.getLogger(__name__)

class ResultProviderInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, 'get') and
				callable(subclass.get) or
				NotImplemented)

	@abc.abstractmethod
	def get(self) -> str:
		"""Load in the data set"""
		raise NotImplementedError

	def search_skater(self,...) -> list[SearchResultsClass]:

	def convertNumber2SkaterId(self, number: str|int) -> Nameclass:

	def getBests(self, skater_id, distance, season) -> list[TimeClass]:

	def getAllResults(self, skater_id, distance, season_start, season_end) -> list[TimeClass]:

	def getCompetitionList((self, skater_id, season) -> list[]:
