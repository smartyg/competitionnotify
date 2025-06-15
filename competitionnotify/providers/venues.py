#!/bin/python

import typing
import logging
import uuid

import competitionnotify.websocket as websocket
import competitionnotify.dataclasses.venue as venue
import competitionnotify.dataclasses.discipline as discipline
import competitionnotify.providers.base.loadable_provider as loadable_provider
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

class Venues(loadable_provider.LoadableProvider, websocket.WebsocketInterface):
	_api_url = "https://inschrijven.schaatsen.nl/api/venues"
	_venues: dict[int, venue.VenueClass] = dict()

	def __init__(self):
		# load data from api into self._venues
		super().__init__(self._api_url, self._loadData)

	async def _loadData(self, json: dict):
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
		venue = self._venues[code]
		venue = venue.AddDiscipline(discipline)
		self._venues[code] = venue

	def _addTrack(self, code: int, track: venue.TrackClass):
		self._addDiscipline(code, track.getDiscipline())

		venue = self._venues[code]
		venue = venue.AddTrack(track)
		self._venues[code] = venue

	def hasVenue(self, code: str|None = None, name: str|None = None, discipline: discipline.DisciplineClass|None = None) -> bool:
		if code is None and name is None:
			raise ...
		for key, venue in sef._venues.items():
			ret: bool = False
			if code is not None:
				if venue.getCode() != code:
					continue
			if name is not None:
				if venue.getName() != name:
					continue
			if discipline is not None:
				if not venue.hasDiscipline(discipline):
					continue
			return True

	def getVenue(self, code: str|None = None, name: str|None = None, discipline: discipline.DisciplineClass|None = None) -> venue.VenueClass:
			if code is None and name is None:
				raise ...
			for key, venue in self._venues.items():
				ret: bool = False
				if code is not None:
					if venue.getCode() != code:
						continue
				if name is not None:
					if venue.getName() != name:
						continue
				if discipline is not None:
					if not venue.hasDiscipline(discipline):
						continue
				return venue

	def getVenueByCode(self, code: str) -> venue.VenueClass:
		return self.getVenue(code=code)

	def getAll(self) -> dict[int, venue.VenueClass]:
		return self._venues

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "venues"

	def getCommands(self) -> list[str]:
		return ["count", "get", "search"]

	def processCommand(self, client_id: uuid.UUID, command: str, data: websocket.DataType) -> websocket.DataType:
		pass

	def registerWebsocket(self, ws: "Websocket") -> bool:
		return True