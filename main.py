#!/bin/python

import typing
import json
from datetime import datetime, timedelta, timezone
import logging
import uuid
import aiohttp
import asyncio
import random
import jinja2
from DataStructure import ProcessedCompetitions, Emails, Skaters, EmailsSkaters, HomeVenues
import minify_html
import traceback

logger = logging.getLogger(__name__)

homeVenueCodes = ["ALK", "AMS"]
categoryCode = ["HPF", "DPF", "HPE", "DPE", "HPD", "DPD", "HPC", "DPC", "HPB", "DPB", "HPA", "DPA", "HC1", "DC1", "HC2", "DC2", "HB1", "DB1", "HB2", "DB2", "HA1", "DA1", "HA2", "DA2", "HN1", "DN1", "HN2", "DN2", "HN3", "DN3", "HN4", "DN4", "HSA", "DSA", "HSB", "DSB", "H40", "D40", "H45", "D45", "H50", "D50", "H55", "D55", "H60", "D60", "H65", "D65", "H70", "D70", "H75", "D75", "H80", "D80"]
disciplineCode = ["SpeedSkating.LongTrack", "SpeedSkating.ShortTrack"]

competitionsTasksToProcess = set()
competitionTask = None

processed_competitions = ProcessedCompetitions ('processed_competitions.h5')
prepared_emails = Emails ('emails.h5')
all_skaters = Skaters ('skaters.h5')
emails_skaters = EmailsSkaters('emails_skaters.h5')
venues = HomeVenues('venues.h5')

templateLoader = jinja2.FileSystemLoader(searchpath="./")
templateEnv = jinja2.Environment(loader=templateLoader,enable_async=True)
email_template = templateEnv.get_template("email_template")

async def main():
	logger.info ("Welcome at the competition notification service tool")

	competitionTask = asyncio.create_task(download_competitions ())

	await competitionTask

	logger.warning ("main download loop has ended, stop program")

	return None

async def kill_competitions_tasks():
	for task in competitionsTasksToProcess:
		logger.info ("send cancel exception to task: " + task.get_name())
		task.cancel()
		# wait so all tasks can finish
	await asyncio.sleep (5)
	# check and wait for all reamaining tasks
	for task in competitionsTasksToProcess:
		logger.info ("wait for task to stop: " + task.get_name())
		loop = asyncio.get_running_loop()
		loop.run_until_complete(task)

async def download_competitions():
	try:
		logger.debug ("Start the main loop")
		while True:
			logger.debug ("Download the new competition file")
			async with aiohttp.ClientSession() as session:
				async with session.get('https://inschrijven.schaatsen.nl/api/competitions') as response:
					logger.debug ("New competition file downloaded")
					competitions = json.loads(await response.text())

					# We have a new competition file, now cancel all outstanding tasks
					await kill_competitions_tasks ()

					#now all tasks are finished, process the new downloaded competition file
					await process_all_competitions(competitions)
			# Run this loop once every 24 hours
			await asyncio.sleep(24*3600)
	except asyncio.CancelledError:
		logger.warning ("Request to kill the main loop")
		await kill_competitions_tasks ()
	except Exception as e:
		logger.error ("Error: " + traceback.format_exc())
		await kill_competitions_tasks ()

	finally:
		processed_competitions.save()
		prepared_emails.save()
		all_skaters.save()
		emails_skaters.save()
		venues.save()

def start_process_competition(id: uuid, code: str|None, when: datetime|int) -> asyncio.Task:
	name = "Task " + str(id)
	if code is not None:
		if len(code) > 0:
			name += " (" + code + ")"
	task = asyncio.create_task(process_competition (id, when))
	task.set_name(name)
	task.add_done_callback(competitionsTasksToProcess.discard)
	competitionsTasksToProcess.add(task)
	return task

