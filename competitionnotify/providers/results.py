#!/bin/python

import typing
import typeguard
import logging
import abc
import collections.abc
import uuid
import time
import functools

import websocketframework.websocket as websocket

import competitionnotify.classes.skater as skater
import competitionnotify.classes.distance as distance
import competitionnotify.classes.time as class_time
import competitionnotify.classes.searchresults as searchresults
import competitionnotify.classes.result as result
import competitionnotify.classes.categories as categories
import competitionnotify.providers.skaters as skaters

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ResultsInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, 'getNameCode') and
				callable(subclass.getNameCode) and
				hasattr(subclass, 'searchSkater') and
				callable(subclass.searchSkater) and
				hasattr(subclass, 'convertNumber2SkaterId') and
				callable(subclass.convertNumber2SkaterId) and
				hasattr(subclass, 'getBests') and
				callable(subclass.getBests) and
				hasattr(subclass, 'getAllResults') and
				callable(subclass.getAllResults) and
				hasattr(subclass, 'getCompetitionList') and
				callable(subclass.getCompetitionList) and
				hasattr(subclass, 'getSkaterIdType') and
				callable(subclass.getSkaterIdType) or
				NotImplemented)

	@abc.abstractmethod
	def getNameCode(self) -> str:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def searchSkater(self, person: skater.PersonNameClass, category: categories.CategoryClass) -> list[searchresults.SearchResultsClass]:
		#full name
		#gender
		#Birth year
		#country
		"""Load in the data set"""
		raise NotImplementedError

	# @abc.abstractmethod
	# def convertNumber2SkaterId(self, number: str|int) -> skater.PersonNameClass:
	# 	"""Load in the data set"""
	# 	raise NotImplementedError

	@abc.abstractmethod
	def getBests(self, skater_id, distance: int|None = None, season: int|None = None) -> result.BestTimesClass:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getAllResults(self, skater_id, distance: distance.DistanceValueClass, season_start: int, season_end: int) -> list[class_time.TimeClass]:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getCompetitionList(self, skater_id, season: int) -> list[object]:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getSkaterIdType(self) -> type:
		"""Load in the data set"""
		raise NotImplementedError

@typeguard.typechecked
class ResultsMapping[T]:
	_type: type[T]
	_mapping: list[tuple[str, T]] = []

	def __init__(self, t: type):
		self._type=t

	def getSkaterById(self, i: str) -> T:
		for e in self._mapping:
			if e[0] == i:
				return e[1]
		raise KeyError(f'Id {i} is not found in the mapping.')

	def getIdBySkater(self, i: T) -> str:
		i = typeguard.check_type(i, self._type)
		for e in self._mapping:
			if e[1] == i:
				return e[0]
		raise KeyError(f'Id {i} is not found in the mapping.')

	def add(self, i1: str, i2: T) -> bool:
		i2 = typeguard.check_type(i2, self._type)
		for e in self._mapping:
			if e[0] == i1 or e[1] == i2:
				return False
		try:
			self._mapping.append((i1, i2))
			return True
		except:
			return False

	def hasId(self, i: str) -> bool:
		for e in self._mapping:
			if e[0] == i:
				return True
		return False

	def hasSkater(self, i: T) -> bool:
		i = typeguard.check_type(i, self._type)
		for e in self._mapping:
			if e[1] == i:
				return True
		return False

	def getSkaterIdType(self) -> type:
		return self._type

@typeguard.typechecked
class Results(websocket.WebsocketInterface):
	_providers: set[ResultsInterface] = set()
	#_skaters_provider: skaters.Skaters

	_mapping: dict[str, ResultsMapping[typing.Any]] = {}

	def __init__(self, providers: collections.abc.Sequence[ResultsInterface]):#, skaters_provider: skaters.Skaters):
		self._providers = set(providers)
		#self._skaters_provider = skaters

		for p in self._providers:
			mapping_type: type = p.getSkaterIdType()
			mapping: ResultsMapping[mapping_type] = ResultsMapping(mapping_type)
			self._mapping[p.getNameCode()] = mapping

	def getBests(self, s: collections.abc.Sequence[skater.SkaterClass], distance: int = -1, season: int = -1) -> dict[skater.SkaterClass, result.BestTimesClass]:
		res_dict: dict[skater.SkaterClass, result.BestTimesClass] = {}
		for p in s:
			search_result: tuple[str, type, typing.Any]|None = self._searchSkater(p, True)
			if search_result is None:
				continue
			provider_str = search_result[0]
			skater_id = search_result[2]
			res = self._getBests(provider_str, skater_id, distance, season)
			if res[0] < (int(time.time()) + 86400):
				self._getBests.cache_clear()
				res = self._getBests(provider_str, skater_id, distance, season)
			res_dict[p] = res[1]
		return res_dict

	@functools.lru_cache(maxsize=2048, typed=True)
	def _getBests(self, provider_str: str, skater_id: typing.Any, distance: int, season: int) -> tuple[int, result.BestTimesClass]:
		provider: ResultsInterface = typeguard.check_type(self._getProvider(provider_str), ResultsInterface)
		timestamp: int = int(time.time())
		res: result.BestTimesClass = provider.getBests(skater_id, distance, season)
		return (timestamp, res)

	def _hasProvider(self, provider_str: str) -> bool:
		for p in self._providers:
			if p.getNameCode() == provider_str:
				return True
		return False

	def _getProvider(self, provider_str: str) -> ResultsInterface|None:
		for p in self._providers:
			if p.getNameCode() == provider_str:
				return p
		return None

	def _getProviderMapping(self, provider_str: str) -> ResultsMapping[typing.Any]|None:
		return self._mapping.get(provider_str, None)

	def _searchSkater(self, s: skater.SkaterClass, prefer_cached: bool = True) -> tuple[str, type, typing.Any]|None:
		search: tuple[str, type, typing.Any]|None

		if prefer_cached:
			search = self._searchSkaterMapping(s)
			if search is not None:
				return search
		return self._searchSkaterProvider(s)

	def _searchSkaterMapping(self, s: skater.SkaterClass) -> tuple[str, type, typing.Any]|None:
		for provider_str in self._mapping:
			mapping = self._getProviderMapping(provider_str)
			if mapping is None:
				continue
			if mapping.hasId(s.getId()):
				skater_id_type = mapping.getSkaterIdType()
				skater_id: skater_id_type = mapping.getSkaterById(s.getId())
				return (provider_str, skater_id_type, skater_id)
		return None

	def _searchSkaterProvider(self, s: skater.SkaterClass) -> tuple[str, type, typing.Any]|None:
		for provider in self._providers:
			provider_str: str = provider.getNameCode()
			provider_skater_id_type: type = provider.getSkaterIdType()
			skater_id: tuple[bool, type, provider_skater_id_type] = provider.searchSkater(s._personName, s.getCategory())
			if skater_id[0]:
				mapping = typeguard.check_type(self._mapping.get(provider_str, None), ResultsMapping[typing.Any])
				mapping.add(s.getId(), skater_id[2])
				return (provider_str, provider_skater_id_type, skater_id[2])
			else:
				continue
		return None

	def getName(self) -> str:
		return "results"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count),
			)

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True