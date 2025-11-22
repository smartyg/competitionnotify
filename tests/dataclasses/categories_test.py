import competitionnotify.dataclasses.categories as categories # CategoryFilterClass, CategoryClass

import unittest
import pytest

import datetime

class TestCategoryClass(unittest.TestCase):
	def test_construct(self):
		test = categories.CategoryClass(gender=0, age=0, ageSub=0)
		self.assertIsInstance(test, categories.CategoryClass)

	def test_constructByDate(self):
		date = datetime.date(1987, 10, 20)
		test = categories.CategoryClass.getCategoryByDate(male=True, date=date)
		self.assertIsInstance(test, categories.CategoryClass)

	def test_constructByText(self):
		test = categories.CategoryClass.getCategoryByString(string="HSA")
		self.assertIsInstance(test, categories.CategoryClass)

	def test_equalTrue(self):
		test1 = categories.CategoryClass(gender=0, age=0, ageSub=0)
		test2 = categories.CategoryClass.getCategoryByString(string="DPF")
		self.assertTrue(test1.equal(test2))

	def test_equalFalse(self):
		test1 = categories.CategoryClass(gender=0, age=0, ageSub=0)
		test2 = categories.CategoryClass.getCategoryByString(string="D55")
		self.assertFalse(test1.equal(test2))

	def test_toString1(self):
		test = categories.CategoryClass.getCategoryByString(string="H55")
		string = test.asString(old_style=False)
		self.assertEqual(string, "H55")

	def test_toString2(self):
		test = categories.CategoryClass.getCategoryByString(string="H55")
		string = test.asString(old_style=True)
		self.assertEqual(string, "HMD")

	def test_toString3(self):
		test = categories.CategoryClass.getCategoryByString(string="HMD")
		string = test.asString(old_style=False)
		self.assertEqual(string, "H55")

	def test_toString4(self):
		test = categories.CategoryClass.getCategoryByString(string="HMD")
		string = test.asString(old_style=True)
		self.assertEqual(string, "HMD")

	def test_toString5(self):
		test = categories.CategoryClass.getCategoryByString(string="H55")
		string = str(test)
		self.assertEqual(string, "H55")

	def test_equalByDate(self):
		date = datetime.date(1987, 10, 20)
		test1 = categories.CategoryClass.getCategoryByDate(male=True, date=date)
		test2 = categories.CategoryClass.getCategoryByString(string="H35")
		self.assertTrue(test1.equal(test2))

	def test_constructFail1(self):
		with pytest.raises(ValueError) as e:
			test = categories.CategoryClass(gender=2, age=0, ageSub=0)

	def test_constructFail2(self):
		with pytest.raises(ValueError) as e:
			test = categories.CategoryClass(gender=0, age=12, ageSub=0)

	def test_constructFail3(self):
		with pytest.raises(ValueError) as e:
			test = categories.CategoryClass(gender=0, age=5, ageSub=4)

	def test_CategoryClass_converter(self):
		test = categories.CategoryClass_converter(data="H55")
		string = str(test)

class TestCategoryFilterClass(unittest.TestCase):
	def test_constructByText1(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		num = test.numberOfCategories()
		self.assertEqual(num, 60)

	def test_constructByText2(self):
		test = categories.CategoryFilterClass.fromString("D*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		num = test.numberOfCategories()
		self.assertEqual(num, 30)
		b = test.hasCategory("DPA")
		self.assertTrue(b)
		b = test.hasCategory("HPA")
		self.assertFalse(b)

	def test_constructByText3(self):
		test = categories.CategoryFilterClass.fromString("D*,H*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		num = test.numberOfCategories()
		self.assertEqual(num, 60)

	def test_constructByText4(self):
		test = categories.CategoryFilterClass.fromString("?P?")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		num = test.numberOfCategories()
		self.assertEqual(num, 12)

	def test_constructByText5(self):
		test = categories.CategoryFilterClass.fromString("HC*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		num = test.numberOfCategories()
		self.assertEqual(num, 2)

	def test_constructByText6(self):
		test = categories.CategoryFilterClass.fromString("HC2")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		num = test.numberOfCategories()
		self.assertEqual(num, 1)
		b = test.hasCategory("HC2")
		self.assertTrue(b)
		b = test.hasCategory("HC1")
		self.assertFalse(b)

	def test_hasCategory1(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)

		for g in categories.CategoryBase.getGenderPosibilities():
			for a in categories.CategoryBase.getAgePosibilities():
				for s in categories.CategoryBase.getAgeSubPosibilities(a):
					c = categories.CategoryClass(gender=g, age=a, ageSub=s)
					self.assertIsInstance(c, categories.CategoryClass)
					b = test.hasCategory(c)
					self.assertTrue(b)

	def test_hasCategory2(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)

		for g in categories.CategoryBase.getGenderPosibilities():
			for a in categories.CategoryBase.getAgePosibilities():
				for s in categories.CategoryBase.getAgeSubPosibilities(a):
					c = categories.CategoryClass(gender=g, age=a, ageSub=s)
					self.assertIsInstance(c, categories.CategoryClass)
					string = c.asString(False)
					b = test.hasCategory(string)
					self.assertTrue(b)

	def test_hasCategory3(self):
		test = categories.CategoryFilterClass.fromString("H*")
		self.assertIsInstance(test, categories.CategoryFilterClass)

		for a in categories.CategoryBase.getAgePosibilities():
			for s in categories.CategoryBase.getAgeSubPosibilities(a):
				c = categories.CategoryClass(gender=1, age=a, ageSub=s)
				self.assertIsInstance(c, categories.CategoryClass)
				b = test.hasCategory(c)
				self.assertTrue(b)

				c = categories.CategoryClass(gender=0, age=a, ageSub=s)
				self.assertIsInstance(c, categories.CategoryClass)
				b = test.hasCategory(c)
				self.assertFalse(b)

	def test_constructByText1(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		with pytest.raises(ValueError) as e:
			b= test.hasCategory("INV")