async def process_all_competitions(competitions: list):
	logger.debug ("Process new competition file")
	now = datetime.now(timezone.utc)

	for comp in competitions:
		if comp['test']:
			continue
		comp_settings = comp['settings']
		comp_id = uuid.UUID(comp['id'], version=4)

		if not comp_settings['isClosed']:
			if not processed_competitions.columnHasValue('comp_id', comp_id.bytes):
				start_process_competition(comp_id, comp['code'], -1)
		else:
			time_open = datetime.fromisoformat(comp_settings['opens'])
			if time_open > now:
				start_process_competition(comp_id, comp['code'], time_open)

		# if comp['venue'] is not None:
		# 	venues.update(address=comp['venue']['address'], code=comp['venue']['code'], name=comp['venue']['name'])
		# 	venues.save()

		# give also some time to other tasks
		await asyncio.sleep (0)

def find_dict(d: dict, key: str, value: str) -> dict:
	for e in d:
		if key in e:
			if e[key] == value:
				return e
	return {}

def get_urls(id: uuid) -> dict[str: str]:
	urls = {
		'competitions': 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id),
		'distancecombinations': 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id) + '/distancecombinations',
		'settings': 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id) + '/settings/distancecombinations'
	}
	return urls

def get_links(id: uuid) -> dict[str: str]:
	links = {
		'general': 'https://inschrijven.schaatsen.nl/',
		'subscription': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/inschrijven',
		'information': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/informatie',
		'participants': 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/deelnemers'
	}
	return links

async def process_competition(id: uuid, when: datetime|int = 0):
	logger.debug ("(" + str(id) + "): schedule the processing of competition")
	try:
		if isinstance(when, int):
			if when == -1:
				when = random.randint(1, 60)
			logger.debug ("(" + str(id) + "): wait for " + str(when) + " seconds to start processing competition")
			await asyncio.sleep(when)
		else:
			while datetime.now(timezone.utc) < when:
				delta = when - datetime.now(timezone.utc)
				wait = int(delta.total_seconds ()) + 1
				logger.debug ("(" + str(id) + "): wait for " + str(wait) + " seconds to start processing competition")
				await asyncio.sleep(wait)
	except asyncio.CancelledError:
		logger.info ("(" + str(id) + "): task got cancelled before it could start")
		# end the task
		return None

	logger.info ("(" + str(id) + "): Controleren van wedstrijd")
	urls = get_urls(id)

	data = {
		'competitions': None,
		'distancecombinations': None,
		'settings': None
	}

	try:
		async with aiohttp.ClientSession() as session:
			for key, url in urls.items():
				async with session.get(url) as response:
					data[key] = json.loads(await response.text())
	except asyncio.CancelledError:
		logger.info ("(" + str(id) + "): task got cancelled during download of competition files")
		# end the task
		return None

	if (data['competitions'] is None) or (data['distancecombinations'] is None) or (data['settings'] is None):
		logger.error ("(" + str(id) + "): download of competition files failed")
		return None
	else:
		logger.debug ("(" + str(id) + "): download of competition files complete")

	skaters = []
	distances = []
	email_html = str()
	venue = None
	serie = None

	try:
		if data['competitions']['settings']['isClosed']:
			logger.warning ("(" + str(id) + "): wedstrijd is (nog) niet open")
			return False

		if data['competitions']['venue'] is not None:
			venue = data['competitions']['venue']['code']

		for d1 in data['settings']:
			d2 = find_dict (data['distancecombinations'], 'id', d1['distanceCombinationId'])
			skaters_distance = all_skaters.filter(venue=venue, homeVenueFilter=d1['homeVenueFilter'], categoryFilter=d2['categoryFilter'], clubCodeFilter=d1['clubCodeFilter'], invitees=d1['invitees'], disciplineCodeFilter=None)

			for skater in skaters_distance:
				if skater not in skaters:
					skaters.append (skater)

			distance_entry = {}
			distance_entry['id'] =  uuid.UUID(d1['distanceCombinationId'], version=4)
			distance_entry['name'] = d2['name']
			distance_entry['limit'] = {'discipline': d1['limitTimeDistanceDiscipline'], 'distance': d1['limitTimeDistanceValue'], 'time': d1['limitTime']}
			distance_entry['cost'] = {'competition': d1['competitionPaymentOption'], 'serie': d1['seriePaymentOption']}
			distance_entry['distances'] = []
			for d in d2['distances']:
				distance_entry['distances'].append (d['value'])

			distances.append (distance_entry)


				# limitTimeDistanceDiscipline
				# limitTimeDistanceValue
				# limitTime
				# allowedRegistrations
				# 1=licentiehouders
				# 9=licentiehouders+active leden
				# 13=selectie active leden
				# 4=selectie

		if data['competitions']['serie'] is not None:
			if data['competitions']['serie']['id'] is not None:
				serie_id = uuid.UUID(data['competitions']['serie']['id'], version=4)
				serie = find_others_in_serie (serie_id, id)

		logger.info ("(" + str(id) + "): distances: " + str(len(distances)) + "; skaters: " + str(len(skaters)))

		email_html = await compose_html_mail (id, get_links(id), data['competitions'], distances, venues.getVenue(venue), serie=serie)
		await asyncio.sleep(0)
	except asyncio.CancelledError:
		logger.info ("(" + str(id) + "): task got cancelled during processing")
		asyncio.current_task().uncancel()
	except Exception as e:
		logger.error ("(" + str(id) + "/" + d1['distanceCombinationId'] + "): " + traceback.format_exc())

	finally:
		if email_html != '':
			email_id = enqueue_email (id, skaters, email_html)
			if email_id is not None:
				add_processed_competition(id, email_id)
		return None

