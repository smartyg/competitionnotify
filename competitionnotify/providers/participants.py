#!/usr/bin/python

import typing
import typeguard
#import attrs
#import asyncio
import logging
import uuid

import websocketframework.websocket as websocket
#import competitionnotify.utils.utils as utils
import competitionnotify.classes.participant as participant
import competitionnotify.providers.schaatsen_nl as schaatsen_nl

logger = logging.getLogger(__name__)

@typeguard.typechecked
class Participants(websocket.WebsocketInterface):

	_competitions: schaatsen_nl.SchaatsenDotNl

	def __init__(self, competitions: schaatsen_nl.SchaatsenDotNl):
		self._competitions = competitions

	def getParticipants(self, client_id: uuid.UUID, competition_id: uuid.UUID, distancecombination_number: int = -1, include_withdraw: bool = True, include_reserve: bool = True) -> tuple[participant.DistancePParticipantsClass]:
		pass

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "participants"

	def getCommands(self) -> websocket.CommandList:
		return (
			("participants", self._cmd_participants, "Return the participants of the given competition."),
			("count_participants", self._cmd_count_participants, "Count the amount of participants of the given competition."),
		)

	def _cmd_participants(self, client_id: uuid.UUID, competition_id: uuid.UUID, distancecombination_number: int = -1, include_withdraw: bool = True, include_reserve: bool = True) -> tuple[dict[str, None|str|int|list[dict[str, None|dict[str, None|str|int]]]]]:
		return ()

	def _cmd_count_participants(self, client_id: uuid.UUID, competition_id: uuid.UUID) -> dict[int, dict[str, int]]:
		return {
			1: {'confirmed': 1, 'unconfirmed': 1, 'withdrawn': 1, 'reserve': 1},
			2: {'confirmed': 1, 'unconfirmed': 1, 'withdrawn': 1, 'reserve': 1},
		}

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True