#!/usr/bin/python
from typing import Any, TypeVar, Literal, TYPE_CHECKING
import dataclasses
from dataclasses import dataclass
from collections.abc import Sequence
import aiohttp
import asyncio
import datetime
import traceback

if TYPE_CHECKING:
	from _typeshed import DataclassInstance

Distances = Literal[100, 300, 500, 700, 1000, 1500, 3000, 5000, 10000]

@dataclass(frozen=True, kw_only=True)
class TimeClass:
	distance: int
	time: datetime.time
	date: datetime.date
	location: str
	name: str = str()
	link: str = str()

@dataclass(frozen=True, kw_only=True)
class BestTimesClass:
	skater: int
	season: int = -1
	records: list[TimeClass]

@dataclass(frozen=True, kw_only=True)
class ResultsClass:
	skater: int
	season: int
	distance: int
	results: list[TimeClass]

@dataclass(frozen=True, kw_only=True)
class CompetitionClass:
	id: int
	name: str
	startdate: datetime.date
	enddate: datetime.date
	link: str

@dataclass(frozen=True, kw_only=True)
class CompetitionsClass:
	skater: int
	season: int
	competitions: list[CompetitionClass]

@dataclass(frozen=True, kw_only=True)
class NameClass:
	id: int
	familyname: str
	givenname: str
	country: str
	gender: str
	category: str = str()

	def getFullName(self) -> str:
		return str(self.givenname + " " + self.familyname)

def sanitize(fields: tuple[dataclasses.Field, ...], d: dict[str, Any]) -> dict[str, Any]|None:
	e={}
	for f in fields:
		if f.name in d:
			e[f.name] = d[f.name]
		elif f.default == dataclasses.MISSING:
			print("Error, no value for " + str(f.name))
			return None
	return e

#U = TypeVar('U', bound=DataclassInstance) # Declare type variable "U"
U = TypeVar('U') # Declare type variable "U"

def class_factory(d: dict[str, Any], c: U) -> U|None:
	e = sanitize(dataclasses.fields(c), d)
	if e is None:
		return None
	return c(**e)

