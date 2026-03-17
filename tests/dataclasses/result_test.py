import competitionnotify.classes.result as result

import unittest
import pytest

import competitionnotify.utils.utils as utils
import competitionnotify.classes.discipline as discipline

class TestBestTimesClass(unittest.TestCase):
	pass
	# def test_construct1(self):
	# 	test = discipline.DisciplineClass(discipline=0)
	# 	self.assertIsInstance(test, discipline.DisciplineClass)
	# 	self.assertEqual(test.asString(), "SpeedSkating.Inline")
	# 	self.assertTrue(test.isValid())
	# 	self.assertFalse(test.isUnknown())
	def test_convertor1(self):
		data = {'skater': 11244, 'records': [{'distance': 500, 'time': '41,08', 'date': '2016-02-13', 'location': 'Inzell (GER)'}, {'distance': 1000, 'time': '1.21,63', 'date': '2016-02-02', 'location': 'Heerenveen (NED)'}, {'distance': 1500, 'time': '2.00,92', 'date': '2016-02-20', 'location': 'Inzell (GER)'}, {'distance': 3000, 'time': '4.20,95', 'date': '2016-02-21', 'location': 'Inzell (GER)'}, {'distance': 5000, 'time': '7.42,05', 'date': '2016-03-23', 'location': 'Heerenveen (NED)'}, {'distance': 10000, 'time': '16.05,65', 'date': '2016-03-24', 'location': 'Heerenveen (NED)'}]}
		test = utils.class_factory(data, result.BestTimesClass, int)
		#test = result.BestTimesClass[int](**data)
		self.assertIsInstance(test, result.BestTimesClass)
		self.assertEqual(test.getSkater(), 11244)
		self.assertIs(test.getSkaterIdType(), int)
		self.assertIsNot(test.getSkaterIdType(), str)

	def test_construct1(self):
		data = {'discipline': 1}
		test = utils.class_factory(data, discipline.DisciplineClass)
		#test = result.BestTimesClass[int](**data)
		#self.assertIsInstance(test, result.BestTimesClass)
		#test = discipline.DisciplineClass(discipline=0)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.LongTrack")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())