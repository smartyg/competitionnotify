#!/bin/python

import typeguard
import logging
import asyncio

import websocketframework.websocket as websocket
import competitionnotify.providers.venues as venues

logger = logging.getLogger(__name__)

@typeguard.typechecked
async def run() -> None:
	venues_provider = venues.Venues()
	await venues_provider.load()
	ws = websocket.Websocket()
	ws.registerModule(venues_provider)
	await ws.run()

if __name__ == '__main__':
	asyncio.run(run())