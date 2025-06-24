#!/bin/python

import typing
import typeguard
import asyncio
import logging
import uuid

import competitionnotify.providers.base.result_provider_interface as result_provider
import competitionnotify.websocket as websocket

logger = logging.getLogger(__name__)

#TODO: make class working
@typeguard.typechecked
class ResultsSSR(result_provider.ResultProviderInterface, websocket.WebsocketInterface):
	def __init__(self):
		return None

	def get(self) -> str:
		return "test"

	def getName(self) -> str:
		return "results_ssr"

	def getCommands(self) -> websocket.CommandList:
		return (
			("count", self._cmd_count),
			)

	def _cmd_count(self) -> int:
		return 1

	def registerWebsocket(self, ws: websocket.Websocket) -> bool:
		return True