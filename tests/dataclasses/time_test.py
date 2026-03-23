import competitionnotify.classes.time as time

import unittest
import pytest
import json

class TestTimeClass(unittest.TestCase):
	def test_construct1(self):
		test = time.TimeClass(hours=0, minutes=0, seconds=0, miliseconds=0)
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getTime(), 0.0)
		self.assertEqual(test.getHours(), 0)
		self.assertEqual(test.getMinutes(), 0)
		self.assertEqual(test.getSeconds(), 0)
		self.assertEqual(test.getMiliseconds(), 0)

	def test_construct2(self):
		test = time.TimeClass(hours=23, minutes=59, seconds=59, miliseconds=999)
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getTime(), 86399.999)
		self.assertEqual(test.getHours(), 23)
		self.assertEqual(test.getMinutes(), 59)
		self.assertEqual(test.getSeconds(), 59)
		self.assertEqual(test.getMiliseconds(), 999)

	def test_constructInvalid1(self):
		with pytest.raises(ValueError) as e:
			test = time.TimeClass(hours=23, minutes=59, seconds=59, miliseconds=1000)

	def test_constructInvalid2(self):
		with pytest.raises(ValueError) as e:
			test = time.TimeClass(hours=23, minutes=59, seconds=60, miliseconds=999)

	def test_constructInvalid3(self):
		with pytest.raises(ValueError) as e:
			test = time.TimeClass(hours=23, minutes=60, seconds=59, miliseconds=999)

	def test_constructInvalid4(self):
		with pytest.raises(ValueError) as e:
			test = time.TimeClass(hours=24, minutes=59, seconds=59, miliseconds=999)

	def test_fromString1(self):
		test = time.TimeClass.from_string("12:34:56")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 12)
		self.assertEqual(test.getMinutes(), 34)
		self.assertEqual(test.getSeconds(), 56)
		self.assertEqual(test.getMiliseconds(), 0)

	def test_fromString2(self):
		test = time.TimeClass.from_string("12:34:56.7")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 12)
		self.assertEqual(test.getMinutes(), 34)
		self.assertEqual(test.getSeconds(), 56)
		self.assertEqual(test.getMiliseconds(), 700)

	def test_fromString3(self):
		test = time.TimeClass.from_string("12:34:56.78")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 12)
		self.assertEqual(test.getMinutes(), 34)
		self.assertEqual(test.getSeconds(), 56)
		self.assertEqual(test.getMiliseconds(), 780)

	def test_fromString4(self):
		test = time.TimeClass.from_string("12:34:56.789")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 12)
		self.assertEqual(test.getMinutes(), 34)
		self.assertEqual(test.getSeconds(), 56)
		self.assertEqual(test.getMiliseconds(), 789)

	def test_fromString1(self):
		test = time.TimeClass.from_string("12,3")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 0)
		self.assertEqual(test.getMinutes(), 0)
		self.assertEqual(test.getSeconds(), 12)
		self.assertEqual(test.getMiliseconds(), 300)

	def test_fromString2(self):
		test = time.TimeClass.from_string("12,34")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 0)
		self.assertEqual(test.getMinutes(), 0)
		self.assertEqual(test.getSeconds(), 12)
		self.assertEqual(test.getMiliseconds(), 340)

	def test_fromString3(self):
		test = time.TimeClass.from_string("12,345")
		self.assertIsInstance(test, time.TimeClass)
		self.assertEqual(test.getHours(), 0)
		self.assertEqual(test.getMinutes(), 0)
		self.assertEqual(test.getSeconds(), 12)
		self.assertEqual(test.getMiliseconds(), 345)

	def test_repr(self):
		test1 = time.TimeClass.from_string("12,345")
		self.assertIsInstance(test1, time.TimeClass)
		string = repr(test1)
		self.assertIsInstance(string, str)
		test2 = time.TimeClass.from_string(string)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertEqual(test2.getHours(), 0)
		self.assertEqual(test2.getMinutes(), 0)
		self.assertEqual(test2.getSeconds(), 12)
		self.assertEqual(test2.getMiliseconds(), 345)

	def test_hasEqual(self):
		test1 = time.TimeClass.from_string("12:34:56.789")
		test2 = time.TimeClass.from_string("12:34:56.789")
		self.assertIsInstance(test1, time.TimeClass)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertTrue(test1 == test2)

	def test_notEqual1(self):
		test1 = time.TimeClass.from_string("12:34:56.789")
		test2 = time.TimeClass.from_string("01:23:45.678")
		self.assertIsInstance(test1, time.TimeClass)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertTrue(test1 != test2)

	def test_notEqual2(self):
		test1 = time.TimeClass.from_string("12:34:56.789")
		test2 = time.TimeClass()
		self.assertIsInstance(test1, time.TimeClass)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertTrue(test1 != test2)

	def test_lessThen1(self):
		test1 = time.TimeClass.from_string("01:23:45.678")
		test2 = time.TimeClass.from_string("12:34:56.789")
		self.assertIsInstance(test1, time.TimeClass)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertTrue(test1 < test2)

	def test_lessThen2(self):
		test1 = time.TimeClass.from_string("01:23:45.678")
		test2 = time.TimeClass.from_string("01:23:45.678")
		self.assertIsInstance(test1, time.TimeClass)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertFalse(test1 < test2)

	def test_hashable(self):
		test = time.TimeClass.from_string("12:34:56.789")
		self.assertIsInstance(test, time.TimeClass)
		self.assertIsInstance(hash(test), int)

	def test_json(self):
		test1 = time.TimeClass.from_string("12:34:56.789")
		self.assertIsInstance(test1, time.TimeClass)
		json_string = test1.json()
		self.assertIsInstance(json_string, str)

		d = json.loads(json_string)
		test2 = time.TimeClass(**d)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertTrue(test1 == test2)

	def test_serializable(self):
		test1 = time.TimeClass.from_string("12:34:56.789")
		self.assertIsInstance(test1, time.TimeClass)
		s = test1.serialize()

		test2 = time.TimeClass.deserialize(s)
		self.assertIsInstance(test2, time.TimeClass)
		self.assertTrue(test1 == test2)