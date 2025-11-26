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
import datetime

import taskmanager.taskmanager as task_manager
import websocketframework.websocket as websocket
import competitionnotify.utils.utils as utils
import competitionnotify.classes.base as base
import competitionnotify.classes.competition as competition
import competitionnotify.classes.distance_combination as distance_combination
import competitionnotify.classes.skater as skater
import competitionnotify.classes.result as result
import competitionnotify.classes.filter as filter
import competitionnotify.providers.base.loadable_provider as loadable_provider
import competitionnotify.providers.venues as venues
import competitionnotify.providers.skaters as skaters
import competitionnotify.providers.base.result_provider_interface as result_provider_interface
import competitionnotify.providers.emails as emails
import competitionnotify.providers.processed_competitions as processed_competitions

logger = logging.getLogger(__name__)

U = typing.TypeVar('U', bound=attrs.AttrsInstance) # Declare type variable "U"

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class CompetitionProcess:

	@attrs.define(frozen=True, kw_only=False, slots=False)
	class apiCall:
		_url: str = attrs.field(validator=attrs.validators.instance_of(str))
		_type: type = attrs.field(validator=attrs.validators.instance_of(type))

		@_type.validator
		def _check_type(self, attribute, value):
			if utils.testAttrsClass(value):
				return True
			raise ValueError("value (" + str(type(value)) + ") is not a subclass of attrs.AttrsInstance")

		def getUrl(self) -> str:
			return self._url

		def getClass(self) -> type: #attrs.AttrsInstance:
			return self._type

	_competition: competition.CompetitionClass = attrs.field(converter=competition.CompetitionClass_converter, validator=attrs.validators.instance_of(competition.CompetitionClass)) # type: ignore [misc]

	_venue_provider: venues.Venues = attrs.field(validator=attrs.validators.instance_of(venues.Venues))
	_skaters_provider: skaters.Skaters = attrs.field(validator=attrs.validators.instance_of(skaters.Skaters))
	_results_provider: tuple[result_provider_interface.ResultProviderInterface, ...] = attrs.field(validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(result_provider_interface.ResultProviderInterface),
            iterable_validator=attrs.validators.instance_of(tuple)))
	_processed_competition_provider: processed_competitions.ProcessedCompetitions = attrs.field(validator=attrs.validators.instance_of(processed_competitions.ProcessedCompetitions))
	_email_provider: emails.Emails = attrs.field(validator=attrs.validators.instance_of(emails.Emails))

	async def load(self) -> None:
		pass

	def getId(self) -> uuid.UUID:
		return self._competition.getId()

	def getName(self) -> str:
		return self._competition.getName()

	def isOpen(self) -> bool:
		now = datetime.datetime.now(datetime.timezone.utc)
		return (self._competition.opens() < now and self._competition.closes() > now)

	def isOpenFuture(self) -> bool:
		now = datetime.datetime.now(datetime.timezone.utc)
		return (self._competition.opens() > now and self._competition.closes() > now)

	def isClosed(self) -> bool:
		now = datetime.datetime.now(datetime.timezone.utc)
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
			'competition': CompetitionProcess.apiCall('https://inschrijven.schaatsen.nl/api/competitions/' + str(self._competition.getId()), competition.CompetitionClass),
			'distancecombinations': CompetitionProcess.apiCall('https://inschrijven.schaatsen.nl/api/competitions/' + str(self._competition.getId()) + '/distancecombinations', distance_combination.DistancecombinationsClass),
			'distancecombinationsettings': CompetitionProcess.apiCall('https://inschrijven.schaatsen.nl/api/competitions/' + str(self._competition.getId()) + '/settings/distancecombinations', distance_combination.DistancecombinationsettingsClass)
		}
		return urls

	@staticmethod
	async def apiDownload(url: str, c: type[U]) -> U:
		async with aiohttp.ClientSession() as session:
			logger.debug ("download file: " + url + " ...")
			async with session.get(url) as response:
				#logger.debug ("Download competition data file for competition ...")
				data = json.loads(await response.text())
				logger.debug ("Download completed.")
				ret = None
				if not isinstance(data, dict):
					name = base.getFirstFieldName(c)
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

	async def waitDownloadTaskCompletion(self, name: str, task: asyncio.Task[typing.Any], c: type[U]) -> U:
		while not task.done():
			await task

		return task.result()

	async def waitTillOpen(self) -> None:
		delta = self._competition.opens() - datetime.datetime.now(datetime.timezone.utc)
		wait = int(delta.total_seconds ()) + 1
		logger.debug ("(" + str(self.getId()) + "): wait for " + str(wait) + " seconds to start processing competition")
		await asyncio.sleep(wait)

	async def run(self, nowait:bool = False) -> bool:
		if not nowait:
			while datetime.datetime.now(datetime.timezone.utc) < self._competition.opens():
				await self.waitTillOpen()

		logger.info("Run competition process: " + self.getName())

		# Download the competition files
		logger.debug("Create download tasks.")
		download_task = await self.downloadCompetitionData_task()

		logger.debug("download competition file ...")
		competition = await self.waitDownloadTaskCompletion('competition', download_task['competition'], competition.CompetitionClass)
		logger.debug("download distance combinations file ...")
		distancecombinations = await self.waitDownloadTaskCompletion('distancecombinations', download_task['distancecombinations'], distance_combination.DistancecombinationsClass)
		logger.debug("download distance combination settings file ...")
		distancecombinationsettings = await self.waitDownloadTaskCompletion('distancecombinationsettings', download_task['distancecombinationsettings'], distance_combination.DistancecombinationsettingsClass)

		first_run: bool = False
		filters_list: list[filter.FilterClass] = []
		logger.debug("compile list of filters.")
		for dc in distancecombinations.getTuple():
			for dcs in distancecombinationsettings.getTuple():
				if dc.getId() == dcs.getId():
					filters_list.append(filter.FilterClass.fromDistanceCombination(competition, dc, dcs))

		filters: tuple[filter.FilterClass, ...] = tuple(filters_list)
		if (len(filters)) == 0:
			logger.warning("For this competition there are no filter criteria present, nothing to do.")
			# There are no filters for this competition present, now we can not do anything with this, so stop.
			return True

		# get stored filter info
		stored_filters: tuple[filter.FilterClass, ...] = self._processed_competition_provider.getFilters(competition.getId())

		# If no filters were previously stored, we assume this is a first run
		if len(stored_filters) > 0:
			first_run = True

		# Now compare the stored filters with the new filters
		if filters == stored_filters:
			# Filters are the same, so assume nothing has changed worth notifing
			logger.info("Competition (" + self.getName() + ") has not been changed, nothing to do.")
			return True

		# There were either no filters stored (first run) or something significant has changed
		# Get a new list of all skaters that can attend this race
		recipients_step3: list[skater.SkaterClass] = []

		# Loop over all induvidual filters in the list of filters
		logger.debug("compile list of recipients.")
		for f in filters:
			# Filtering of the skaters that are allowed to attend happens in 2 steps:
			#   1 - Select skaters based on all filters, except time limits
			#   2 - from the remaining set, look up the personal bests and filter those
			recipients_step1: list[skater.SkaterClass] = self._skaters_provider.filterSkaters(f)
			if f.hasTimeFilter():
				recipients_step2: list[skater.SkaterClass] = []
				# Request the pbs for all remaining skaters
				pbs: dict[skater.SkaterClass, result.BestTimesClass] = self._results_provider.getBests(recipients_step2)
				for s in pbs:
					pb: result.BestTimesClass|None = pbs.get(s, None)
					if pb is not None:
						if f.testTime(pb):
							# Skaters personal best(s) are good enough, append to the list of this step
							recipients_step2.append(s)

				# Step 2 is done, extend the total list of recipients with it
				recipients_step3.extend(recipients_step2)
			else:
				# No step 2 was needed (no time limit), extend the total list of recipients with step 1
				recipients_step3.extend(recipients_step1)

		# Now create a set, which effectivaly filters out duplicates
		recipients: set[skater.SkaterClass] = set(recipients_step3)
		logger.debug("Competition (" + self.getName() + ") total length of recipients is: " + str(len(recipients)) + ".")
		
		# send_to_all is always True for a first run
		send_to_all: bool = first_run
		if len(stored_filters) != len(filters):
			# There is a change in number of distances (or this race was never proccessed), now send to all recipients (again)
			send_to_all = True
			return self._email_provider.generateEmail(competition.getId(), recipients, competition, distancecombinations, distancecombinationsettings, not first_run)
			
		if not send_to_all:
			old_recipients: set[skater.SkaterClass] = self._skaters_provider.getSkatersByNumber(self._email_provider.getRecipients(competition.getId()))
			added_recipients: set[skater.SkaterClass] = recipients.difference(old_recipients) # [r for r in recipients if r not in old_recipients]
			logger.debug("Competition (" + self.getName() + ") total length of recipients for the update is: " + str(len(added_recipients)) + ".")
			return self._email_provider.generateEmail(competition.getId(), added_recipients, competition, distancecombinations, distancecombinationsettings, True)

		logger.error("We should not reach this point.")
		return False

