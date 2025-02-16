#!/bin/python

import typing
from typing import Any
import json
from datetime import datetime, timedelta, timezone
import logging
import uuid
import aiohttp
import asyncio
import random
import jinja2
from DataStructure import ProcessedCompetitions, Emails, Skaters, EmailsSkaters, HomeVenues
import minify_html
import traceback

type DownloadFileType = dict[str, Any]

logger = logging.getLogger(__name__)

class Competitions:
	def __init__(self, minify_html: bool = True):
		self._competitions_tasks_to_process: set[asyncio.Task] = set()
		self._competitions: list[CompetitionsType] = list()

		self._competition_task: asyncio.Task #|None = None

		self._processed_competitions: ProcessedCompetitions = ProcessedCompetitions ('processed_competitions.h5')
		self._prepared_emails: Emails = Emails ('emails.h5')
		self._all_skaters: Skaters = Skaters ('skaters.h5')
		self._emails_skaters: EmailsSkaters = EmailsSkaters('emails_skaters.h5')
		self._venues: HomeVenues = HomeVenues('venues.h5')

		templateLoader = jinja2.FileSystemLoader(searchpath="./")
		templateEnv = jinja2.Environment(loader=templateLoader, enable_async=True)
		self._email_template = templateEnv.get_template("email_template")
		self._minify_html: bool = minify_html

	def isRunning(self) -> bool:
		if isinstance(self._competition_task, asyncio.Task):
			return not self._competition_task.done()
		else:
			return False

	async def run(self) -> asyncio.Task:
		logger.info ("Welcome at the competition notification service tool")
		self._competition_task = asyncio.create_task(self._downloadCompetitions())
		# await self._competition_task
		# logger.warning ("main download loop has ended, stop program")
		return self._competition_task

	async def _downloadCompetitions(self):
		try:
			logger.debug ("Start the main loop")
			while True:
				logger.debug ("Download the new competition file")
				async with aiohttp.ClientSession() as session:
					async with session.get('https://inschrijven.schaatsen.nl/api/competitions') as response:
						logger.debug ("New competition file downloaded")
						self._competitions = json.loads(await response.text())

						# We have a new competition file, now cancel all outstanding tasks
						await self._killCompetitionTasks()

						#now all tasks are finished, process the new downloaded competition file
						await self._processAllCompetitions(self._competitions)
				# Run this loop once every 24 hours
				await asyncio.sleep(24*3600)
		except asyncio.CancelledError:
			logger.warning ("Request to kill the main loop")
			await self._killCompetitionTasks()
		except Exception as e:
			logger.error ("Error: " + traceback.format_exc())
			await self._killCompetitionTasks()

		finally:
			self._processed_competitions.save()
			self._prepared_emails.save()
			self._all_skaters.save()
			self._emails_skaters.save()
			self._venues.save()

	async def _killCompetitionTasks(self):
		for task in self._competitions_tasks_to_process:
			logger.info ("send cancel exception to task: " + task.get_name())
			task.cancel()
			# wait so all tasks can finish
		await asyncio.sleep (1)
		# check and wait for all reamaining tasks
		for task in self._competitions_tasks_to_process:
			logger.info ("wait for task to stop: " + task.get_name())
			loop = asyncio.get_running_loop()
			loop.run_until_complete(task)

	async def _processAllCompetitions(self, competitions: list[CompetitionsType]) -> None:
		logger.debug ("Process new competition file")
		now = datetime.now(timezone.utc)

		for competition in competitions:
			if competition['test']:
				continue

			competition_id = uuid.UUID(competition['id'], version=4)

			if not competition['settings']['isClosed']:
				if not self._processed_competitions.columnHasValue('comp_id', competition_id.bytes):
					self._startProcessCompetition(competition_id, competition['code'], -1)
			else:
				time_open = datetime.fromisoformat(competition['settings']['opens'])
				if time_open > now:
					self._startProcessCompetition(competition_id, competition['code'], time_open)

			if competition['venue'] is not None:
				self._venues.update(address=competition['venue']['address'], code=competition['venue']['code'], name=competition['venue']['name'])
				self._venues.save()

			# give also some time to other tasks
			await asyncio.sleep (0)

	def _startProcessCompetition(self, id: uuid.UUID, code: str|None, when: datetime|int) -> asyncio.Task:
		name = "Task " + str(id)
		if code is not None:
			if len(code) > 0:
				name += " (" + code + ")"
		task = asyncio.create_task(self.processCompetition (id, when))
		task.set_name(name)
		task.add_done_callback(self._competitions_tasks_to_process.discard)
		self._competitions_tasks_to_process.add(task)
		return task

	async def processCompetition(self, id: uuid.UUID, when: datetime|int = 0) -> bool:
		logger.debug ("(" + str(id) + "): schedule the processing of competition")
		try:
			await Competitions._waiter(when)
		except asyncio.CancelledError:
			logger.info ("(" + str(id) + "): task got cancelled before it could start")
			# end the task
			return False

		data: dict[str, dict[str, Any]] = dict()
		try:
			logger.info ("(" + str(id) + "): Check competition")
			data = await Competitions._downloadCompetitionFiles(id)
		except asyncio.CancelledError:
			logger.info ("(" + str(id) + "): task got cancelled during download of competition files")
			# end the task
			return False

		if (data['competitions'] is None) or (data['distancecombinations'] is None) or (data['settings'] is None):
			logger.error ("(" + str(id) + "): download of competition files failed")
			return False
		else:
			logger.debug ("(" + str(id) + "): download of competition files complete")

		skaters: list[uuid.UUID] = []
		combinations: list[dict[str, Any]] = []
		email_html: str = str()
		venue: str|None = None
		serie: dict[str, uuid.UUID|str|list] = dict()

		try:
			if data['competitions']['settings']['isClosed']:
				logger.warning ("(" + str(id) + "): wedstrijd is (nog) niet open")
				return False

			if data['competitions']['venue'] is not None:
				venue = data['competitions']['venue']['code']

			for d1 in data['settings']:
				d2 = Competitions._findInDict (data['distancecombinations'], 'id', d1['distanceCombinationId'])
				skaters_distance = self._all_skaters.filter(venue=venue, homeVenueFilter=d1['homeVenueFilter'], categoryFilter=d2['categoryFilter'], clubCodeFilter=d1['clubCodeFilter'], invitees=d1['invitees'], disciplineCodeFilter=None)

				for skater in skaters_distance:
					if skater not in skaters:
						skaters.append (skater)

				combination: dict[str, uuid.UUID|str|dict[str, Any]|list[int]] = {}
				combination['id'] = uuid.UUID(d1['distanceCombinationId'], version=4)
				combination['name'] = d2['name']
				combination['limit'] = {
					'discipline': d1['limitTimeDistanceDiscipline'],
					'distance': d1['limitTimeDistanceValue'],
					'time': d1['limitTime']
				}
				combination['cost'] = {'competition': d1['competitionPaymentOption'], 'serie': d1['seriePaymentOption']}
				combination['distances'] = []
				for d in d2['distances']:
					combination['distances'].append(d['value'])

				combinations.append (combination)


					# limitTimeDistanceDiscipline
					# limitTimeDistanceValue
					# limitTime
					# allowedRegistrations
					# 1=licentiehouders
					# 9=licentiehouders+active leden
					# 13=selectie active leden
					# 4=selectie

			if data['competitions']['serie'] is not None:
				if isinstance(data['competitions']['serie'], dict) and data['competitions']['serie']['id'] is not None:
					serie['id'] = uuid.UUID(data['competitions']['serie']['id'], version=4)
					serie['name'] = data['competitions']['serie']['name']
					serie['competitions'] = await self._findCompetitionsInSerie (serie['id'], id)

			logger.info ("(" + str(id) + "): distances: " + str(len(combinations)) + "; skaters: " + str(len(skaters)))

			email_html = await self._composeHtmlMail (id, Competitions.getLinks(id), data['competitions'], combinations, self._venues.getVenue(venue), serie)
			await asyncio.sleep(0)
		except asyncio.CancelledError:
			logger.info ("(" + str(id) + "): task got cancelled during processing")
			asyncio.current_task().uncancel()
		except Exception as e:
			logger.error ("(" + str(id) + ": " + traceback.format_exc())

		finally:
			if email_html != '':
				email_id = self._enqueueEmail (id, skaters, email_html)
				if email_id is not None:
					self._addProcessedCompetition(id, email_id)
			return True

	async def _composeHtmlMail(self, id: uuid.UUID, links: dict[str, str], competition: CompetitionsType, combinations: list[dict[str, Any]], venue: dict|None, serie: dict[str, uuid.UUID|str|list]) -> str:
		email: str = str()
		try:
			logger.debug ("(" + str(id) + "): run template Jinja2 generator")
			email_full = await self._email_template.render_async({
				'id': str(id),
				'code': competition['code'],
				'discipline': competition['discipline'],
				'starts': datetime.fromisoformat(competition['starts']),
				'ends': datetime.fromisoformat(competition['ends']),
				'name': competition['name'],
				'closes': datetime.fromisoformat(competition['settings']['closes']),
				'url': competition['settings']['contact']['url'],
				'opens': competition['settings']['opens'],
				'withdrawUntil': datetime.fromisoformat(competition['settings']['withdrawUntil']),
				'message1': competition['settings']['extra'],
				'message2': competition['extra'],
				'location_description': competition['location'],
				'links': links,
				'combinations': combinations,
				'venue': venue,
				'serie_id': serie['id'],
				'serie_name': serie['name'],
				'serie': serie['competitions']
			})
			if self._minify_html:
				email = minify_html.minify(email_full,
								minify_js=True,
								minify_css=True,
								keep_input_type_text_attr=True,
								do_not_minify_doctype=True,
								ensure_spec_compliant_unquoted_attribute_values=True,
								keep_closing_tags=True,
								keep_html_and_head_opening_tags=True,
								keep_spaces_between_attributes=True,
								keep_comments=False,
								remove_processing_instructions=True)
			else:
				email = email_full

			filename = "./" + str(id) + ".email"
			logger.debug ("(" + str(id) + "): email generated and stored in: " + str(filename))
			with open(filename, "w") as outfile:
				outfile.write(email)

		except asyncio.CancelledError as e:
			raise e
		except Exception as e:
			logger.error ("Error: " + traceback.format_exc())

		finally:
			return email

	def _addProcessedCompetition(self, competition_id: uuid.UUID, email_id: uuid.UUID) -> bool:
		ret = self._processed_competitions.append([competition_id.bytes, email_id.bytes])
		self._processed_competitions.save()
		return ret

	async def _findCompetitionsInSerie(self, serie_id: uuid.UUID, exclude_id: uuid.UUID|None = None) -> list[dict[str, uuid.UUID|str]]:
		if self._competitions is None:
			return list()
		result: list[dict] = []
		for competition in self._competitions:
			if competition['serie'] is not None:
				if str(serie_id) == competition['serie']['id']:
					item = {}
					item['id'] = uuid.UUID(competition['id'], version=4)
					item['name'] = competition['name']
					result.append(item)
		return result

	def _enqueueEmail (self, competition_id: uuid.UUID, skaters: list, email_html: str) -> uuid.UUID|None:
		email_uuid = uuid.uuid4()
		ret = self._prepared_emails.append([email_uuid.bytes, competition_id.bytes, email_html, False, None])
		for skater in skaters:
			self._emails_skaters.append([email_uuid.bytes, skater.bytes])
		self._prepared_emails.save()
		self._emails_skaters.save()
		if ret:
			return email_uuid
		else:
			return None

	@staticmethod
	def getCompetitionUrls(id: uuid.UUID) -> dict[str, str]:
		return {
			'competitions': 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id),
			'distancecombinations': 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id) + '/distancecombinations',
			'settings': 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id) + '/settings/distancecombinations'
		}

	@staticmethod
	def getLinks(id: uuid.UUID) -> dict[str, str]:
		return {
			'general': 'https://inschrijven.schaatsen.nl/',
			'subscription': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/inschrijven',
			'information': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/informatie',
			'participants': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/deelnemers'
		}

	@staticmethod
	async def _waiter(when: datetime|int) -> None:
		wait: int = int()
		if isinstance(when, int):
			if when < 0:
				wait = random.randint(1, abs(when))
			logger.debug ("(" + str(id) + "): wait for " + str(wait) + " seconds to start processing competition")
			await asyncio.sleep(wait)
		else:
			while datetime.now(timezone.utc) < when:
				delta = when - datetime.now(timezone.utc)
				wait = int(delta.total_seconds ()) + 1
				logger.debug ("(" + str(id) + "): wait for " + str(wait) + " seconds to start processing competition")
				await asyncio.sleep(wait)
		return None

	@staticmethod
	async def _downloadCompetitionFiles(id: uuid.UUID) -> dict[str, dict[str, Any]]:
		urls = Competitions.getCompetitionUrls(id)
		data: dict[str, dict[str, Any]] = {
				'competitions': dict(),
				'distancecombinations': dict(),
				'settings': dict()
			}
		async with aiohttp.ClientSession() as session:
			for key, url in urls.items():
				async with session.get(url) as response:
					data[key] = json.loads(await response.text())
		return data

	@staticmethod
	def _findInDict(d: dict, key: str, value: str) -> dict[str, Any]:
		for e in d:
			if key in e:
				if e[key] == value:
					return e
		return {}
