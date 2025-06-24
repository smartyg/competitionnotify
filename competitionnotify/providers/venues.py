#!/bin/python

import typing
import typeguard
import logging
import uuid
import attrs

import competitionnotify.websocket as websocket
import competitionnotify.dataclasses.venue as venue
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.providers.base.loadable_provider as loadable_provider
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
class Venues(loadable_provider.LoadableProvider, websocket.WebsocketInterface):
	_api_url = "https://inschrijven.schaatsen.nl/api/venues"
	_venues: dict[int, venue.VenueClass] = dict()

	def __init__(self):
		# load data from api into self._venues
		super().__init__(self._api_url, self._loadData)

	async def _loadData(self, json: list[dict]):
		for entry in json:
			code = self._getVenueRefByCode(entry['code'])
			if code is None:
				venue_cls = utils.class_factory(entry, venue.VenueClass)
				self._addVenue(venue_cls)
			else:
				self._addDiscipline(code, discipline.DisciplineClass.getDisciplineByString(string=entry['discipline']))
				for track_entry in entry['tracks']:
					track = utils.class_factory(track_entry, venue.TrackClass)
					self._addTrack(code, track)

	def _getVenueRefByCode(self, code: str) -> int|None:
		for key, venue in self._venues.items():
			if venue.getCode() == code:
				return key
		return None

	def _addVenue(self, venue_cls: venue.VenueClass) -> int:
		i = len(self._venues.keys())
		while i in self._venues:
			i += 1
		self._venues[i] = venue_cls
		return i

	def _addDiscipline(self, code: int, discipline: discipline.DisciplineClass):
		venue_cls = self._venues[code]
		venue_cls = venue_cls.AddDiscipline(discipline)
		self._venues[code] = venue_cls

	def _addTrack(self, code: int, track: venue.TrackClass):
		self._addDiscipline(code, track.getDiscipline())

		venue_cls = self._venues[code]
		venue_cls = venue_cls.AddTrack(track)
		self._venues[code] = venue_cls

	def hasVenue(self, code: str|None = None, name: str|None = None, discipline: discipline.DisciplineClass|None = None) -> bool:
		if code is None and name is None:
			raise TypeError
		for venue_cls in self._venues.values():
			return testVenue(venue_cls, code, name, discipline)

	def getVenue(self, code: str|None = None, name: str|None = None, discipline: discipline.DisciplineClass|None = None) -> venue.VenueClass:
			if code is None and name is None:
				raise TypeError
			for venue_cls in self._venues.values():
				if testVenue(venue_cls, code, name, discipline):
					return venue_cls

	def getVenueCodes(self, code: str|None = None, name: str|None = None, discipline: discipline.DisciplineClass|None = None) -> list[str]:
		return [v.getCode() for v in self._venues.values() if testVenue(v, code, name, discipline)]

	def getVenueByCode(self, code: str) -> venue.VenueClass:
		return self.getVenue(code=code)

	def getAll(self) -> dict[int, venue.VenueClass]:
		return self._venues

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "venues"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count, "Number of venues."),
			("get", self._cmd_get),
			("list", self._cmd_list, "List all venue codes."),
			)

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return len(self._venues)

	def _cmd_get(self, client_id: uuid.UUID, code: str) -> dict[str, typing.Any]:
		res = self.getVenue(code=code)
		return attrs.asdict(res)

	def _cmd_list(self, client_id: uuid.UUID, d: str|None = None) -> list[str]:
		res: list[str] = []
		d_cls: discipline.DisciplineClass|None = None
		if d is not None:
			d_cls = discipline.DisciplineClass.getDisciplineByString(string=d)

		return self.getVenueCodes(discipline=d_cls)

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True

@typeguard.typechecked
def testVenue(venue_cls: venue.VenueClass, code: str|None = None, name: str|None = None, discipline: discipline.DisciplineClass|None = None) -> bool:
	if code is not None:
		if venue_cls.getCode() != code:
			return False
	if name is not None:
		if venue_cls.getName() != name:
			return False
	if discipline is not None:
		if not venue_cls.hasDiscipline(discipline):
			return False
	return True

import asyncio
import competitionnotify.websocket as websocket

async def run() -> None:
	venues_provider = Venues()
	await venues_provider.load()
	ws = websocket.Websocket()
	ws.registerModule(venues_provider)
	await ws.run()

if __name__ == '__main__':
	asyncio.run(run())