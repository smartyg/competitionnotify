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

import competitionnotify.classes.base as base
import competitionnotify.classes.distance as distance
import competitionnotify.classes.result as result
#import competitionnotify.speedskatingresults.classes as classes
import competitionnotify.utils.utils as utils

skaterIdType = int

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
	async def _apiSkaterId(session: aiohttp.ClientSession, name: dict[str, str]) -> result.NameClass[skaterIdType]:
		url = SpeedSkatingResults.construct_url("skater_id", name)
		async with session.get(url) as response:
			response_dict = await response.json()
			print(response_dict)
			skaters = response_dict.get('skaters', None)
			if len(skaters) == 1:
				c = ('H' if skaters[0]['gender'] == 'm' else 'D') + str(skaters[0]['category'])
				skaters[0]['category'] = c
				skaters[0]['skater'] = skaters[0]['id']
				res: result.NameClass
				try:
					print(skaters[0])
					res = utils.class_factory(skaters[0], result.NameClass, skaterIdType)
					print(res)
				except Exception as error:
					traceback.print_exc()
					print(f'Caught this error: {error!r}.')
				if res is not None:
					return res
			else:
				raise ValueError('Found ' + str(len(skaters)) + ' skaters that meet the search criteria')
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiPersonalRecord(session: aiohttp.ClientSession, s: int|result.NameClass[skaterIdType], d: int|None) -> result.BestTimesClass[skaterIdType]:
		if isinstance(s, result.NameClass):
			skater_id = s.getId()
		else:
			skater_id = s

		url = SpeedSkatingResults.construct_url("personal_records", {'skater': skater_id, 'distance': d})

		async with session.get(url) as response:
			response_dict: dict = await response.json()
			res = utils.class_factory(response_dict, result.BestTimesClass, skaterIdType)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiSeasonBests(session: aiohttp.ClientSession, skater: int|result.NameClass[skaterIdType], distance: int|None = None, start: int|None = None, end: int|None = None) -> result.BestTimesClass[skaterIdType]:
		if isinstance(skater, result.NameClass):
			skater_id = skater.getId()
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("season_bests", {'skater': skater_id, 'distance': distance, 'start': start, 'end': end})

		async with session.get(url) as response:
			response_dict: dict = await response.json()
			seasons = response_dict.get('seasons', None)
			#TODO: make working when looking for multiple seasons
			if seasons is not None and len(seasons) == 1:
				response_dict['season'] = seasons[0].get('start', None)
				response_dict['records'] = seasons[0].get('records', None)

			res = utils.class_factory(response_dict, result.BestTimesClass[skaterIdType])
			if res is not None:
				return res
		raise ValueError('No season best found for this skater (id=' + str(skater_id) + ')')

	@staticmethod
	async def _apiCompetitionList(session: aiohttp.ClientSession, skater: int|result.NameClass[skaterIdType], start: int|None = None) -> result.CompetitionsClass:
		if isinstance(skater, result.NameClass):
			skater_id = skater.getId()
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("competition_list", {'skater': skater_id, 'season': start})

		async with session.get(url) as response:
			response_dict: dict = await response.json()
			res = utils.class_factory(response_dict, result.CompetitionsClass)
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')


	@staticmethod
	async def _apiDistanceResult(session: aiohttp.ClientSession, skater: int|result.NameClass[skaterIdType], distance: int, season: int|None = None) -> result.ResultsClass[skaterIdType]:
		if isinstance(skater, result.NameClass):
			skater_id = skater.getId()
		else:
			skater_id = skater

		url = SpeedSkatingResults.construct_url("distance_results", {'skater': skater_id, 'distance': distance, 'season': season})

		async with session.get(url) as response:
			response_dict: dict = await response.json()

			if "results" in response_dict:
				for r in response_dict["results"]:
					r['distance'] = response_dict['distance']
			res = utils.class_factory(response_dict, result.ResultsClass[skaterIdType])
			if res is not None:
				return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def getId(names: list[dict[str, str]]|dict[str, str]) -> list[result.NameClass[skaterIdType]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(names, list):
					tasks = [SpeedSkatingResults._apiSkaterId(session, skater_name) for skater_name in names]
				else:
					tasks = [SpeedSkatingResults._apiSkaterId(session, names)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print(f'Caught this error: {error!r}.')
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getPersonalRecord(skaters: list[int]|list[result.NameClass[skaterIdType]]|int|result.NameClass[skaterIdType], d: distance.DistanceValueClass|int|None = None) -> list[result.BestTimesClass[skaterIdType]]:
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
				print(f'Caught this error: {error!r}.')
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getSeasonBest(skaters: list[int]|list[result.NameClass[skaterIdType]]|int|result.NameClass[skaterIdType], d: distance.DistanceValueClass|int|None = None, start: int|None = None, end: int|None = None) -> list[result.BestTimesClass[skaterIdType]]:
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
				print(f'Caught this error: {error!r}.')
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getCompetitionList(skaters: list[int]|list[result.NameClass[skaterIdType]]|int|result.NameClass[skaterIdType], season: int|None = None) -> list[result.CompetitionsClass]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skater, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skaters, season)]
				results = await asyncio.gather(*tasks, return_exceptions=True)
			except Exception as error:
				print(f'Caught this error: {error!r}.')
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]

	@staticmethod
	async def getDistanceResult(skaters: list[int]|list[result.NameClass[skaterIdType]]|int|result.NameClass[skaterIdType], d: distance.DistanceValueClass|int, season: int|None = None) -> list[result.ResultsClass[skaterIdType]]:
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
				print(f'Caught this error: {error!r}.')
				#traceback.print_exception(type(error), error, error.__traceback__)

		return [r for r in results if not isinstance(r, BaseException)]