#!/bin/python

import typing
import typeguard
import asyncio
import logging
import uuid

import websocketframework.websocket as websocket
import competitionnotify.classes.searchresults as searchresults
import competitionnotify.classes.time as time
import competitionnotify.classes.skater as skater
import competitionnotify.classes.distance as distance
import competitionnotify.classes.result as result
import competitionnotify.providers.results as results

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ResultsVantage(results.ResultsInterface, websocket.WebsocketInterface):
	def __init__(self):
		return None

	def getNameCode(self) -> str:
		return "vantage"

	def searchSkater(self, person: skater.PersonNameClass, category: categories.CategoryClass) -> list[searchresults.SearchResultsClass]:
		raise NotImplementedError

	def convertNumber2SkaterId(self, number: str|int) -> skater.PersonNameClass:
		raise NotImplementedError

	def getBests(self, skater_id, distance = -1, season: int = -1) -> result.BestTimesClass:
		raise NotImplementedError

	def getAllResults(self, skater_id, distance: distance.DistanceValueClass, season_start: int, season_end: int) -> list[time.TimeClass]:
		raise NotImplementedError

	def getCompetitionList(self, skater_id, season: int) -> list[object]:
		raise NotImplementedError

	def getSkaterIdType(self) -> type:
		return type(uuid.UUID)

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "vantage"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count),
			)

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True