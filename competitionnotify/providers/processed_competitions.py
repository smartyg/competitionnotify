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
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ProcessedCompetitions(websocketinterface.WebsocketInterface):

	_competitions: list[object] = []
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
		#self._cursor.execute("CREATE TABLE IF NOT EXISTS skaters (number INTEGER PRIMARY KEY NOT NULL, email TEXT NOT NULL, home_venue INTEGER DEFAULT FALSE, venues TEXT DEFAULT '', disciplines INTEGER DEFAULT 0, team INTEGER DEFAULT 0) STRICT")

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "processed-competitions"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count),
			)

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True