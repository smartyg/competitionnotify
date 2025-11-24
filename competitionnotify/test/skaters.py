#!/usr/bin/python

import typeguard
import logging
import asyncio

import websocketframework.websocket as websocket
import competitionnotify.providers.skaters as skaters

logger = logging.getLogger(__name__)

@typeguard.typechecked
async def run() -> None:
	skaters_provider = skaters.Skaters()
	await skaters_provider.load()
	ws = websocket.Websocket()
	ws.registerModule(skaters_provider)
	await ws.run()

if __name__ == '__main__':
	asyncio.run(run())