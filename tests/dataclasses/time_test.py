import competitionnotify.dataclasses.time as time

import unittest
import pytest

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