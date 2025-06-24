#!/bin/python

import typing
import typeguard
import aiohttp
import asyncio
import attrs
import json
import logging
import traceback
import uuid
from datetime import datetime, timezone

#from baseclass import BaseClass
#from classes import CompetitionClass, CompetitionClass_converter, DistancecombinationsClass, DistancecombinationsettingsClass

import competitionnotify.websocket as websocket
import competitionnotify.utils.utils as utils
import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.classes as dataclasses
import competitionnotify.task_manager as task_manager
import competitionnotify.providers.base.loadable_provider as loadable_provider
import competitionnotify.providers.venues as venues
import competitionnotify.providers.skaters as skaters
import competitionnotify.providers.base.result_provider_interface as result_provider_interface

logger = logging.getLogger(__name__)

U = typing.TypeVar('U', bound=type[attrs.AttrsInstance]) # Declare type variable "U"

@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionProcess:

	@attrs.define(frozen=True, kw_only=False, slots=False)
	class apiCall:
		_url: str = attrs.field(validator=attrs.validators.instance_of(str))
		_type: attrs.AttrsInstance = attrs.field()#validator=attrs.validators.instance_of(attrs.AttrsInstance))

		@_type.validator
		def _check_type(self, attribute, value):
			print("_check_type: subclasses:")
			print([cls.__name__ for cls in value.__subclasses__()])
			if not issubclass(value, (CompetitionClass, DistancecombinationsClass, DistancecombinationsettingsClass)): #attrs.AttrsInstance):
				raise ValueError("value (" + str(type(value)) + ") is not a subclass of attrs.AttrsInstance")

		def getUrl(self) -> str:
			return self._url

		def getClass(self) -> str:
			return self._type

	_competition: dataclasses.CompetitionClass = attrs.field(converter=dataclasses.CompetitionClass_converter, validator=attrs.validators.instance_of(dataclasses.CompetitionClass))

	async def load(self) -> None:
		pass

	def getId(self) -> uuid.UUID:
		return self._competition.getId()

	def getName(self) -> str:
		return self._competition.getName()

	def isOpen(self) -> bool:
		now = datetime.now(timezone.utc)
		return (self._competition.opens() < now and self._competition.closes() > now)

	def isOpenFuture(self) -> bool:
		now = datetime.now(timezone.utc)
		return (self._competition.opens() > now and self._competition.closes() > now)

	def isClosed(self) -> bool:
		now = datetime.now(timezone.utc)
		return (self._competition.closes() < now)

	def isTest(self) -> bool:
		return self._competition.isTest()

	# def filterSkaters(skaters: Skaters) -> list[SkaterClass]:
	# 	pass
 #
	# def generateMail(template: jinja2) -> str:
	# 	pass

	def getLinks(self) -> dict[str, str]:
		links = {
			'general': 'https://inschrijven.schaatsen.nl/',
			'subscription': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(self._competition.getId()) + '/inschrijven',
			'information': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(self._competition.getId()) + '/informatie',
			'participants': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(self._competition.getId()) + '/deelnemers'
		}
		return links

	def getApiCalls(self) -> dict[str, apiCall]:
		urls = {
			'competition': CompetitionProcess.apiCall('https://inschrijven.schaatsen.nl/api/competitions/' + str(self._competition.getId()), CompetitionClass),
			'distancecombinations': CompetitionProcess.apiCall('https://inschrijven.schaatsen.nl/api/competitions/' + str(self._competition.getId()) + '/distancecombinations', DistancecombinationsClass),
			'distancecombinationsettings': CompetitionProcess.apiCall('https://inschrijven.schaatsen.nl/api/competitions/' + str(self._competition.getId()) + '/settings/distancecombinations', DistancecombinationsettingsClass)
		}
		return urls


	@staticmethod
	async def apiDownload(url: str, c: U) -> U:
		async with aiohttp.ClientSession() as session:
			async with session.get(url) as response:
				logger.debug ("Download competition data file for competition ...")
				data = json.loads(await response.text())
				ret = None
				if not isinstance(data, dict):
					name = base.BaseClass.getFirstFieldName(c)
					if name is not None:
						ret = utils.class_factory({name: data}, c)
				else:
					ret = utils.class_factory(data, c)
				if ret is None:
					raise ValueError("failed to create and instance of type " + str(c.__name__) + " with data: " + str(data))
				return ret


	async def downloadCompetitionData_task(self) -> dict[str, asyncio.Task[typing.Any]]:
		ret: dict[str, asyncio.Task[typing.Any]] = {}

		for name, api in self.getApiCalls().items():
			coroutine = CompetitionProcess.apiDownload(api.getUrl(), api.getClass())
			ret[name] = asyncio.create_task(coroutine)
			ret[name].set_name("download " + str(self.getId()) + name)

		return ret

	async def waitDownloadTaskCompletion(self, name: str, task: asyncio.Task[typing.Any], c: U) -> U:
		while not task.done():
			await task

		return task.result()

	async def waitTillOpen(self) -> None:
		delta = self._competition.opens() - datetime.now(timezone.utc)
		wait = int(delta.total_seconds ()) + 1
		logger.debug ("(" + str(self.getId()) + "): wait for " + str(wait) + " seconds to start processing competition")
		await asyncio.sleep(wait)

	async def run (self, nowait:bool = False) -> bool:
		if not nowait:
			while datetime.now(timezone.utc) < self._competition.opens():
				await self.waitTillOpen()

		print("run competition process: " + self.getName())

		# Download the competition files
		download_task = await self.downloadCompetitionData_task()

		# Get record from processed competitions for this competition

		print("competition...")
		competition = await self.waitDownloadTaskCompletion('competition', download_task['competition'], CompetitionClass)
		print("distancecombinations...")
		distancecombinations = await self.waitDownloadTaskCompletion('distancecombinations', download_task['distancecombinations'], DistancecombinationsClass)
		print("distancecombinationsettings...")
		distancecombinationsettings = await self.waitDownloadTaskCompletion('distancecombinationsettings', download_task['distancecombinationsettings'], DistancecombinationsettingsClass)


		# Check if current settings have changed
		# if change only affects participants, send email to added participants
		# else send email to all participants (again)

		return True

