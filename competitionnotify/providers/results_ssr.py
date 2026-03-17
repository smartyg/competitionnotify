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
import competitionnotify.classes.categories as categories
import competitionnotify.classes.result as result
import competitionnotify.providers.results as results
import competitionnotify.speedskatingresults.speedskatingresults as speedskatingresults

logger = logging.getLogger(__name__)

skaterIdType = speedskatingresults.skaterIdType

#TODO: make class working
@typeguard.typechecked
class ResultsSSR(results.ResultsInterface, websocket.WebsocketInterface):
	def __init__(self):
		return None

	def getNameCode(self) -> str:
		return "vantage"

	async def searchSkater(self, person: skater.PersonNameClass, category: categories.CategoryClass) -> list[searchresults.SearchResultsClass]:
		search: dict[str, str] = {
			'familyname': person.getSurenameWithPrefix(),
			'givenname': person.getFirstName(),
			'country': 'NED',
		}

		if category.getGender() == 'H':
			search['gender'] = 'm'
		elif category.getGender() == 'D':
			search['gender'] = 'f'

		search_results = await speedskatingresults.SpeedSkatingResults.getId(search)
		if len(result_list) == 0:
			return {}
		else:
			return [e.asdict() for e in result_list if isinstance(e, result.NameClass)]
		raise NotImplementedError

	def getBests(self, skater_id, distance: int|None = None, season: int|None = None) -> result.BestTimesClass[skaterIdType]:
		if season is None:
			search_results = speedskatingresults.SpeedSkatingResults.getPersonalRecord(skater_id, distance)
		raise NotImplementedError

	def getAllResults(self, skater_id, distance: distance.DistanceValueClass, season_start: int, season_end: int) -> list[time.TimeClass]:
		raise NotImplementedError

	def getCompetitionList(self, skater_id, season: int) -> list[object]:
		raise NotImplementedError

	def getSkaterIdType(self) -> type:
		return type(skaterIdType)

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "ssr"

	def getCommands(self) -> websocket.CommandList:
		return (
			("search", self._cmd_search, "Lookup the skater id based on a name."),
			("personal_record", self._cmd_getPersonalRecord, "List the personal times record based on the given skater id."),
			#("season_best", self._cmd_getSeasonBest, "List the seasonal best times based on the given skater id."),
			#("competition_list", self._cmd_getCompetitionList, "List all the competitions based on the given skater id."),
			#("distance_result", self._cmd_getDistanceResult, "List all the result of a single distance based on the given skater id."),
			)

	async def _cmd_search(self, client_id: uuid.UUID, first_name: str|None = None, family_name: str|None = None, country: str|None = None, gender: str|None = None) -> list[dict]:
		valid: bool = False
		query: dict[str, str] = {}
		if first_name is not None:
			query["givenname"] = first_name
			valid = True
		if family_name is not None:
			query["familyname"] = family_name
			valid = True
		if country is not None:
			query["country"] = country
		if gender is not None:
			query["gender"] = gender

		if not valid:
			raise TypeError('At least first_name or family_name must be given.')

		result_list = await speedskatingresults.SpeedSkatingResults.getId(query)
		if len(result_list) == 0:
			return {}
		else:
			return [e.asdict() for e in result_list if isinstance(e, result.NameClass)]

	async def _cmd_getPersonalRecord(self, client_id: uuid.UUID, skater_id: skaterIdType, distance: int|None = None) -> dict:
		result_list = await speedskatingresults.SpeedSkatingResults.getPersonalRecord(skater_id, distance)
		if len(result_list) == 0:
			return {}
		elif len(result_list) == 1:
			return result_list[0].asdict()
		else:
			raise NotImplementedError

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True