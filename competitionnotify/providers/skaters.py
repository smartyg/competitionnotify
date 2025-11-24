#!/usr/bin/python

import typing
import typeguard
import attrs
import asyncio
import logging
import uuid
import json
import sqlite3

import websocketframework.websocket as websocket
import websocketframework.websocketinterface as websocketinterface
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.skater as skater
import competitionnotify.classes.filter as filter
import competitionnotify.providers.base.loadable_provider as loadable_provider
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
class Skaters(loadable_provider.LoadableProvider, websocketinterface.WebsocketInterface):
	# saved data:
	#  - KNSB nummer
	#  - email adres
	#  - home venue
	#  - list of venue codes
	#  - list of discpine codes

	_skaters: list[skater.SkaterClass] = []
	_connection: sqlite3.Connection|None = None
	_cursor: sqlite3.Cursor
	_db_file: str|None

	def __init__(self, db_file: str|None = None):
		self._db_file = db_file
		if isinstance(db_file, str):
			self._connection = sqlite3.connect(db_file)
		else:
			self._connection = sqlite3.connect(":memory:")
		self._cursor = self._connection.cursor()

		logger.info ("Check if database contains a table `skaters`, if not create it.")
		self._cursor.execute("CREATE TABLE IF NOT EXISTS skaters (number INTEGER PRIMARY KEY NOT NULL, email TEXT NOT NULL, home_venue INTEGER DEFAULT FALSE, venues TEXT DEFAULT '', disciplines INTEGER DEFAULT 0, team INTEGER DEFAULT 0) STRICT")

		super().__init__(None, self._loadData)

	def __del__(self):
		if self._connection is not None:
			self.save()
			self._connection.close()
		self._connection = None

	async def _loadData(self, json: dict) -> None:
		session = await self.getSession()
		self._skaters = await asyncio.gather(*[self._loadSkater(session, e) for e in self._loadDB()])

	def _loadDB(self) -> list[dict[str, typing.Any]]:
		result: list[dict[str, typing.Any]] = []
		for entry in self._cursor.execute("SELECT number, email, home_venue, venues, disciplines, team FROM skaters;"):
			result_entry: dict[str, typing.Any] = {}
			result_entry['number'] = entry[0]
			result_entry['emailAddress'] = entry[1]
			result_entry['homeVenue'] = True if entry[2] else False
			result_entry['venues'] = []
			result_entry['disciplines'] = []

			for code in str.split(entry[3], ','):
				result_entry['venues'].append(code)

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

	def hasSkaterByNumber(self, id: int|str) -> bool:
		for skater in self._skaters:
			if skater.getId() == str(id):
				return True
		return True

	def getSkaterByNumber(self, id: int|str) -> skater.SkaterClass|None:
		for s in self._skaters:
			if s.getId() == str(id):
				return s
		return None

	def getAll(self) -> list[skater.SkaterClass]:
		return self._skaters

	def addOrUpdate(self, skater: skater.SkaterClass) -> bool:
		number = skater.getId()
		for old_skater in self._skaters:
			if old_skater.getId() == number:
				self._skaters.remove(old_skater)
		self._skaters.append(skater)
		return self.save()

	def filterSkatersEmailAddress(self, filter: filter.FilterClass) -> list[str]:
		return [skater.getEmailAddress() for skater in self._skaters if filter.testSkater(skater)]

	def filterSkaters(self, filter: filter.FilterClass) -> list[skater.SkaterClass]:
		return [skater for skater in self._skaters if filter.testSkater(skater)]

	def save(self) -> bool:
		data: list[dict[str, str|int|bool]] = [skater.sqlDict() for skater in self._skaters]
		sql_insert = "INSERT OR REPLACE INTO `skaters` (number, email, home_venue, venues, disciplines, team) VALUES (:number, :email, :home_venue, :venues, :disciplines, :team)" # + ",".join(data)
		self._cursor.executemany(sql_insert, data)
		return True

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "skaters"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count, "Return the number of skaters in the database"),
			("add", self._cmd_add, "Add a skaters to the list with KNSB number and email address."),
			("update", self._cmd_update, "update mail settings of a skater"),
			("remove", self._cmd_remove, "Remove a skater from the database by KNSB number."),
			("get", self._cmd_get, "Get the details of a skater in the database."),
			("search_name", self._cmd_search, "Search a skater by (part of) a name.")
			)

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return len(self._skaters)

	async def _cmd_add(self, client_id: uuid.UUID, number: str, email: str) -> bool:
		session = await self.getSession()
		record: dict[str, typing.Any] = {}
		record['number'] = number
		record['emailAddress'] = email
		record['homeVenue'] = False
		record['venues'] = []
		record['disciplines'] = []
		s = await self._loadSkater(session, record)
		self._skaters.append(s)
		return True

	def _cmd_update(self, client_id: uuid.UUID, number: str, email: str|None = None, home_venue: bool|None = None, venues: list[str]|None = None, disciplines: list[int]|None = None) -> bool:
		s = self.getSkaterByNumber(number)
		if s is None:
			return False

		o = s.getOptions()
		if o is None:
			o = skater.MailOptionsClass(emailAddress="", homeVenue=False, venues=tuple(), disciplines=tuple())

		if email is not None:
			o_new = attrs.evolve(o, emailAddress=email)
			o = o_new

		if home_venue is not None:
			o_new = attrs.evolve(o, homeVenue=home_venue)
			o = o_new

		if venues is not None:
			o_new = attrs.evolve(o, venues=tuple(venues))
			o = o_new

		if disciplines is not None:
			disciplines_new = [discipline.DisciplineClass(discipline=d) for d in disciplines]
			o_new = attrs.evolve(o, disciplines=tuple(disciplines_new))
			o = o_new

		s_new = attrs.evolve(s, mailOptions=o)

		return self.addOrUpdate(s_new)

	def _cmd_remove(self, client_id: uuid.UUID, number: str, remove: bool = False) -> bool:
		if not remove:
			return False

		s = self.getSkaterByNumber(number)
		if s is None:
			return False
		else:
			self._skaters.remove(s)
			return True

	def _cmd_get(self, client_id: uuid.UUID, number: str) -> dict[str, typing.Any]:
		s = self.getSkaterByNumber(number)
		if s is None:
			return {}
		else:
			return attrs.asdict(s)

	def _cmd_search(self, client_id: uuid.UUID, first_name: str|None = None, last_name_prefix: str|None = None, last_name: str|None = None, category: str|None = None, club: int|None = None) -> list[dict[str, typing.Any]]:
		results: list[dict[str, typing.Any]] = []
		for s in self._skaters:
			p = s._personName

			match: bool = False

			if first_name is not None:
				if first_name == s.getFirstName():
					match = True
				else:
					match = False

			if last_name_prefix is not None:
				if last_name_prefix == s.getPrefix():
					match = True
				else:
					match = False

			if last_name is not None:
				if first_name == s.getSurename():
					match = True
				else:
					match = False

			if category is not None:
				if category == s.getFirstName():
					match = True
				else:
					match = False

			if club is not None:
				if club == s.getClub():
					match = True
				else:
					match = False

			if match:
				results.append(attrs.asdict(s))

		return results

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True