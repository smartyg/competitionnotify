#!/bin/python

import requests
import json
from datetime import datetime
from datetime import timedelta
import time
import logging
import datatable
import uuid

logger = logging.getLogger(__name__)
timer_list = {}
emails_send = []

homeVenueCodes = ["ALK", "AMS"]
categoryCode = ["HPF", "DPF", "HPE", "DPE", "HPD", "DPD", "HPC", "DPC", "HPB", "DPB", "HPA", "DPA", "HC1", "DC1", "HC2", "DC2", "HB1", "DB1", "HB2", "DB2", "HA1", "DA1", "HA2", "DA2", "HN1", "DN1", "HN2", "DN2", "HN3", "DN3", "HN4", "DN4", "HSA", "DSA", "HSB", "DSB", "H40", "D40", "H45", "D45", "H50", "D50", "H55", "D55", "H60", "D60", "H65", "D65", "H70", "D70", "H75", "D75", "H80", "D80"]
disciplineCode = ["SpeedSkating.LongTrack", "SpeedSkating.ShortTrack"]

def main_loop():
	process_competitions_last_run = datetime.min

	with open('emails_send.json', 'r') as file:
		emails_send = json.load(file)

	while True:
		now = datetime.utcnow ()
		logger.info ("new run at " + now.strftime("%d-%m-%Y %H:%M:%S"))

		if now > (process_competitions_last_run + timedelta(days=1)):
			logger.info ("download en verwerk nieuwe data")
			process_competitions_last_run = now
			process_competitions ()
		else:
			for open_date, id in timer_list.items():
				if open_date <= now:
					logger.info ("download en verwerk wedstrijd: " + id)
					process_competition (id)
					time.sleep (10)

	time.sleep (15 * 60)

	return None

def download_json(url):
	logger.debug ("download url: " + url)
	response = requests.get(url)
	if response.status_code == 200:
		j = json.loads(response.content)
		return j
	else:
		logger.error ('Failed to download file')
		return None

def process_competitions():
	competitions = download_json ('https://inschrijven.schaatsen.nl/api/competitions')

	for comp in competitions:
		comp_settings = comp['settings']
		comp_id = uuid.UUID(comp['id'], version=4)
		processed_competitions = get_processed_competitions ()
		if not comp_settings['isClosed']:
			if comp_id.int not in processed_competitions['comp_id']:
				process_competition (comp_id)
				time.sleep (30)
		else:
			timer_list.clear ()
			time_open = datetime.fromisoformat(comp_settings['opens'])
			timer_list[time_open] = comp_id

def find_dict(d, key, value):
	for e in d:
		if key in e:
			if e[key] == value:
				return e
	return None

def process_competition(id):
	logger.info ("Controleren van wedstrijd id: " + str(id))
	url_competition = 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id)
	url_distancecombinations = 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id) + '/distancecombinations'
	url_distancecombinations_settings = 'https://inschrijven.schaatsen.nl/api/competitions/' + str(id) + '/settings/distancecombinations'

	links = {}
	links['subscription'] = 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/inschrijven'
	links['information'] = 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/informatie'
	links['participants'] = 'https://inschrijven.schaatsen.nl/#/wedstrijd/' + str(id) + '/deelnemers'

	competition = download_json (url_competition)

	if competition['settings']['isClosed']:
		logger.warning ("wedstrijd is (nog) niet open")
		return False

	distancecombinations = download_json (url_distancecombinations)
	distancecombinations_settings = download_json (url_distancecombinations_settings)

	test = []
	skaters = []
	distances = []
	all_skaters = load_skaters()

	for d1 in distancecombinations_settings:
		d2 = find_dict (distancecombinations, 'id', d1['distanceCombinationId'])
		#d = d1 | d2
		test.append (d1 | d2)
		skaters_distance = filter_skaters (all_skaters, homeVenueFilter=d1['homeVenueFilter'], categoryFilter=d2['categoryFilter'], clubCodeFilter=d1['clubCodeFilter'], invitees=d1['invitees'], disciplineCodeFilter=None)
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
			distance_entry['distances'].append (distance['value'])

		distances.append (distance_entry)



			   # limitTimeDistanceDiscipline
			   # limitTimeDistanceValue
			   # limitTime
			   # allowedRegistrations
			   # 1=licentiehouders
			   # 9=licentiehouders+active leden
			   # 13=selectie active leden
			   # 4=selectie


	# Serializing json
	json_object = json.dumps(test, indent=2)

	# Writing to sample.json
	with open(str(id) + ".json", "w") as outfile:
		outfile.write(json_object)

	email_html = compose_html_mail (id, links, competition, distances)

	email_id = enqueue_email (id, skaters, email_html)
	add_processed_competition(id, email_id)

def filter_skaters (skaters, homeVenueFilter, categoryFilter, clubCodeFilter, disciplineCodeFilter, invitees):
	result = skaters
	if invitees is not None:
		result = result[:,:]
	if homeVenueFilter is not None:
		homeVenueFilterId = homeVenueCodes.index (homeVenueFilter)
		result = result[f.skater_id in homeVenueFilterId, :]
	if disciplineCodeFilter is not None:
		disciplineCodeFilterId = disciplineCode.index (disciplineCodeFilter)
		result = result[f.discipline in disciplineCodeFilterId, :]
	if clubCodeFilter is not None:
		result = result[f.clubCode in clubCodeFilter, :]

	return result

def compose_html_mail (id, links, competition, distances):
	return str("Hallo")

def enqueue_email (id, skaters, email_html):
	email_uuid = uuid.uuid4()
	return email_uuid

def get_processed_competitions():
	try:
		table = datatable.fread('processed_competitions.jay')
	except (datatable.exceptions.IOError, datatable.exceptions.ValueError):
		table = datatable.Frame(names=["comp_id", "email_id"], types=[datatable.Type.obj64, datatable.Type.obj64])
	return table.to_dict()

def add_processed_competition(comp_id, email_id):
	processed_competitions = get_processed_competitions()
	processed_competitions['comp_id'].append(comp_id.int)
	processed_competitions['email_id'].append(email_id.int)
	table = datatable.Frame(processed_competitions, types=[datatable.Type.obj64, datatable.Type.obj64])
	table.to_jay ('processed_competitions.jay', method='write')

def load_skaters():
	try:
		table = datatable.fread('skaters.jay')
	except (datatable.exceptions.IOError, datatable.exceptions.ValueError):
		table = datatable.Frame(names=["skater_id", "name", "email", "phone", "homeVenue", "clubCode", "category", "discipline"], types=[datatable.Type.obj64, datatable.Type.str64, datatable.Type.str64, datatable.Type.str64, datatable.Type.int8, datatable.Type.int32, datatable.Type.int8, datatable.Type.int8])
	return table

if __name__ == '__main__':
	logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
	main_loop()