#!/bin/python

import asyncio
import logging
import traceback

import competitionnotify.providers.venues as venues
import competitionnotify.providers.skaters as skaters
import competitionnotify.providers.results_vantage as results_vantage
import competitionnotify.providers.results_ssr as results_ssr
import competitionnotify.providers.schaatsen_nl as schaatsen_nl
import competitionnotify.task_manager as task_manager
import websocketframework.websocket as websocket

logger = logging.getLogger(__name__)

async def runner() -> None:
	try:
		# Initialize instances of the task manager class
		competition_processes = task_manager.TaskManager()
		utils_processes = task_manager.TaskManager()
		websocket_process = task_manager.TaskManager()

		# get instance to venues
		venues_provider = venues.Venues()
		await utils_processes.startProcess(venues_provider.load())

		# get instance to skaters
		skaters_provider = skaters.Skaters(db_file="/mnt/projects/development/competitionnotify/skaters.db")
		await utils_processes.startProcess(skaters_provider.load())

		# get instance to Vantage (KNSB) times
		results_provider_vantage = results_vantage.ResultsVantage()

		# get instance to Speed Skating Results
		results_provider_ssr = results_ssr.ResultsSSR()

		# Database with processed competitions
		processed_competitions = ProcessedCompetitions(db_file="/mnt/projects/development/competitionnotify/processed_competitions.db")

		# And of course the email handling provider
		emails = Emails(prepared_file="prepared_emails", send_file="send_emails")

		# Get an instance of the main download class
		competitions = schaatsen_nl.SchaatsenDotNl(skaters=skaters_provider, venues=venues_provider, results=[results_provider_vantage, results_provider_ssr], processed_competitions=processed_competitions, emails=emails)
		#competitions = schaatsen_nl.SchaatsenDotNl(skaters=skaters_provider, venues=venues_provider, results=[results_provider_ssr], processed_competitions=None, emails=None)
		await utils_processes.startProcess(competitions.load())

		# start websocket
		ws = websocket.Websocket()

		# register all modules for the websocket
		ws.registerModule(venues_provider)
		ws.registerModule(skaters_provider)
		ws.registerModule(results_provider_vantage)
		ws.registerModule(results_provider_ssr)
		ws.registerModule(processed_competitions)
		ws.registerModule(emails)
		ws.registerModule(competitions)

		# now wait till the util processes are done (all data is loaded)
		await utils_processes.waitAllProcesses()

		# The modules (incl. data) are properly loaded, now start the web socket
		await websocket_process.startProcess(ws.run())

		# Always run the main loop, untill an exception happens
		while True:
			# get a new list of competition coroutines
			competitions = await competitions.getCompetitions(download=True)

			# Cancel all existing (running) tasks, as now we have a new list of tasks prepared
			await competition_processes.cancelProcesses()
			# Run the new list of prepared tasks
			await competition_processes.startProcesses(competitions)

			# Run this loop once every 24 hours
			await asyncio.sleep(24*3600)

	except asyncio.CancelledError:
		logger.warning ("Request to kill the main loop")
		await competition_processes.cancelProcesses()
		await websocket_process.cancelProcesses()
		await utils_processes.cancelProcesses()
	except Exception as e:
		logger.error ("Error: " + traceback.format_exc())
		await competition_processes.cancelProcesses()
		await websocket_process.cancelProcesses()
		await utils_processes.cancelProcesses()

	return None

# async def test() -> None:
# 	wedstrijden = SchaatsenDotNl()
# 	await wedstrijden.load()
#
# 	i = uuid.UUID("41d4c490-d4d9-4c6b-8daa-ccac6f90bd33", version=4)
# 	cr = wedstrijden.getCompetition(i)
#
# 	c = await cr.getCoroutine()
# 	print(type(c))
# 	print(c)
#
#
# async def test_venues() -> None:
# 	venues_provider = venues.Venues()
# 	await venues_provider.load()
#
# 	s = venues_provider.getAll()
# 	print(type(s))
# 	print(s)
#
# async def test_skaters() -> None:
# 	skaters_provider = skaters.Skaters("/mnt/projects/development/competitionnotify/skaters.db")
# 	await skaters_provider.load()
#
# 	s = skaters_provider.getAll()
# 	print(type(s))
# 	print(s)

if __name__ == '__main__':
	#logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	asyncio.run(runner())
	#asyncio.run(test())
	#asyncio.run(test_skaters())