@typeguard.typechecked
class SchaatsenDotNl(loadable_provider.LoadableProvider, websocket.WebsocketInterface):
	_venue_provider: venues.Venues
	_skaters_provider: skaters.Skaters
	_results_provider: set[result_provider_interface.ResultProviderInterface]
	_processed_competition_provider: processed_competitions.ProcessedCompetitions
	_email_provider: emails.Emails

	_competitions: set[CompetitionProcess] = set()

	def __init__(self, skaters: skaters.Skaters, venues: venues.Venues, results: typing.Sequence[result_provider_interface.ResultProviderInterface], processed_competitions: processed_competitions.ProcessedCompetitions, emails: emails.Emails):
		self._competitions.clear()
		self._venue_provider = venues
		self._skaters_provider = skaters
		self._results_provider = set(results)
		self._processed_competition_provider = processed_competitions
		self._email_provider = emails

		super().__init__('https://inschrijven.schaatsen.nl/api/competitions', self._load_competitions)

	@staticmethod
	async def download() -> list[dict[str, typing.Any]]:
		logger.debug ("Download the new competition file")
		async with aiohttp.ClientSession() as session:
			async with session.get('https://inschrijven.schaatsen.nl/api/competitions') as response:
				logger.debug ("New competition file downloaded")
				return json.loads(await response.text())

	async def _load_competitions(self, json: list) -> None:
		# Clear the list of existing coroutines
		self._competitions.clear()

		# Loop over all the competitions and generate for each a CompetitionProcess
		for competition in json:
			c = utils.class_factory({'competition': competition, 'venue_provider': self._venue_provider, 'skaters_provider': self._skaters_provider, 'results_provider': self._results_provider, 'processed_competition_provider': self._processed_competition_provider, 'email_provider': self._email_provider}, CompetitionProcess)
			if c is not None:
				self._competitions.add(c)
		print("processed " + str(len(self._competitions)) + "/" + str(len(json)) + " competitions")

	def listOpen(self) -> set[CompetitionProcess]:
		return {c for c in self._competitions if c.isOpen()}

	def listOpenFuture(self) -> set[CompetitionProcess]:
		return {c for c in self._competitions if c.isOpenFuture()}

	def listClosed(self) -> set[CompetitionProcess]:
		return {c for c in self._competitions if c.isClosed()}

	def listTest(self) -> set[CompetitionProcess]:
		return {c for c in self._competitions if c.isTest()}

	def listNoTest(self) -> set[CompetitionProcess]:
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

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True
