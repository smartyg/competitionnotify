#!/usr/bin/python

import typing
import asyncio
import logging
import uuid
import json
import sqlite3

import competitionnotify.websocket as websocket
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.dataclasses.skater as skater
import competitionnotify.dataclasses.filter as filter
import competitionnotify.providers.base.loadable_provider as loadable_provider
import competitionnotify.providers.venues as venues
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

class Skaters(loadable_provider.LoadableProvider, websocket.WebsocketInterface):
	# saved data:
	#  - KNSB nummer
	#  - email adres
	#  - home venue
	#  - list of venue codes
	#  - list of discpine codes

	_skaters: list[skater.SkaterClass] = list()
	_venueProvider: venues.Venues
	_connection: sqlite3.Connection
	_cursor: sqlite3.Cursor

	def __init__(self, db_file: str, venue_provider: venues.Venues):
		self._connection = sqlite3.connect(db_file)
		self._cursor = self._connection.cursor()
		self._venueProvider = venue_provider
		super().__init__(None, self._loadData)

	def __del__(self):
		self._connection.close()

	async def _loadData(self, json: dict) -> None:
		while not self._venueProvider.isLoaded():
			await asyncio.sleep(1)

		session = await self.getSession()
		self._skaters = await asyncio.gather(*[self._loadSkater(session, e) for e in self._loadDB()])

	def _loadDB(self) -> list[dict[str, typing.Any]]:
		result: list[dict[str, typing.Any]] = []
		for entry in self._cursor.execute("SELECT number, email, home_venue, venues, disciplines, team FROM skaters;"):
			result_entry: dict[str, typing.Any] = {}
			result_entry['number'] = entry[0]
			result_entry['emailAddress'] = entry[1]
			result_entry['homeVenue'] = entry[2]
			result_entry['venues'] = []
			result_entry['disciplines'] = []

			for code in str.split(entry[3], ','):
				result_entry['venues'].append(self._venueProvider.getVenueByCode(code))

			n: int = 0
			while (entry[4] >> n) > 0:
				if ((entry[4] >> n) & 1) == 1:
					result_entry['disciplines'].append(discipline.DisciplineClass(discipline=n))
				n += 1

			result.append(result_entry)

		return result

	async def _loadSkater(self, session, s: dict[str, typing.Any]) -> skater.SkaterClass:
		url = "https://inschrijven.schaatsen.nl/api/licenses/KNSB/SpeedSkating.LongTrack/" + str(s['number'])
		async with session.get(url) as response:
			logger.debug ("Download record for skater id " + str(s['number']) + " ...")
			entry = json.loads(await response.text())
			entry['mailOptions'] = {}
			entry['mailOptions']['emailAddress'] = s['emailAddress']
			entry['mailOptions']['homeVenue'] = s['homeVenue']
			entry['mailOptions']['venues'] = s['venues']
			entry['mailOptions']['disciplines'] = s['disciplines']
			ret = utils.class_factory(entry, skater.SkaterClass)
			return ret

	def getSkaterByName(self, name: str) -> skater.SkaterClass|None:
		for skater in self._skaters:
			if skater.getName() == name:
				return skater
		return None

	def getSkaterByNumber(self, number: int) -> skater.SkaterClass|None:
		for skater in self._skaters:
			if skater.getNumber() == number:
				return skater
		return None

	def getAll(self) -> list[skater.SkaterClass]:
		return self._skaters

	def addOrUpdate(self, skater: skater.SkaterClass) -> bool:
		number = skater.getNumber()
		for old_skater in self._skaters:
			if old_skater.getNumber() == number:
				self._skaters.remove(old_skater)
		self._skaters.append(skater)
		return self.save()

	def filterSkatersEmail(filter: filter.FilterClass) -> list[str]:
		#return [skater.getEmail() if skater.filter(filter) for skater in self._skaters]
		return [skater.getEmail() for skater in self._skaters if filter.testSkater(skater)]

	def filterSkaters(filter: filter.FilterClass) -> list[skater.SkaterClass]:
		#return [skater if skater.filter(filter) for skater in self._skaters]
		return [skater for skater in self._skaters if filter.testSkater(skater)]

	def save(self) -> bool:
		#self._table = [skater.exportDict() for skater in self._skaters]
		pass

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "skaters"

	def getCommands(self) -> list[str]:
		return ["count", "add", "change", "remove", "get", "search"]

	def processCommand(self, client_id: uuid.UUID, command: str, data: websocket.DataType) -> websocket.DataType:
		pass

	def registerWebsocket(self, ws: "Websocket") -> bool:
		return True