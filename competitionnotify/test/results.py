#!/bin/python

import typeguard
import logging
import asyncio

import websocketframework.websocket as websocket
import competitionnotify.providers.results as results
#import competitionnotify.providers.results_vantage as results_vantage
import competitionnotify.providers.results_ssr as results_ssr

logger = logging.getLogger(__name__)

@typeguard.typechecked
async def run() -> None:
	#results_provider_vantage = results_vantage.ResultsVantage()
	results_provider_ssr = results_ssr.ResultsSSR()
	#results_provider = results.Results([results_provider_vantage])
	#results_provider = results.Results([results_provider_vantage, results_provider_ssr])
	results_provider = results.Results([results_provider_ssr])
	ws = websocket.Websocket()
	ws.registerModule(results_provider)
	ws.registerModule(results_provider_ssr)
	await ws.run()

if __name__ == '__main__':
	asyncio.run(run())
