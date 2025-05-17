#!/usr/bin/python

import typing
import logging
import dataclasses.skaters as skaters

logger = logging.getLogger(__name__)

class Skaters(Datafile, LoadableProvider, WebsocketInterface):
	# saved data:
	#  - KNSB nummer
	#  - email adres
	#  - home venue?
	#  - list of venue codes
	#  - list of discpine codes

	_table: list[dict[str, typing.Any]]
	_skaters: list[skaters.SkaterSettingClass] = list()

	def __init__(self, file: str):
		# load data from file
		self._table = self.loadData(file)


		#load skater info from api

	async def load(self) -> None:
		session = aiohttp.ClientSession()
		self._skaters = await asyncio.gather(*[self._loadSkater(session, e) for e in self._table])

	async def _loadSkater(self, session, entry: dict[str, typing.Any]) -> skaters.SkaterSettingClass:
		url = "https://inschrijven.schaatsen.nl/api/licenses/KNSB/SpeedSkating.LongTrack/" + str(entry[id])
		async with session.get(url) as response:
			logger.debug ("Download record for skater id " + str(entry[id]) + " ...")
			entry['person'] = json.loads(await response.text())
			ret = class_factory(entry, skatersSkaterSettingClass)
			return ret

	def filterSkatersEmail(...) -> list[str]:
		return [skater.getEmail() if skater.filter(...) for skater in self._skaters]

	def filterSkaters(...) -> list[skaters.SkaterClass]:
		return [skater.getPerson() if skater.filter(...) for skater in self._skaters]

	def save(self) -> None:
		self._table = [skater.exportDict() for skater in self._skaters]

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "skaters"

	def getCommands(self) -> list[str]:
		return ["count", "add", "change", "remove", "get", "search"]

	def processCommand(self, client_id: uuid.UUID, command: str, data: DataType) -> DataType:
		pass

	def registerWebsocket(self, ws: "Websocket") -> bool:
		return True