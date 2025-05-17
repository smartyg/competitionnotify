#!/bin/python

import typing
import logging

logger = logging.getLogger(__name__)

class Venues(LoadableProvider, WebsocketInterface):
	def __init__(self):
		# load data from api into self._venues


	def hasVenue(self, code: str|None = None, name: str|None = None, discipline: DiscplineClass|None = None) -> bool:
		if code in None and name is None:
			raise ...
		for venue in sef._venues:
			ret: bool = False
			if code in not None:
				if venue.getCode() != code:
					continue
			if name is not None:
				if venue.getName() != name:
					continue
			if discipline is not None:
				if not venue.hasDiscipline(discipline):
					continue
			return True

def getVenue(self, code: str|None = None, name: str|None = None, discipline: DiscplineClass|None = None) -> VenueClass:
		if code in None and name is None:
			raise ...
		for venue in sef._venues:
			ret: bool = False
			if code in not None:
				if venue.getCode() != code:
					continue
			if name is not None:
				if venue.getName() != name:
					continue
			if discipline is not None:
				if not venue.hasDiscipline(discipline):
					continue
			return venue