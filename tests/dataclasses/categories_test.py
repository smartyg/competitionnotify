from competitionnotify.dataclasses.categories import CategoryFilterClass, CategoryClass

import unittest
import pytest

import datetime

class TestCategoryClass(unittest.TestCase):
	def test_construct(self):
		test = CategoryClass(gender=0, age=0, ageSub=0)
		self.assertIsInstance(test, CategoryClass)

	def test_constructByDate(self):
		date = datetime.date(1987, 10, 20)
		test = CategoryClass.getCategoryByDate(male=True, date=date)
		self.assertIsInstance(test, CategoryClass)

	def test_constructByText(self):
		test = CategoryClass.getCategoryByString(string="HSA")
		self.assertIsInstance(test, CategoryClass)

	def test_equalTrue(self):
		test1 = CategoryClass(gender=0, age=0, ageSub=0)
		test2 = CategoryClass.getCategoryByString(string="DPF")
		self.assertTrue(test1.equal(test2))

	def test_equalFalse(self):
		test1 = CategoryClass(gender=0, age=0, ageSub=0)
		test2 = CategoryClass.getCategoryByString(string="D55")
		self.assertFalse(test1.equal(test2))

	def test_toString1(self):
		test = CategoryClass.getCategoryByString(string="H55")
		string = test.asString(old_style=False)
		self.assertEqual(string, "H55")

	def test_toString2(self):
		test = CategoryClass.getCategoryByString(string="H55")
		string = test.asString(old_style=True)
		self.assertEqual(string, "HMD")

	def test_toString3(self):
		test = CategoryClass.getCategoryByString(string="HMD")
		string = test.asString(old_style=False)
		self.assertEqual(string, "H55")

	def test_toString4(self):
		test = CategoryClass.getCategoryByString(string="HMD")
		string = test.asString(old_style=True)
		self.assertEqual(string, "HMD")

	def test_toString5(self):
		test = CategoryClass.getCategoryByString(string="H55")
		string = str(test)
		self.assertEqual(string, "H55")

	def test_equalByDate(self):
		date = datetime.date(1987, 10, 20)
		test1 = CategoryClass.getCategoryByDate(male=True, date=date)
		test2 = CategoryClass.getCategoryByString(string="H35")
		self.assertTrue(test1.equal(test2))

	def test_constructFail1(self):
		with pytest.raises(ValueError) as e:
			test = CategoryClass(gender=2, age=0, ageSub=0)

	def test_constructFail2(self):
		with pytest.raises(ValueError) as e:
			test = CategoryClass(gender=0, age=11, ageSub=0)

	def test_constructFail3(self):
		with pytest.raises(ValueError) as e:
			test = CategoryClass(gender=0, age=5, ageSub=4)

	def test_CategoryClass_converter(self):
		test = CategoryClass_converter(string="H55")
		string = str(test)

class TestCategoryFilterClass(unittest.TestCase):
	def fromString(filter_text: str, old_style:bool = False) -> "CategoryFilterClass":