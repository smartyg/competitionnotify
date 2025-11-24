#!/bin/python

import typing
import typeguard
import asyncio
import logging

import websocketframework.websocket as websocket
import websocketframework.websocketinterface as websocketinterface
import competitionnotify.providers.base.result_provider_interface as result_provider

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ResultsVantage(result_provider.ResultProviderInterface, websocketinterface.WebsocketInterface):
	pass