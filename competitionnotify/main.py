#!/bin/python

import asyncio
import logging
import traceback

import providers.venues as venues
import providers.skaters as skaters
import providers.results_vantage as results_vantage
import providers.results_ssr as results_ssr
import providers.schaatsen_nl as schaatsen_nl
import task_manager
import websocket

#test
import uuid

logger = logging.getLogger(__name__)

async def runner() -> None:
	try:
		# Initialize instances of the task manager class
		competition_processes = task_manager.TaskManager()
		utils_processes = task_manager.TaskManager()
		websocket_process = task_manager.TaskManager()

		# get isntance to venues
		venues = venues.Venues()
		utils_processes.startProces(venues.load())

		# get instance to skaters
		skaters = skaters.Skaters(file="skaters.h5")
		utils_processes.startProces(skaters.load())

		# get instance to Vantage (KNSB) times
		results_vantage = results_vantage.ResultsVantage()

		# get instance to Speed Skating Results
		results_ssr = results_ssr.ResultsSSR()

		# Database with processed competitions
		processed_competitions = ProcessedCompetitions(file="processed_competitions")

		# And of course the email handling provider
		emails = Emails(prepared_file="prepared_emails", send_file="send_emails")

		# Get an instance of the main download class
		competitions = schaatsen_nl.SchaatsenDotNl(skaters=skaters, venues=venues, results=[results_vantage, results_ssr], processed_competitions=processed_competitions, emails=emails)
		utils_processes.startProces(competitions.load())

		# start websocket
		websocket = websocket.Websocket()

		# register all modules for the websocket
		websocket.registerModule(venues)
		websocket.registerModule(skaters)
		websocket.registerModule(results_vantage)
		websocket.registerModule(results_ssr)
		websocket.registerModule(processed_competitions)
		websocket.registerModule(emails)
		websocket.registerModule(competitions)

		# now wait till the util processes are done (all data is loaded)
		await utils_processes.waitAllProcesses()

		# The modules (incl. data) are properly loaded, now start the web socket
		websocket_process.startProces(websocket.run())

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

async def test() -> None:
	wedstrijden = SchaatsenDotNl()
	await wedstrijden.load()

	i = uuid.UUID("41d4c490-d4d9-4c6b-8daa-ccac6f90bd33", version=4)
	cr = wedstrijden.getCompetition(i)

	c = await cr.getCoroutine()
	print(type(c))
	print(c)


if __name__ == '__main__':
	#logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	asyncio.run(runner())
	#asyncio.run(test())