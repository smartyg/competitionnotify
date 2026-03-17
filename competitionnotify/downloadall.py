#!/bin/python

import typing
import typeguard
import aiohttp
import asyncio
import json
import logging

import competitionnotify.task_manager as task_manager

logger = logging.getLogger(__name__)

@typeguard.typechecked
class downloader:
	_url: str
	_filename: str

	def __init__(self, session, url: str, filename: str):
		self._session = session
		self._url = url
		self._filename = filename

	async def run(self) -> None:
		async with aiohttp.ClientSession() as session:
			async with session.get(self._url) as response:
				logger.debug ("New file downloaded")
				obj = json.loads(await response.text())
				with open(self._filename, "w") as f:
					json.dump(obj, f)

@typeguard.typechecked
async def runner() -> None:
	competitions: list[dict[str, typing.Any]]
	tasks: task_manager.TaskManager = task_manager.TaskManager()

	async with aiohttp.ClientSession() as session:
		async with session.get('https://inschrijven.schaatsen.nl/api/competitions') as response:
			logger.debug ("New competition file downloaded")
			competitions = json.loads(await response.text())

		logger.debug ("number of competitions: " + str(len(competitions)))

		for c in competitions:
			i = c['id']
			logger.debug ("process competition: " + i)
			urls: dict[str, str] = {
				i + '-competition.json': 'https://inschrijven.schaatsen.nl/api/competitions/' + i,
				i + '-distancecombinations.json': 'https://inschrijven.schaatsen.nl/api/competitions/' + i + '/distancecombinations',
				i + '-distancecombinationsettings.json': 'https://inschrijven.schaatsen.nl/api/competitions/' + i + '/settings/distancecombinations'
			}

			for f, u in urls.items():
				logger.debug ("start download of file: " + f + " (" + u + ")")
				download = downloader(session, u, f)
				await tasks.startProcess(download.run())
				await asyncio.sleep(0.1)

			await asyncio.sleep(0.5)

	await tasks.waitAllProcesses()

if __name__ == '__main__':
	logging.basicConfig(filename='test.log', level=logging.DEBUG)
	asyncio.run(runner())