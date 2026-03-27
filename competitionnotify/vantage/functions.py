#!/usr/bin/python

import typeguard
import logging
import datetime
import uuid

import competitionnotify.utils.cache as cache
import competitionnotify.utils.downloader as utils_downloader
import competitionnotify.classes.skater as skater
import competitionnotify.vantage.classes as vantage_classes

logger = logging.getLogger(__name__)

@typeguard.typechecked
@cache.cache(250, 86400, "/tmp/.cache-vantage-license.dat")
async def vantageGetLicense(number: str) -> skater.SkaterClass|None:
	url = 'https://inschrijven.schaatsen.nl/api/licenses/KNSB/SpeedSkating.LongTrack/' + number
	skater_license = await utils_downloader.downloader(url, skater.SkaterClass)
	if skater_license is None:
		return None
	else:
		return skater_license

@typeguard.typechecked
@cache.cache(250, 86400, "/tmp/.cache-vantage-search.dat")
async def vantageSearchId(skater_license: skater.SkaterClass, birth_date: datetime.date) -> vantage_classes.VantageSearchMultipleResultsClass|None:
	url = 'https://tijden-service.schaatsen.nl/api/SearchSkater?name=' + skater_license.getName()
	skater_search_results: tuple[vantage_classes.VantageSearchResultClass, ...] = await utils_downloader.downloaderTuple(url, vantage_classes.VantageSearchResultClass)
	logger.info(f'Found {len(skater_search_results)} matches for skater \'{skater_license.getName()}\'')
	matches: list[vantage_classes.VantageSearchResultClass] = []
	for s in skater_search_results:
		logger.debug (f'Test skater \'{s.getName()} ({s.getBirthYear()})\'')
		if s.match(skater_license.getFirstName(), skater_license.getSurename(), skater_license.getPrefix(), birth_date.year):
			matches.append(s)
	if not matches:
		return None
	else:
		return vantage_classes.VantageSearchMultipleResultsClass(results=tuple(matches))

@typeguard.typechecked
@cache.cache(250, 86400, "/tmp/.cache-vantage-results.dat")
async def vantageGetAllResults(ids: uuid.UUID|tuple[uuid.UUID, ...]) -> vantage_classes.VantageResultsClass:
	if isinstance(ids, tuple):
		result_list: list[vantage_classes.VantageResultsClass] = []
		for id in ids:
			url = 'https://tijden-service.schaatsen.nl/api/SkaterTimes?id=' + str(id)
			result_list.append(await utils_downloader.downloader(url, vantage_classes.VantageResultsClass))
		return vantage_classes.VantageResultsClass.combine(tuple(result_list))
	else:
		url = 'https://tijden-service.schaatsen.nl/api/SkaterTimes?id=' + str(ids)
		return await utils_downloader.downloader(url, vantage_classes.VantageResultsClass)
