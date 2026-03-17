import competitionnotify.classes.distance_combination as distance_combination

import json
import unittest
import pytest
import os
import os.path
import uuid

import competitionnotify.classes.distance as distance
import competitionnotify.classes.categories as categories

class TestDistancecombinationClass(unittest.TestCase):

	def test_convertor1(self):
		json_string = '[{"id": "a5614fea-1343-47ca-987f-87c93687723d", "number": 1, "name": "100 - 500 meter pupil", "classFilter": null, "categoryFilter": "*P*", "classificationWeight": 100, "distances": [{"id": "a2effc37-49c9-4f39-9fc5-899ede997207", "discipline": "SpeedSkating.LongTrack.PairsDistance.Individual", "number": 1, "value": 100, "valueQuantity": 0, "name": "100 meter (100-500)", "starts": "2025-02-15T17:00:00Z"}, {"id": "71331f28-5e2b-4488-bc16-8d5d5a936fd7", "discipline": "SpeedSkating.LongTrack.PairsDistance.Individual", "number": 2, "value": 500, "valueQuantity": 0, "name": "500 meter (100-500)", "starts": "2025-02-15T17:00:00Z"}], "starts": null, "competitorsTotal": 32, "competitorsPending": 2, "competitorsConfirmed": 29, "competitorsWithdrawn": 1, "onlyCountFastestDistanceWhenSameLength": false}]'
		json_data = json.loads(json_string)

		test = distance_combination.DistancecombinationsClass(distancecombinations=json_data)
		json_data_len: int = len(json_data)
		self.assertIsInstance(test, distance_combination.DistancecombinationsClass)
		self.assertEqual(len(test._distancecombinations), json_data_len)

		dc = test._distancecombinations[0]
		self.assertIsInstance(dc, distance_combination.DistancecombinationClass)
		self.assertEqual(str(dc.getId()), "a5614fea-1343-47ca-987f-87c93687723d")
		self.assertEqual(str(dc.getName()), "100 - 500 meter pupil")
		cat = dc.getCategoryFilter()
		self.assertIsInstance(cat, categories.CategoryFilterClass)
		self.assertTrue(cat.hasCategory("HPF"))
		self.assertTrue(cat.hasCategory("HPA"))
		self.assertTrue(cat.hasCategory("DPF"))
		self.assertTrue(cat.hasCategory("DPA"))
		self.assertFalse(cat.hasCategory("HC1"))
		self.assertFalse(cat.hasCategory("D90"))

	def test_convertor2(self):
		json_string = '[{"id": "b3ee9ecd-5db5-4e27-b094-737296a8c3a3", "number": 1, "name": "500-1500", "classFilter": null, "categoryFilter": "D*,H*", "classificationWeight": 500, "distances": [{"id": "752e5c6e-ffdc-4da4-a6c7-8cda4461bd37", "discipline": "SpeedSkating.LongTrack.PairsDistance.Individual", "number": 1, "value": 500, "valueQuantity": 0, "name": "500 meter", "starts": "2025-03-09T18:20:00Z"}, {"id": "ea4f72ff-1753-4b12-b76b-b0fc3a40894a", "discipline": "SpeedSkating.LongTrack.PairsDistance.Individual", "number": 3, "value": 1500, "valueQuantity": 0, "name": "1500 meter", "starts": "2025-03-09T18:20:00Z"}], "starts": null, "competitorsTotal": 40, "competitorsPending": 0, "competitorsConfirmed": 36, "competitorsWithdrawn": 4, "onlyCountFastestDistanceWhenSameLength": false}, {"id": "45adc84d-aa25-4b46-8448-8ab07c7ade17", "number": 2, "name": "Knsb test-event", "classFilter": null, "categoryFilter": "DPA,DC*,DB*,DA*,DN*,DS*,D4*,D5*,D6*,D7*,D8*,D9*,HPA,HC*,HB*,HA*,HN*,HS*,H4*,H5*,H6*,H7*,H8*,H9*", "classificationWeight": 500, "distances": [{"id": "e2f8cba4-f876-47a8-8bc5-7ec6b07ee84d", "discipline": "SpeedSkating.LongTrack.PairsDistance.Individual", "number": 2, "value": 500, "valueQuantity": 0, "name": "Knsb- test event 500 meter", "starts": "2025-03-09T18:20:00Z"}], "starts": null, "competitorsTotal": 7, "competitorsPending": 0, "competitorsConfirmed": 7, "competitorsWithdrawn": 0, "onlyCountFastestDistanceWhenSameLength": false}]'
		json_data = json.loads(json_string)

		test = distance_combination.DistancecombinationsClass(distancecombinations=json_data)
		json_data_len: int = len(json_data)
		self.assertIsInstance(test, distance_combination.DistancecombinationsClass)
		self.assertEqual(len(test._distancecombinations), json_data_len)
		for dc in test._distancecombinations:
			self.assertIsInstance(dc, distance_combination.DistancecombinationClass)
			self.assertIsInstance(dc.getId(), uuid.UUID)
			self.assertIsInstance(dc.getCategoryFilter(), categories.CategoryFilterClass)

			for d in dc._distances:
				self.assertIsInstance(d, distance.DistanceClass)
				self.assertIsInstance(d.getId(), uuid.UUID)
				self.assertIsInstance(d.getDistance(), distance.DistanceValueClass)

	def test_loadRealData(self):
		test_path: str = "./test_data/"
		for f in os.listdir(test_path):
			test_file: str = os.path.join(test_path, f)
			if os.path.isfile(test_file) and test_file.endswith("-distancecombinations.json"):
				json_data: dict[str, typing.Any]
				print("Process file: " + test_file)
				with open(test_file, "r") as f:
					json_data = json.load(f)
				json_data_len: int = len(json_data)
				test = distance_combination.DistancecombinationsClass(distancecombinations=json_data)
				self.assertIsInstance(test, distance_combination.DistancecombinationsClass)
				self.assertEqual(len(test._distancecombinations), json_data_len)
				for s in test._distancecombinations:
					self.assertIsInstance(s, distance_combination.DistancecombinationClass)
					self.assertIsInstance(s.getId(), uuid.UUID)

class TestDistancecombinationsettingClass(unittest.TestCase):
	def test_loadRealData(self):
		test_path: str = "./test_data/"
		for f in os.listdir(test_path):
			test_file: str = os.path.join(test_path, f)
			if os.path.isfile(test_file) and test_file.endswith("-distancecombinationsettings.json"):
				json_data: list[dict[str, typing.Any]]
				print("Process file: " + test_file)
				with open(test_file, "r") as f:
					json_data = json.load(f)
				json_data_len: int = len(json_data)
				test = distance_combination.DistancecombinationsettingsClass(distancecombinationsettings=json_data)
				self.assertIsInstance(test, distance_combination.DistancecombinationsettingsClass)
				self.assertEqual(len(test._distancecombinationsettings), json_data_len)
				for s in test._distancecombinationsettings:
					self.assertIsInstance(s, distance_combination.DistancecombinationsettingClass)
					self.assertIsInstance(s.getId(), uuid.UUID)