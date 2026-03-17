import competitionnotify.classes.distance as distance

import unittest
import pytest
import json

class TestDistanceValueClass(unittest.TestCase):
	def test_construct1(self):
		test = distance.DistanceValueClass(distance=500)
		self.assertIsInstance(test, distance.DistanceValueClass)
		self.assertTrue(test.isValidDistance())

	def test_construct2(self):
		test = distance.DistanceValueClass(distance=50)
		self.assertIsInstance(test, distance.DistanceValueClass)
		self.assertFalse(test.isValidDistance())

	def test_hash(self):
		test = distance.DistanceValueClass(distance=500)
		self.assertIsInstance(test, distance.DistanceValueClass)
		self.assertIsInstance(hash(test), int)

	def test_hasEqual(self):
		test1 = distance.DistanceValueClass(distance=500)
		test2 = distance.DistanceValueClass(distance=500)
		self.assertIsInstance(test1, distance.DistanceValueClass)
		self.assertIsInstance(test2, distance.DistanceValueClass)
		self.assertTrue(test1 == test2)

	def test_notEqual(self):
		test1 = distance.DistanceValueClass(distance=500)
		test2 = distance.DistanceValueClass(distance=1500)
		self.assertIsInstance(test1, distance.DistanceValueClass)
		self.assertIsInstance(test2, distance.DistanceValueClass)
		self.assertTrue(test1 != test2)

	def test_hashable(self):
		test = distance.DistanceValueClass(distance=500)
		self.assertIsInstance(test, distance.DistanceValueClass)
		self.assertIsInstance(hash(test), int)

	def test_json(self):
		test1 = distance.DistanceValueClass(distance=500)
		self.assertIsInstance(test1, distance.DistanceValueClass)
		json_string = test1.json()
		self.assertIsInstance(json_string, str)
		self.assertTrue(len(json_string) > 0)

		d = json.loads(json_string)
		test2 = distance.DistanceValueClass(**d)
		self.assertIsInstance(test2, distance.DistanceValueClass)
		self.assertTrue(test1 == test2)

	def test_serializable(self):
		test1 = distance.DistanceValueClass(distance=500)
		self.assertIsInstance(test1, distance.DistanceValueClass)
		s = test1.serialize()

		test2 = distance.DistanceValueClass.deserialize(s)
		self.assertIsInstance(test1, distance.DistanceValueClass)
		self.assertTrue(test1 == test2)

#class TestDistanceClass(unittest.TestCase):