import competitionnotify.dataclasses.skater as skater

import json
import datetime
import unittest
import pytest

#class TestAdressClass(unittest.TestCase):


class TestSkaterClass(unittest.TestCase):
	def test_convertor1(self):
		json_string = '{"personName":{"initials":"M.","firstName":"Martijn","surnamePrefix":null,"surname":"Goedhart"},"personBirthDate":"0001-01-01T00:00:00Z","key":"10156390","flags":10,"season":2024,"sponsor":null,"club":{"countryCode":"NED","code":6640,"shortName":"YC HGI","shortCode":"YCHGI","fullName":"IJsclub Hard Gaat ie"},"validFrom":"2025-02-24T00:00:00Z","validTo":"2026-05-24T00:00:00Z","category":"HSB","legNumber":null,"number":null,"venueCode":"AMS","transponder1":"TZ-75324","transponder2":null}'
		json_data = json.loads(json_string)
		test = skater.SkaterClass_converter(data=json_data)
		self.assertIsInstance(test, skater.SkaterClass)

	def test_convertor2(self):
		json_string = '{"personName":{"initials":"M.","firstName":"Martijn","surnamePrefix":null,"surname":"Goedhart"},"personBirthDate":"0001-01-01T00:00:00Z","key":"10156390","flags":10,"season":2024,"sponsor":null,"club":{"countryCode":"NED","code":6640,"shortName":"YC HGI","shortCode":"YCHGI","fullName":"IJsclub Hard Gaat ie"},"validFrom":"2025-02-24T00:00:00Z","validTo":"2026-05-24T00:00:00Z","category":"HSB","legNumber":null,"number":null,"venueCode":"AMS","transponder1":"TZ-75324","transponder2":null}'
		json_data = json.loads(json_string)

		json_data['mailOptions'] = {}
		json_data['mailOptions']['emailAddress'] = "test.address@example.com"
		json_data['mailOptions']['homeVenue'] = True
		json_data['mailOptions']['venues'] = ["AMS", "ALK", "HRN"]
		json_data['mailOptions']['disciplines'] = ["SpeedSkating.LongTrack", "SpeedSkating.Marathon"]

		test = skater.SkaterClass_converter(data=json_data)
		self.assertIsInstance(test, skater.SkaterClass)

	def test_license(self):
		json_string = '{"personName":{"initials":"M.","firstName":"Martijn","surnamePrefix":null,"surname":"Goedhart"},"personBirthDate":"0001-01-01T00:00:00Z","key":"10156390","flags":10,"season":2024,"sponsor":null,"club":{"countryCode":"NED","code":6640,"shortName":"YC HGI","shortCode":"YCHGI","fullName":"IJsclub Hard Gaat ie"},"validFrom":"2025-02-24T00:00:00Z","validTo":"2026-05-24T00:00:00Z","category":"HSB","legNumber":null,"number":null,"venueCode":"AMS","transponder1":"TZ-75324","transponder2":null}'
		json_data = json.loads(json_string)
		test = skater.SkaterClass_converter(data=json_data)
		self.assertIsInstance(test, skater.SkaterClass)

		date = datetime.datetime(2025, 2, 23, hour=23, minute=59, second=59, microsecond=999, tzinfo=datetime.UTC)
		self.assertFalse(test.isLicenseValid(date))

		date = datetime.datetime(2025, 2, 24, hour=0, minute=0, second=0, microsecond=1, tzinfo=datetime.UTC)
		self.assertTrue(test.isLicenseValid(date))

		date = datetime.datetime(2026, 5, 23, hour=23, minute=59, second=59, microsecond=999, tzinfo=datetime.UTC)
		self.assertTrue(test.isLicenseValid(date))

		date = datetime.datetime(2026, 5, 24, hour=0, minute=0, second=0, microsecond=1, tzinfo=datetime.UTC)
		self.assertFalse(test.isLicenseValid(date))
