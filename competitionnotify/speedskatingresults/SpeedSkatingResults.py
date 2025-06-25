#!/usr/bin/python
import typing
import typeguard
import attrs
import datetime
import dateutil.relativedelta
import asyncio
import aiohttp
import json

import traceback

import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.distance as distance
import competitionnotify.speedskatingresults.classes as classes
import competitionnotify.utils.utils as utils

@typeguard.typechecked
class SpeedSkatingResults:
	@attrs.define(frozen=True, kw_only=True, slots=False)
	class apiClass(base.BaseClass):
		_base_url: str = attrs.field(validator=attrs.validators.instance_of(str))
		_parameters: list[str] = attrs.field(validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(str),
            iterable_validator=attrs.validators.instance_of(list)))

	_api_base: str = "https://speedskatingresults.com/api/"
	_api_calls: dict[str, apiClass] = {
		"skater_id": apiClass(base_url="/skater_lookup.php", parameters=["familyname", "givenname", "country", "gender"]),
		"competition_list": apiClass(base_url="/skater_competitions.php", parameters=["skater", "season"]),
		"personal_records": apiClass(base_url="/personal_records.php", parameters=["skater", "distance"]),
		"season_bests": apiClass(base_url="/season_bests.php", parameters=["skater", "distance", "start", "end"]),
		"distance_results": apiClass(base_url="/skater_results.php", parameters=["skater", "distance", "season"]),
		}

	@staticmethod
	def construct_url(key: str, parameters: dict[str, typing.Any], type: str = "json") -> str:
		api = SpeedSkatingResults._api_calls.get(key, None)
		if api is not None:
			pp: list[str] = []
			for p in api._parameters:
				if p in parameters and parameters[p] is not None:
					pp.append(p + "=" + str(parameters[p]))
			url: str = SpeedSkatingResults._api_base + type + api._base_url + "?" + "&".join(pp)
			return url
		return str()

	@staticmethod
	async def _apiSkaterId(session: aiohttp.ClientSession, name: dict[str, str]) -> classes.NameClass:
		url = SpeedSkatingResults.construct_url("skater_id", name)
		async with session.get(url) as response:
			result = await response.json()
			skaters = result.get('skaters', None)
			if len(skaters) == 1:
				c = ('H' if skaters[0]['gender'] == 'm' else 'D') + str(skaters[0]['category'])
				skaters[0]['category'] = c
				res = utils.class_factory(skaters[0], classes.NameClass)
				if res is not None:
					return res
			else:
				raise ValueError('Found ' + str(len(skaters)) + ' skaters that meet the search criteria')
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiPersonalRecord(session: aiohttp.ClientSession, skater: int|classes.NameClass, distance: int|None) -> classes.BestTimesClass:
		if isinstance(skater, classes.NameClass):
			skater_id = skater._id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("personal_records", {'skater': skater_id, 'distance': distance})

		async with session.get(url) as response:
			result = await response.json()
			res = utils.class_factory(result, classes.BestTimesClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiSeasonBests(session: aiohttp.ClientSession, skater: int|classes.NameClass, distance: int|None = None, start: int|None = None, end: int|None = None) -> classes.BestTimesClass:
		if isinstance(skater, classes.NameClass):
			skater_id = skater._id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("season_bests", {'skater': skater_id, 'distance': distance, 'start': start, 'end': end})

		async with session.get(url) as response:
			result = await response.json()
			seasons = result.get('seasons', None)
			#TODO: make working when looking for multiple seasons
			if seasons is not None and len(seasons) == 1:
				result['season'] = seasons[0].get('start', None)
				result['records'] = seasons[0].get('records', None)

			res = utils.class_factory(result, classes.BestTimesClass)
			if res is not None:
				return res
		raise ValueError('No season best found for this skater (id=' + str(skater_id) + ')')

	@staticmethod
	async def _apiCompetitionList(session: aiohttp.ClientSession, skater: int|classes.NameClass, start: int|None = None) -> classes.CompetitionsClass:
		if isinstance(skater, classes.NameClass):
			skater_id = skater._id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("competition_list", {'skater': skater_id, 'season': start})

		async with session.get(url) as response:
			result = await response.json()
			res = utils.class_factory(result, classes.CompetitionsClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')


	@staticmethod
	async def _apiDistanceResult(session: aiohttp.ClientSession, skater: int|classes.NameClass, distance: int, season: int|None = None) -> classes.ResultsClass:
		if isinstance(skater, classes.NameClass):
			skater_id = skater._id
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("distance_results", {'skater': skater_id, 'distance': distance, 'season': season})

		async with session.get(url) as response:
			result = await response.json()

			if "results" in result:
				for r in result["results"]:
					r['distance'] = result['distance']
			res = utils.class_factory(result, classes.ResultsClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def getId(names: list[dict[str, str]]|dict[str, str]) -> list[classes.NameClass]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(names, list):
					tasks = [SpeedSkatingResults._apiSkaterId(session, skater_name) for skater_name in names]
				else:
					tasks = [SpeedSkatingResults._apiSkaterId(session, names)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getPersonalRecord(skaters: list[int]|list[classes.NameClass]|int|classes.NameClass, d: distance.DistanceValueClass|int|None = None) -> list[classes.BestTimesClass]:
		distance_value: int|None
		if isinstance(d, int):
			distance_value = distance.DistanceValueClass(distance=d).getValue()
		elif isinstance(d, distance.DistanceValueClass):
			distance_value = d.getValue()
		else:
			distance_value = d

		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiPersonalRecord(session, skater, distance_value) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiPersonalRecord(session, skaters, distance_value)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getSeasonBest(skaters: list[int]|list[classes.NameClass]|int|classes.NameClass, d: distance.DistanceValueClass|int|None = None, start: int|None = None, end: int|None = None) -> list[classes.BestTimesClass]:
		distance_value: int|None
		if isinstance(d, int):
			distance_value = distance.DistanceValueClass(distance=d).getValue()
		elif isinstance(d, distance.DistanceValueClass):
			distance_value = d.getValue()
		else:
			distance_value = d

		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiSeasonBests(session, skater, distance_value, start, end) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiSeasonBests(session, skaters, distance_value, start, end)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getCompetitionList(skaters: list[int]|list[classes.NameClass]|int|classes.NameClass, season: int|None = None) -> list[classes.CompetitionsClass]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skater, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skaters, season)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getDistanceResult(skaters: list[int]|list[classes.NameClass]|int|classes.NameClass, d: distance.DistanceValueClass|int, season: int|None = None) -> list[classes.ResultsClass]:
		distance_value: int
		if isinstance(d, int):
			distance_value = distance.DistanceValueClass(distance=d).getValue()
		elif isinstance(d, distance.DistanceValueClass):
			distance_value = d.getValue()
		else:
			distance_value = d

		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiDistanceResult(session, skater, distance_value, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiDistanceResult(session, skaters, distance_value, season)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]