import competitionnotify.dataclasses.discipline as discipline

import unittest
import pytest

class TestDisciplineClass(unittest.TestCase):
	def test_construct1(self):
		test = discipline.DisciplineClass(discipline=0)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Inline")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())

	def test_construct2(self):
		test = discipline.DisciplineClass(discipline=1)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.LongTrack")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())

	def test_construct3(self):
		test = discipline.DisciplineClass(discipline=2)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Marathon")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())

	def test_construct4(self):
		test = discipline.DisciplineClass(discipline=3)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.ShortTrack")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())

	def test_construct5(self):
		with pytest.raises(ValueError) as e:
			test = discipline.DisciplineClass(discipline=4)

	def test_construct5(self):
		test = discipline.DisciplineClass(discipline=-1)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Unknown")
		self.assertFalse(test.isValid())
		self.assertTrue(test.isUnknown())

	def test_constructByString(self):
		for v in ("SpeedSkating.Inline", "SpeedSkating.LongTrack", "SpeedSkating.Marathon", "SpeedSkating.ShortTrack"):
			test = discipline.DisciplineClass.getDisciplineByString(v)
			self.assertIsInstance(test, discipline.DisciplineClass)
			self.assertEqual(test.asString(), v)
			self.assertTrue(test.isValid())
			self.assertFalse(test.isUnknown())

	def test_constructByStringInvalid(self):
		test = discipline.DisciplineClass.getDisciplineByString("InvalidString")
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Unknown")
		self.assertFalse(test.isValid())
		self.assertTrue(test.isUnknown())


	def test_converter1(self):
		test = discipline.DisciplineClass_converter("SpeedSkating.LongTrack")
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.LongTrack")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())

	def test_converter2(self):
		test = discipline.DisciplineClass_converter("InvalidString")
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Unknown")
		self.assertFalse(test.isValid())
		self.assertTrue(test.isUnknown())

	def test_converter3(self):
		test = discipline.DisciplineClass_converter(None)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Unknown")
		self.assertFalse(test.isValid())
		self.assertTrue(test.isUnknown())

	def test_converter4(self):
		cls = discipline.DisciplineClass(discipline=0)
		test = discipline.DisciplineClass_converter(cls)
		self.assertIsInstance(test, discipline.DisciplineClass)
		self.assertEqual(test.asString(), "SpeedSkating.Inline")
		self.assertTrue(test.isValid())
		self.assertFalse(test.isUnknown())
		self.assertEqual(test, cls)


	def test_converter_list1(self):
		test = discipline.DisciplineClassList_converter("SpeedSkating.LongTrack")
		self.assertIsInstance(test, list)
		self.assertEqual(len(test), 1)
		item = test[0]
		self.assertIsInstance(item, discipline.DisciplineClass)
		self.assertEqual(item.asString(), "SpeedSkating.LongTrack")
		self.assertTrue(item.isValid())
		self.assertFalse(item.isUnknown())

	def test_converter_list2(self):
		test = discipline.DisciplineClassList_converter("InvalidString")
		self.assertIsInstance(test, list)
		self.assertEqual(len(test), 1)
		item = test[0]
		self.assertIsInstance(item, discipline.DisciplineClass)
		self.assertEqual(item.asString(), "SpeedSkating.Unknown")
		self.assertFalse(item.isValid())
		self.assertTrue(item.isUnknown())

	def test_converter_list3(self):
		test = discipline.DisciplineClassList_converter(None)
		self.assertIsInstance(test, list)
		self.assertEqual(len(test), 0)

	def test_converter_list4(self):
		cls1 = discipline.DisciplineClass(discipline=0)
		cls2 = discipline.DisciplineClass(discipline=2)
		test = discipline.DisciplineClassList_converter([cls1, cls2])
		self.assertIsInstance(test, list)
		self.assertEqual(len(test), 2)

		item = test[0]
		self.assertIsInstance(item, discipline.DisciplineClass)
		self.assertEqual(item.asString(), "SpeedSkating.Inline")
		self.assertTrue(item.isValid())
		self.assertFalse(item.isUnknown())
		self.assertEqual(item, cls1)

		item = test[1]
		self.assertIsInstance(item, discipline.DisciplineClass)
		self.assertEqual(item.asString(), "SpeedSkating.Marathon")
		self.assertTrue(item.isValid())
		self.assertFalse(item.isUnknown())
		self.assertEqual(item, cls2)
