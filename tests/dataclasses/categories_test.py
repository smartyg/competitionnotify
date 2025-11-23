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

	def test_constructByTextInvalid(self):
		test = categories.CategoryClass.getCategoryByString(string="ABC")
		self.assertIsNone(test)

	def test_equalTrue(self):
		test1 = categories.CategoryClass(gender=0, age=0, ageSub=0)
		test2 = categories.CategoryClass.getCategoryByString(string="DPF")
		self.assertTrue(test1.equal(test2))

	def test_equalFalse(self):
		test1 = categories.CategoryClass(gender=0, age=0, ageSub=0)
		test2 = categories.CategoryClass.getCategoryByString(string="D55")
		self.assertFalse(test1.equal(test2))

	def test_toString1(self):
		category_text = "H55"
		test = categories.CategoryClass.getCategoryByString(string=category_text)
		self.assertEqual(test.asString(old_style=False), category_text)

	def test_toString2(self):
		category_text = "H55"
		category_text_old = "HMD"
		test = categories.CategoryClass.getCategoryByString(string=category_text)
		self.assertEqual(test.asString(old_style=True), category_text_old)

	def test_toString3(self):
		category_text = "H55"
		category_text_old = "HMD"
		test = categories.CategoryClass.getCategoryByString(string=category_text_old)
		self.assertEqual(test.asString(old_style=False), category_text)

	def test_toString4(self):
		category_text = "HMD"
		test = categories.CategoryClass.getCategoryByString(string="HMD")
		self.assertEqual(test.asString(old_style=True), category_text)

	def test_toString5(self):
		category_text = "H55"
		test = categories.CategoryClass.getCategoryByString(string=category_text)
		self.assertEqual(str(test), category_text)

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
		category_text = "H55"
		test = categories.CategoryClass_converter(data=category_text)
		self.assertIsInstance(test, categories.CategoryClass)
		self.assertEqual(str(test), category_text)

class TestCategoryFilterClass(unittest.TestCase):
	def test_constructByText1(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 60)

	def test_constructByText2(self):
		test = categories.CategoryFilterClass.fromString("D*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 30)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertFalse(test.hasCategory("HPA"))

	def test_constructByText3(self):
		test = categories.CategoryFilterClass.fromString("D*,H*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 60)

	def test_constructByText4(self):
		test = categories.CategoryFilterClass.fromString("?P?")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 12)

	def test_constructByText5(self):
		test = categories.CategoryFilterClass.fromString("HC*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 2)

	def test_constructByText6(self):
		test = categories.CategoryFilterClass.fromString("HC2")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 1)
		self.assertTrue(test.hasCategory("HC2"))
		self.assertFalse(test.hasCategory("HC1"))

	def test_constructByText6(self):
		test = categories.CategoryFilterClass.fromString("*2")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 8)
		self.assertTrue(test.hasCategory("DC2"))
		self.assertTrue(test.hasCategory("HC2"))
		self.assertTrue(test.hasCategory("DB2"))
		self.assertTrue(test.hasCategory("HB2"))
		self.assertTrue(test.hasCategory("DA2"))
		self.assertTrue(test.hasCategory("HA2"))
		self.assertTrue(test.hasCategory("DN2"))
		self.assertTrue(test.hasCategory("HN2"))
		self.assertFalse(test.hasCategory("DC1"))
		self.assertFalse(test.hasCategory("HC1"))

	# Test for odd formatting
	def test_constructByText7(self):
		test = categories.CategoryFilterClass.fromString(",HPA,DPA")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 2)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("HPA"))
		self.assertFalse(test.hasCategory("HPB"))

	def test_constructByText8(self):
		test = categories.CategoryFilterClass.fromString("DPA*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 1)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertFalse(test.hasCategory("HPA"))

	def test_constructByText9(self):
		test = categories.CategoryFilterClass.fromString("*DP*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 6)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("DPB"))
		self.assertTrue(test.hasCategory("DPF"))
		self.assertFalse(test.hasCategory("HPA"))

	def test_constructByText10(self):
		test = categories.CategoryFilterClass.fromString("*PA*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 6)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertFalse(test.hasCategory("DPB"))
		self.assertFalse(test.hasCategory("HPA"))

	def test_constructByText11(self):
		test = categories.CategoryFilterClass.fromString("DPA?")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 1)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertFalse(test.hasCategory("HPA"))

	def test_constructByText12(self):
		test = categories.CategoryFilterClass.fromString("HPA DPA")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 2)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("HPA"))
		self.assertFalse(test.hasCategory("HPB"))

	def test_constructByText13(self):
		test = categories.CategoryFilterClass.fromString("*PD* *PE* *PF*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 6)
		self.assertTrue(test.hasCategory("DPF"))
		self.assertTrue(test.hasCategory("HPF"))
		self.assertFalse(test.hasCategory("HPC"))
		self.assertFalse(test.hasCategory("DPC"))

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

	def test_constructByTextInvalid1(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		with pytest.raises(ValueError) as e:
			b= test.hasCategory("INV")
