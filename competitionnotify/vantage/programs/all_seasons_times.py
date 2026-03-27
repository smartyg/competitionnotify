#!/usr/bin/python

import typeguard
import asyncio
import logging
import uuid
import csv
import aiohttp
import datetime

import competitionnotify.utils.utils as utils
import competitionnotify.classes.season as season
import competitionnotify.classes.distance as distance
import competitionnotify.classes.categories as categories
import competitionnotify.classes.skater as skater
import competitionnotify.classes.result as result
import competitionnotify.vantage.functions as vantage_functions
import competitionnotify.vantage.classes as vantage_classes

logger = logging.getLogger(__name__)

@typeguard.typechecked
async def getSkaterRecords(skater_id: uuid.UUID|tuple[uuid.UUID, ...], request_season: season.SeasonClass) -> list[str|int]:
	results: vantage_classes.VantageResultsClass = await vantage_functions.vantageGetAllResults(skater_id)

	result_list: list[str|int] = []
	distances = distance.DistanceValueClass.allDistances()
	season_best_time: dict[int, result.ResultClass|None] = {}
	is_personal_best_time: dict[int, bool] = {}

	for distance_value in distances:
		season_best = results.getSeasonBest(distance_value, request_season)
		personal_best = results.getPersonalBest(distance_value, request_season)
		season_best_time[distance_value] = "" if season_best is None else str(season_best.getTime())
		is_personal_best_time[distance_value] = 1 if season_best is not None and season_best.getTime() == personal_best.getTime() else 0

	result_list.extend(season_best_time.values())
	result_list.extend(is_personal_best_time.values())

	return result_list

@typeguard.typechecked
async def runner() -> None:
	skater_numbers: list[tuple[str, str]] = [
	]

	print("step 1 ...")
	skaters: list[tuple[skater.SkaterClass|None, datetime.date]] = [(await vantage_functions.vantageGetLicense(s[0]), datetime.datetime.strptime(s[1], "%d-%m-%Y").date()) for s in skater_numbers]
	print(skaters)

	print("step 2 ...")
	skater_ids: list[tuple[vantage_classes.VantageSearchMultipleResultsClass|None, skater.SkaterClass, datetime.date]] = [(await vantage_functions.vantageSearchId(s[0], s[1]), s[0], s[1]) for s in skaters if s[0] is not None]
	print(skater_ids)

	print("step 3 ...")
	result_list: list[list[str|int]] = []
	for request_season_int in range(1999, 2026):
		request_season = season.SeasonClass(request_season_int)
		result_list.append([[s[1].getName(), categories.CategoryClass.getCategoryByDate(s[1].getCategory().isMale(), s[2], request_season)] + await getSkaterRecords(s[0].getAllIds(), request_season) for s in skater_ids if s[0] is not None])
	print(result_list)

	filename = "season_results-test.csv"
	with open(filename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile,delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)        # Create writer object
		csvwriter.writerows(result_list)

if __name__ == '__main__':
	logging.basicConfig(filename='test.log', level=logging.DEBUG, filemode='w')
	asyncio.run(runner())