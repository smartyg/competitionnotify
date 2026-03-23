import competitionnotify.classes.distance_combination_competitors as distance_combination_competitors

import json
import unittest
import pytest
import os
import os.path
import uuid

import competitionnotify.classes.categories as categories

class TestCompetitorClass(unittest.TestCase):
	def test_convertor1(self):
		json_string = '{"listId": "d9a6d02d-28eb-4ee8-8f74-899772bebb60", "startNumber": 3, "legNumber": null, "nationalityCode": "NED", "licenseDiscipline": "SpeedSkating.LongTrack", "licenseKey": "10156390", "licenseFlags": 10, "status": 1, "category": "HSB", "class": null, "sponsor": null, "clubCountryCode": "NED", "clubCode": 6640, "clubShortName": "YC HGI", "clubShortCode": "YCHGI", "clubFullName": "IJsclub Hard Gaat ie", "from": "LANDSMEER", "transponder1": "TZ-75324", "transponder2": null, "organizationTransponder1": null, "organizationTransponder2": null, "fullName": "Martijn Goedhart", "shortName": "Goedhart", "added": "2026-02-01T15:14:28.635221Z", "source": 0, "typeName": "PersonCompetitor", "hideNameOnCompetitorsList": null, "id": "569a49d9-b463-4f7c-a5ef-6b6213bcdef7", "gender": 0}'
		json_data = json.loads(json_string)

		test = distance_combination_competitors.CompetitorClass_converter(data=json_data)
		self.assertIsInstance(test, distance_combination_competitors.CompetitorClass)
		self.assertEqual(str(test.getId()), "569a49d9-b463-4f7c-a5ef-6b6213bcdef7")
		self.assertEqual(str(test.getName()), "Martijn Goedhart")
		self.assertEqual(test.getCategory().asString(), "H35")

class TestDistanceCombinationCompetitorClass(unittest.TestCase):
	def test_convertor1(self):
		json_string = '{"competitor": {"listId": "d9a6d02d-28eb-4ee8-8f74-899772bebb60", "startNumber": 3, "legNumber": null, "nationalityCode": "NED", "licenseDiscipline": "SpeedSkating.LongTrack", "licenseKey": "10156390", "licenseFlags": 10, "status": 1, "category": "HSB", "class": null, "sponsor": null, "clubCountryCode": "NED", "clubCode": 6640, "clubShortName": "YC HGI", "clubShortCode": "YCHGI", "clubFullName": "IJsclub Hard Gaat ie", "from": "LANDSMEER", "transponder1": "TZ-75324", "transponder2": null, "organizationTransponder1": null, "organizationTransponder2": null, "fullName": "Martijn Goedhart", "shortName": "Goedhart", "added": "2026-02-01T15:14:28.635221Z", "source": 0, "typeName": "PersonCompetitor", "hideNameOnCompetitorsList": null, "id": "569a49d9-b463-4f7c-a5ef-6b6213bcdef7", "gender": 0}, "reserve": null, "status": 1}'
		json_data = json.loads(json_string)

		test = distance_combination_competitors.DistanceCombinationCompetitorClass_converter(data=json_data)
		self.assertIsInstance(test, distance_combination_competitors.DistanceCombinationCompetitorClass)
		self.assertTrue(test.isConfirmed())
		self.assertFalse(test.isWithdrawn())
		self.assertFalse(test.isNotConfirmed())
		self.assertFalse(test.isReserve())
		self.assertIsInstance(test.getCompetitor(), distance_combination_competitors.CompetitorClass)
		self.assertEqual(str(test.getCompetitor().getId()), "569a49d9-b463-4f7c-a5ef-6b6213bcdef7")

class TestCompetitorsClass(unittest.TestCase):
	def test_loadRealData(self):
		test_path: str = "./test_data/2025-2026"
		for f in os.listdir(test_path):
			test_file: str = os.path.join(test_path, f)
			if os.path.isfile(test_file) and test_file.endswith("-competitors.json"):
				json_data: list[dict[str, typing.Any]]
				print("Process file: " + test_file)
				with open(test_file, "r") as f:
					json_data = json.load(f)
				json_data_len: int = len(json_data)
				test = distance_combination_competitors.CompetitorsClass(distance_combination_competitors=json_data)
				self.assertIsInstance(test, distance_combination_competitors.CompetitorsClass)
				self.assertEqual(len(test._distance_combination_competitors), json_data_len)
				for s in test._distance_combination_competitors:
					self.assertIsInstance(s, distance_combination_competitors.DistanceCombinationCompetitorsClass)
					self.assertIsInstance(s.getId(), uuid.UUID)
					for c1 in s._competitors:
						c2 = c1._competitor
						self.assertIsInstance(c2, distance_combination_competitors.CompetitorClass)
						self.assertIsInstance(c2.getId(), uuid.UUID)