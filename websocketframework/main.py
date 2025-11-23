#!/bin/python

import typeguard
import asyncio
import logging

import websocketframework.websocket

logger = logging.getLogger(__name__)

@typeguard.typechecked
async def run() -> None:
	ws = websocketframework.websocket.Websocket()
	await ws.run()

if __name__ == '__main__':
	#logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	asyncio.run(run())