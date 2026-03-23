#!/usr/bin/python

import typeguard
import logging
import datetime
import uuid

import competitionnotify.classes.skater as skater
import competitionnotify.vantage.classes as vantage_classes
import competitionnotify.vantage.cache as cache
import competitionnotify.utils.downloader as utils_downloader

logger = logging.getLogger(__name__)

vantage_result_cache: cache.Cache = cache.Cache(150, 43200)

@typeguard.typechecked
async def vantageGetLicense(number: str) -> skater.SkaterClass|None:
	url = 'https://inschrijven.schaatsen.nl/api/licenses/KNSB/SpeedSkating.LongTrack/' + number
	skater_license = await utils_downloader.downloader(url, skater.SkaterClass)
	if skater_license is None:
		return None
	else:
		return skater_license

@typeguard.typechecked
async def vantageSearchId(skater_license: skater.SkaterClass, birth_date: datetime.date) -> uuid.UUID|None:
  url = 'https://tijden-service.schaatsen.nl/api/SearchSkater?name=' + skater_license.getName()
  skater_search_results: tuple[vantage_classes.VantageSearchResultClass, ...] = await utils_downloader.downloaderTuple(url, vantage_classes.VantageSearchResultClass)
  logger.info(f'Found {len(skater_search_results)} matches for skater \'{skater_license.getName()}\'')
  for s in skater_search_results:
	  logger.debug (f'Test skater \'{s.getName()} ({s.getBirthYear()})\'')
	  if s.match(skater_license.getFirstName(), skater_license.getSurename(), skater_license.getPrefix(), birth_date.year):
		  return s.getId()
  return None

@typeguard.typechecked
async def vantageGetAllResults_internal(id: uuid.UUID) -> vantage_classes.VantageResultsClass:
	url = 'https://tijden-service.schaatsen.nl/api/SkaterTimes?id=' + str(id)
	return await utils_downloader.downloader(url, vantage_classes.VantageResultsClass)

@typeguard.typechecked
async def vantageGetAllResults(id: uuid.UUID) -> vantage_classes.VantageResultsClass:
	r: vantage_classes.VantageResultsClass|None = vantage_result_cache.get(id, 43200)
	if r is not None:
		logger.debug (f'Retrieve stored data for id `{id}`.')
		return r
	else:
		logger.debug (f'No stored data for id `{id}` availible.')
		r = await vantageGetAllResults_internal(id)
		vantage_result_cache.add(id, r)
		return r
