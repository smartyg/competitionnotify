#!/bin/python

import typing
import typeguard
import asyncio
import logging
import uuid

import websocketframework.websocket as websocket
import websocketframework.websocketinterface as websocketinterface
import competitionnotify.providers.base.result_provider_interface as result_provider

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ResultsVantage(result_provider.ResultProviderInterface, websocketinterface.WebsocketInterface):
	def __init__(self):
		return None

	def get(self) -> str:
		return "test"

	# Interfaces for WebsocketInterface
	def getName(self) -> str:
		return "vantage"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count),
			)

	def _cmd_count(self, client_id: uuid.UUID) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True