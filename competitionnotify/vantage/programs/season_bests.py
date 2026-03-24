#!/usr/bin/python

import typeguard
import asyncio
import logging
import uuid
import csv
import aiohttp
import datetime

import competitionnotify.utils.utils as utils
import competitionnotify.classes.distance as distance
import competitionnotify.classes.categories as categories
import competitionnotify.classes.result as result
import competitionnotify.vantage.functions as vantage_functions

logger = logging.getLogger(__name__)

async def getSkaterRecords(skater_id: uuid.UUID, season: int) -> list[str|int]:
	results = await vantage_functions.vantageGetAllResults(skater_id)

	result_list: list[str|int] = []
	result_list.append(results.countRaces(season))
	result_list.append(results.countDays(season))

	distances = distance.DistanceValueClass.allDistances()
	season_best_time: dict[int, result.ResultClass|None] = {}
	personal_best_time: dict[int, result.ResultClass|None] = {}
	is_personal_best_time: dict[int, bool] = {}

	for distance_value in distances:
		season_best = results.getSeasonBest(distance_value, season)
		personal_best = results.getPersonalBest(distance_value)
		season_best_time[distance_value] = "" if season_best is None else str(season_best.getTime())
		personal_best_time[distance_value] = "" if personal_best is None else str(personal_best.getTime())
		is_personal_best_time[distance_value] = 1 if season_best is not None and season_best.getTime() == personal_best.getTime() else 0

	result_list.extend(season_best_time.values())
	result_list.extend(personal_best_time.values())
	result_list.extend(is_personal_best_time.values())

	return result_list

async def runner() -> None:
	skater_numbers: list[tuple[str, str]] = [
	]

	season = 2025

	print("step 1 ...")
	skaters: list[tuple[skater.SkaterClass|None, datetime.date]] = [(await vantage_functions.vantageGetLicense(s[0]), datetime.datetime.strptime(s[1], "%d-%m-%Y").date()) for s in skater_numbers]
	print(skaters)

	print("step 2 ...")
	skater_ids: list[tuple[vantage_classes.VantageSearchResultClass|None, skater.SkaterClass, categories.CategoryClass]] = [(await vantage_functions.vantageSearchId(s[0], s[1]), s[0], categories.CategoryClass.getCategoryByDate(s[0].getCategory().isMale(), s[1], season)) for s in skaters if s[0] is not None]
	print(skater_ids)

	print("step 3 ...")
	result_list: list[list[str|int]] = [[s[1].getName(), s[2]] + await getSkaterRecords(s[0].getId(), season) if s[0] is not None else [s[1].getName(), s[2]] for s in skater_ids]
	print(result_list)

	filename = "season_results.csv"
	with open(filename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile,delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)        # Create writer object
		csvwriter.writerows(result_list)

if __name__ == '__main__':
	logging.basicConfig(filename='test.log', level=logging.DEBUG, filemode='w')
	asyncio.run(runner())