def find_others_in_serie (serie_id: uuid, exclude_id: "uuid|None" = None) -> list|None:
	return None

async def compose_html_mail (id: uuid, links: dict[str: str], competition: dict, combinations: list, venue: dict|None = None, serie: list|None = None) -> str:
	email = str()
	try:
		logger.debug ("(" + str(id) + "): run template Jinja2 generator")
		email_full = await email_template.render_async({
			'id': str(id),
			'code': competition['code'],
			'discipline': competition['discipline'],
			'starts': datetime.fromisoformat(competition['starts']),
			'ends': datetime.fromisoformat(competition['ends']),
			'name': competition['name'],
			'closes': datetime.fromisoformat(competition['settings']['closes']),
			'url': competition['settings']['contact']['url'],
			'opens': competition['settings']['opens'],
			'withdrawUntil': datetime.fromisoformat(competition['settings']['withdrawUntil']),
			'message1': competition['settings']['extra'],
			'message2': competition['extra'],
			'location_description': competition['location'],
			'links': links,
			'combinations': combinations,
			'venue': venue,
			'serie': serie
		})
		email=email_full
		# email = minify_html.minify(email_full,
		# 					 minify_js=True,
		# 					 minify_css=True,
		# 					 keep_input_type_text_attr=True,
		# 					 do_not_minify_doctype=True,
		# 					 ensure_spec_compliant_unquoted_attribute_values=True,
		# 					 keep_closing_tags=True,
		# 					 keep_html_and_head_opening_tags=True,
		# 					 keep_spaces_between_attributes=True,
		# 					 keep_comments=False,
		# 					 remove_processing_instructions=True)
		filename = "./" + str(id) + ".email"
		logger.debug ("(" + str(id) + "): email generated and stored in: " + str(filename))
		with open(filename, "w") as outfile:
			outfile.write(email)

	except asyncio.CancelledError as e:
		raise e
	except Exception as e:
		logger.error ("Error: " + traceback.format_exc())

	finally:
		return email

def enqueue_email (comp_id: uuid, skaters: list, email_html: str) -> uuid:
	email_uuid = uuid.uuid4()
	ret = prepared_emails.append([email_uuid.bytes, comp_id.bytes, email_html, False, None])
	for skater in skaters:
		emails_skaters.append([email_uuid.bytes, skater])
	prepared_emails.save()
	emails_skaters.save()
	if ret:
		return email_uuid
	else:
		return None

def add_processed_competition(comp_id: uuid, email_id: uuid) -> bool:
	ret = processed_competitions.append([comp_id.bytes, email_id.bytes])
	processed_competitions.save()
	return ret

if __name__ == '__main__':
	logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	asyncio.run(main())