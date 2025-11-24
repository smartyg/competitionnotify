#!/bin/python

import asyncio
import logging
import traceback

import taskmanager.taskmanager as task_manager
import websocketframework.websocket as websocket
import competitionnotify.providers.venues as venues
import competitionnotify.providers.skaters as skaters
import competitionnotify.providers.results_vantage as results_vantage
import competitionnotify.providers.results_ssr as results_ssr
import competitionnotify.providers.emails as emails
import competitionnotify.providers.processed_competitions as processed_competitions
import competitionnotify.providers.schaatsen_nl as schaatsen_nl

logger = logging.getLogger(__name__)

async def runner() -> None:
	try:
		# Initialize instances of the task manager class
		competition_processes = task_manager.TaskManager()
		utils_processes = task_manager.TaskManager()
		websocket_process = task_manager.TaskManager()

		# get instance to venues
		venues_provider = venues.Venues()
		await utils_processes.createAndStartProcess(venues_provider.load())

		# get instance to skaters
		skaters_provider = skaters.Skaters(db_file="/mnt/projects/development/competitionnotify/skaters.db")
		await utils_processes.createAndStartProcess(skaters_provider.load())

		# get instance to Vantage (KNSB) times
		results_provider_vantage = results_vantage.ResultsVantage()

		# get instance to Speed Skating Results
		results_provider_ssr = results_ssr.ResultsSSR()

		# Database with processed competitions
		processed_competitions = processed_competitions.ProcessedCompetitions(db_file="/mnt/projects/development/competitionnotify/processed_competitions.db")

		# And of course the email handling provider
		emails = emails.Emails(db_file="/mnt/projects/development/competitionnotify/emails.db")

		# Get an instance of the main download class
		competitions = schaatsen_nl.SchaatsenDotNl(skaters=skaters_provider, venues=venues_provider, results=[results_provider_vantage, results_provider_ssr], processed_competitions=processed_competitions, emails=emails)
		#competitions = schaatsen_nl.SchaatsenDotNl(skaters=skaters_provider, venues=venues_provider, results=[results_provider_ssr], processed_competitions=None, emails=None)
		await utils_processes.createAndStartProcess(competitions.load())

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
		await websocket_process.createAndStartProcess(ws.run())

		# Always run the main loop, untill an exception happens
		while True:
			# get a new list of competition coroutines
			competition_list: set[task_manager.CoroutineClass] = await competitions.getCompetitions(download=True)

			# Cancel all existing (running) tasks, as now we have a new list of tasks prepared
			await competition_processes.cancelProcesses()
			# Run the new list of prepared tasks
			await competition_processes.startProcesses(competition_list)

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

if __name__ == '__main__':
	logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	asyncio.run(runner())