class SpeedSkatingResults:
	@dataclass(frozen=True, kw_only=True)
	class apiClass:
		base_url: str
		parameters: list[str]

	_api_base: str = "https://speedskatingresults.com/api/"
	_api_calls: dict[str, apiClass] = {
		"skater_id": apiClass(base_url="/skater_lookup.php", parameters=["familyname", "givenname", "country", "gender"]),
		"competition_list": apiClass(base_url="/skater_competitions.php", parameters=["skater", "season"]),
		"personal_records": apiClass(base_url="/personal_records.php", parameters=["skater", "distance"]),
		"season_bests": apiClass(base_url="/season_bests.php", parameters=["skater", "distance", "start"]),
		"distance_results": apiClass(base_url="/skater_results.php", parameters=["skater", "distance", "season"]),
		}

	@staticmethod
	def construct_url(key: str, parameters: dict[str, Any], type: str = "json") -> str:
		api = SpeedSkatingResults._api_calls.get(key, None)
		if api is not None:
			pp: list[str] = []
			for p in api.parameters:
				if p in parameters and parameters[p] is not None:
					pp.append(p + "=" + str(parameters[p]))
			url: str = SpeedSkatingResults._api_base + type + api.base_url + "?" + "&".join(pp)
			return url
		return str()

	@staticmethod
	async def _apiSkaterId(session: aiohttp.ClientSession, name: dict[str, str]) -> type[NameClass]:
		url = SpeedSkatingResults.construct_url("skater_id", name)
		async with session.get(url) as response:
			result = await response.json()
			skaters = result.get('skaters', None)
			if len(skaters) == 1:
				res = class_factory(skaters[0], NameClass)
				if res is not None:
					return res
			else:
				raise ValueError('Found ' + str(len(skaters)) + ' skaters that meet the search criteria')
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiPersonalRecord(session: aiohttp.ClientSession, skater: int, distance: Distances|None) -> type[BestTimesClass]:
		url = SpeedSkatingResults.construct_url("personal_records", {'skater': skater, 'distance': distance})

		async with session.get(url) as response:
			result = await response.json()
			records = result.get('records', None)
			if records is not None:
				r = []
				for record in records:
					t = class_factory(record, TimeClass)
					r.append(t)
				result['records'] = r
				res = class_factory(result, BestTimesClass)
				if res is not None:
					return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiSeasonBests(session: aiohttp.ClientSession, skater: int, distance: Distances|None = None, start: int|None = None) -> type[BestTimesClass]:
		url = SpeedSkatingResults.construct_url("season_bests", {'skater': skater, 'distance': distance, 'start': start})

		async with session.get(url) as response:
			result = await response.json()
			seasons = result.get('seasons', None)
			if seasons is not None:
				season = seasons[0].get('start', None)
				if season is not None:
					result['season'] = season
				records = seasons[0].get('records', None)
				if records is not None:
					r = []
					for record in records:
						t = class_factory(record, TimeClass)
						r.append(t)
					result['records'] = r
					res = class_factory(result, BestTimesClass)
					if res is not None:
						return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def _apiCompetitionList(session: aiohttp.ClientSession, skater: int, start: int|None = None) -> type[CompetitionsClass]:
		url = SpeedSkatingResults.construct_url("competition_list", {'skater': skater, 'season': start})

		async with session.get(url) as response:
			result = await response.json()

			season = result.get('season', None)
			if season is not None:
				result['season'] = season

			competitions = result.get('competitions', None)
			if competitions is not None:
				c = []
				for competition in competitions:
					t = class_factory(competition, CompetitionClass)
					c.append(t)
				result['competitions'] = c
				res = class_factory(result, CompetitionsClass)
				if res is not None:
					return res
		raise ValueError('Did not find the requested skater')


	@staticmethod
	async def _apiDistanceResult(session: aiohttp.ClientSession, skater: int, distance: Distances, season: int|None = None) -> type[ResultsClass]:
		url = SpeedSkatingResults.construct_url("distance_results", {'skater': skater, 'distance': distance, 'season': season})

		async with session.get(url) as response:
			result = await response.json()

			distance_results = result.get('results', None)
			distance = result.get('distance', None)
			if distance_results is not None:
				c = []
				for distance_result in distance_results:
					distance_result['distance'] = distance
					t = class_factory(distance_result, TimeClass)
					c.append(t)
				result['results'] = c
				res = class_factory(result, ResultsClass)
				if res is not None:
					return res
		raise ValueError('Did not find the requested skater')

	@staticmethod
	async def getId(names: list[dict[str, str]]|dict[str, str]) -> list[type[NameClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(names, list):
					tasks = [SpeedSkatingResults._apiSkaterId(session, skater_name) for skater_name in names]
				else:
					tasks = [SpeedSkatingResults._apiSkaterId(session, names)]
				results = await asyncio.gather(*tasks)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				traceback.print_exception(type(error), error, error.__traceback__)

		return results

	@staticmethod
	async def getPersonalRecord(skaters: list[int]|int, distance: Distances|None = None) -> list[type[BestTimesClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiPersonalRecord(session, skater, distance) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiPersonalRecord(session, skaters, distance)]
				results = await asyncio.gather(*tasks)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				traceback.print_exception(type(error), error, error.__traceback__)

		return results

	@staticmethod
	async def getSeasonBest(skaters: list[int]|int, distance: Distances|None = None, season: int|None = None) -> list[type[BestTimesClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiSeasonBests(session, skater, distance, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiSeasonBests(session, skaters, distance, season)]
				results = await asyncio.gather(*tasks)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				traceback.print_exception(type(error), error, error.__traceback__)

		return results

	@staticmethod
	async def getCompetitionList(skaters: list[int]|int, season: int|None = None) -> list[type[CompetitionsClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skater, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiCompetitionList(session, skaters, season)]
				results = await asyncio.gather(*tasks)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				traceback.print_exception(type(error), error, error.__traceback__)

		return results

	@staticmethod
	async def getDistanceResult(skaters: list[int]|int, distance: Distances, season: int|None = None) -> list[type[ResultsClass]]:
		results = []
		async with aiohttp.ClientSession() as session:
			try:
				if isinstance(skaters, list):
					tasks = [SpeedSkatingResults._apiDistanceResult(session, skater, distance, season) for skater in skaters]
				else:
					tasks = [SpeedSkatingResults._apiDistanceResult(session, skaters, distance, season)]
				results = await asyncio.gather(*tasks)
			except Exception as error:
				print('Caught this error: ' + repr(error))
				traceback.print_exception(type(error), error, error.__traceback__)

		return results

# async def main() -> None:
# 	#skaters_id = await SpeedSkatingResults.getId([{'familyname': "Goedhart", 'givenname': "Martijn", 'country': "NED", 'gender': 'm'}, {'familyname': "Goedhart", 'givenname': "Jos", 'country': "NED", 'gender': 'm'}])
# 	skaters_id = await SpeedSkatingResults.getId([{'familyname': "van den 1Bout", 'givenname': "Frans Nico", 'country': "NED", 'gender': 'm'}])
#
# 	print(skaters_id)
# 	for id in skaters_id:
# 		# print("get personal bests for " + id.givenname + " " + id.familyname + ":")
# 		# #print(type(id.familyname))
# 		# pb = await SpeedSkatingResults.getPersonalRecord(id.id)
# 		# print(pb)
# 		# print("get seasonal bests for " + id.givenname + " " + id.familyname + " for season 2014/2015:")
# 		# sb = await SpeedSkatingResults.getSeasonBest(id.id, None, "2013")
# 		# print(sb)
# 		# print("get competitions for " + id.givenname + " " + id.familyname + " for season 2013/2014:")
# 		# c = await SpeedSkatingResults.getCompetitionList(id.id, "2013")
# 		# print(c)
# 		print("get 1500m results for " + id.getFullName() + " for season 2013/2014:")
# 		d = await SpeedSkatingResults.getDistanceResult(id.id, 1500, 2008)
# 		print(d)
#
# 	return None
#
# if __name__ == '__main__':
# 	asyncio.run(main())