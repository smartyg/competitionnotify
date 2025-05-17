#!/bin/python

import asyncio
import logging
import providers.base.result_provider_interface as result_provider
import websocket

logger = logging.getLogger(__name__)

class ResultSSR(result_provider.ResultProviderInterface, websocket.WebsocketInterface):
	pass