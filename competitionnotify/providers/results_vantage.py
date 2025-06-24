#!/bin/python

import typing
import typeguard
import asyncio
import logging

import competitionnotify.providers.base.result_provider_interface as result_provider
import competitionnotify.websocket as websocket

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ResultsVantage(result_provider.ResultProviderInterface, websocket.WebsocketInterface):
	pass