@typeguard.typechecked
class SchaatsenDotNl(loadable_provider.LoadableProvider, websocket.WebsocketInterface):
	_venue_provider: venues.Venues
	_skaters_provider: skaters.Skaters
	_results_provider: set[result_provider_interface.ResultProviderInterface]

	_competitions: set[type[CompetitionProcess]] = set()

	def __init__(self, skaters: skaters.Skaters, venues: venues.Venues, results: typing.Sequence[typing.Any], processed_competitions: None, emails: None):
		self._competitions.clear()
		self._venue_provider = venues
		self._skaters_provider = skaters
		self._results_provider = set(results)

		super().__init__('https://inschrijven.schaatsen.nl/api/competitions', self._load_competitions)

	@staticmethod
	async def download() -> list[dict[str, typing.Any]]:
		logger.debug ("Download the new competition file")
		async with aiohttp.ClientSession() as session:
			async with session.get('https://inschrijven.schaatsen.nl/api/competitions') as response:
				logger.debug ("New competition file downloaded")
				return json.loads(await response.text())

	async def _load_competitions(self, json) -> None:
		# Clear the list of existing coroutines
		self._competitions.clear()

		# Loop over all the competitions and generate for each a CompetitionProcess
		for competition in json:
			c = utils.class_factory({'competition': competition}, CompetitionProcess)
			if c is not None:
				self._competitions.add(c)
		print("processed " + str(len(self._competitions)) + "/" + str(len(competitions)) + " competitions")

	def listOpen(self) -> set[type[CompetitionProcess]]:
		return {c for c in self._competitions if c.isOpen()}

	def listOpenFuture(self) -> set[type[CompetitionProcess]]:
		return {c for c in self._competitions if c.isOpenFuture()}

	def listClosed(self) -> set[type[CompetitionProcess]]:
		return {c for c in self._competitions if c.isClosed()}

	def listTest(self) -> set[type[CompetitionProcess]]:
		return {c for c in self._competitions if c.isTest()}

	def listNoTest(self) -> set[type[CompetitionProcess]]:
		return {c for c in self._competitions if not c.isTest()}

	def getCompetition(self, id: uuid.UUID) -> task_manager.CoroutineClass|None:
		for competition in self._competitions:
			if competition.getId() == id:
				return task_manager.CoroutineClass(coroutine=competition.run(True), name=competition.getName())
		return None

	async def getCompetitions(self, download: bool, include_open: bool = True, include_open_future: bool = True, include_closed: bool = False, include_test: bool = False) -> set[task_manager.CoroutineClass]:
		if download:
			await self.load()

		# Filter the list of competitions
		run_competitions = ((self.listOpen() if include_open else set()) |
							(self.listOpenFuture() if include_open_future else set()) |
							(self.listClosed() if include_closed else set())
						) & (self.listNoTest() if not include_test else self._competitions)

		# Generate a CoroutineClass object for each listed competition
		ret: set[task_manager.CoroutineClass] = set()
		for competition in run_competitions:
				ret.add(task_manager.CoroutineClass(coroutine=competition.run(), name=competition.getName()))

		# Return the list of competition coroutines
		return ret

	def getName(self) -> str:
		return "competitions"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count),
			)

	def _cmd_count(self) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True
