import competitionnotify.classes.categories as categories

import unittest
import pytest

import datetime
import json

class TestCategoryBase(unittest.TestCase):
	def test_getGenderPosibilities(self):
		self.assertEqual(len(categories.CategoryBase.getGenderPosibilities()), 2)

	def test_getAgePosibilities(self):
		self.assertEqual(len(categories.CategoryBase.getAgePosibilities()), 12)

	def test_getAgeSubPosibilities(self):
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(0)), 6)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(1)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(2)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(3)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(4)), 4)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(5)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(6)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(7)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(8)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(9)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(10)), 2)
		self.assertEqual(len(categories.CategoryBase.getAgeSubPosibilities(11)), 2)

	def test_getGenderValue(self):
		self.assertEqual(categories.CategoryBase.getGenderValue("D"), 0)
		self.assertEqual(categories.CategoryBase.getGenderValue("d"), 0)
		self.assertEqual(categories.CategoryBase.getGenderValue("H"), 1)
		self.assertEqual(categories.CategoryBase.getGenderValue("h"), 1)

	def test_getAgeValue1(self):
		self.assertEqual(categories.CategoryBase.getAgeValue("P"), 0)
		self.assertEqual(categories.CategoryBase.getAgeValue("C"), 1)
		self.assertEqual(categories.CategoryBase.getAgeValue("B"), 2)
		self.assertEqual(categories.CategoryBase.getAgeValue("A"), 3)
		self.assertEqual(categories.CategoryBase.getAgeValue("N"), 4)
		self.assertEqual(categories.CategoryBase.getAgeValue("3"), 5)
		self.assertEqual(categories.CategoryBase.getAgeValue("4"), 6)
		self.assertEqual(categories.CategoryBase.getAgeValue("5"), 7)
		self.assertEqual(categories.CategoryBase.getAgeValue("6"), 8)
		self.assertEqual(categories.CategoryBase.getAgeValue("7"), 9)
		self.assertEqual(categories.CategoryBase.getAgeValue("8"), 10)
		self.assertEqual(categories.CategoryBase.getAgeValue("9"), 11)

	def test_getAgeValue2(self):
		self.assertEqual(categories.CategoryBase.getAgeValue("P", False), 0)
		self.assertEqual(categories.CategoryBase.getAgeValue("C", False), 1)
		self.assertEqual(categories.CategoryBase.getAgeValue("B", False), 2)
		self.assertEqual(categories.CategoryBase.getAgeValue("A", False), 3)
		self.assertEqual(categories.CategoryBase.getAgeValue("N", False), 4)
		self.assertEqual(categories.CategoryBase.getAgeValue("3", False), 5)
		self.assertEqual(categories.CategoryBase.getAgeValue("4", False), 6)
		self.assertEqual(categories.CategoryBase.getAgeValue("5", False), 7)
		self.assertEqual(categories.CategoryBase.getAgeValue("6", False), 8)
		self.assertEqual(categories.CategoryBase.getAgeValue("7", False), 9)
		self.assertEqual(categories.CategoryBase.getAgeValue("8", False), 10)
		self.assertEqual(categories.CategoryBase.getAgeValue("9", False), 11)

	def test_getAgeValue3(self):
		self.assertEqual(categories.CategoryBase.getAgeValue("P", True), 0)
		self.assertEqual(categories.CategoryBase.getAgeValue("C", True), 1)
		self.assertEqual(categories.CategoryBase.getAgeValue("B", True), 2)
		self.assertEqual(categories.CategoryBase.getAgeValue("A", True), 3)
		self.assertEqual(categories.CategoryBase.getAgeValue("N", True), 4)
		self.assertEqual(categories.CategoryBase.getAgeValue("S", True), 5)
		self.assertEqual(categories.CategoryBase.getAgeValue("M", True), 6)

	def test_getAgeSubValue1(self):
		# Pupillen
		self.assertEqual(categories.CategoryBase.getAgeSubValue("F", 0), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("E", 0), 1)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("D", 0), 2)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("C", 0), 3)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("B", 0), 4)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("A", 0), 5)
		# Junioren C
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 1), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 1), 1)
		# Junioren B
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 2), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 2), 1)
		# Junioren A
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 3), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 3), 1)
		# Neo-Senioren
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 4), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 4), 1)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("3", 4), 2)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("4", 4), 3)
		# Masters
		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 5), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 5), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 6), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 6), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 7), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 7), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 8), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 8), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 9), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 9), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 10), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 10), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 11), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 11), 1)

	def test_getAgeSubValue2(self):
		# Pupillen
		self.assertEqual(categories.CategoryBase.getAgeSubValue("F", 0, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("E", 0, False), 1)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("D", 0, False), 2)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("C", 0, False), 3)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("B", 0, False), 4)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("A", 0, False), 5)
		# Junioren C
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 1, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 1, False), 1)
		# Junioren B
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 2, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 2, False), 1)
		# Junioren A
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 3, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 3, False), 1)
		# Neo-Senioren
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 4, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 4, False), 1)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("3", 4, False), 2)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("4", 4, False), 3)
		# Masters
		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 5, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 5, False), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 6, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 6, False), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 7, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 7, False), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 8, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 8, False), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 9, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 9, False), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 10, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 10, False), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("0", 11, False), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("5", 11, False), 1)

	def test_getAgeSubValue3(self):
		# Pupillen
		self.assertEqual(categories.CategoryBase.getAgeSubValue("F", 0, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("E", 0, True), 1)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("D", 0, True), 2)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("C", 0, True), 3)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("B", 0, True), 4)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("A", 0, True), 5)
		# Junioren C
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 1, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 1, True), 1)
		# Junioren B
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 2, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 2, True), 1)
		# Junioren A
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 3, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 3, True), 1)
		# Neo-Senioren
		self.assertEqual(categories.CategoryBase.getAgeSubValue("1", 4, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("2", 4, True), 1)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("3", 4, True), 2)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("4", 4, True), 3)
		# Masters
		self.assertEqual(categories.CategoryBase.getAgeSubValue("A", 5, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("B", 5, True), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("A", 6, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("B", 6, True), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("C", 7, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("D", 7, True), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("E", 8, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("F", 8, True), 1)

		self.assertEqual(categories.CategoryBase.getAgeSubValue("G", 9, True), 0)
		self.assertEqual(categories.CategoryBase.getAgeSubValue("H", 9, True), 1)

	def test_getAllCategories(self):
		all_categories = (
			'DPF', 'DPE', 'DPD', 'DPC', 'DPB', 'DPA',
			'DC1', 'DC2',
			'DB1', 'DB2',
			'DA1', 'DA2',
			'DN1', 'DN2', 'DN3', 'DN4',
			'D30', 'D35', 'D40', 'D45', 'D50', 'D55', 'D60', 'D65', 'D70', 'D75', 'D80', 'D85', 'D90', 'D95',
			'HPF', 'HPE', 'HPD', 'HPC', 'HPB', 'HPA',
			'HC1', 'HC2',
			'HB1', 'HB2',
			'HA1', 'HA2',
			'HN1', 'HN2', 'HN3', 'HN4',
			'H30', 'H35', 'H40', 'H45', 'H50', 'H55', 'H60', 'H65', 'H70', 'H75', 'H80', 'H85', 'H90', 'H95'
		)

		all_categories_old = (
			'DPF', 'DPE', 'DPD', 'DPC', 'DPB', 'DPA',
			'DC1', 'DC2',
			'DB1', 'DB2',
			'DA1', 'DA2',
			'DN1', 'DN2', 'DN3', 'DN4',
			'DSA', 'DSB',
			'DMA', 'DMB', 'DMC', 'DMD', 'DME', 'DMF', 'DMG', 'DMH',
			'HPF', 'HPE', 'HPD', 'HPC', 'HPB', 'HPA',
			'HC1', 'HC2',
			'HB1', 'HB2',
			'HA1', 'HA2',
			'HN1', 'HN2', 'HN3', 'HN4',
			'HSA', 'HSB',
			'HMA', 'HMB', 'HMC', 'HMD', 'HME', 'HMF', 'HMG', 'HMH',
		)
		test = categories.CategoryBase.getAllCategories()
		self.assertIsInstance(test, tuple)
		self.assertEqual(test, all_categories)

		test = categories.CategoryBase.getAllCategories(False)
		self.assertIsInstance(test, tuple)
		self.assertEqual(test, all_categories)

		test = categories.CategoryBase.getAllCategories(True)
		self.assertIsInstance(test, tuple)
		self.assertEqual(test, all_categories_old)

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

	def test_compare_eq1(self):
		category_text_1 = "H55"
		category_text_2 = "HMD"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 == test_2)

	def test_compare_eq2(self):
		category_text_1 = "H55"
		category_text_2 = "DMD"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertFalse(test_1 == test_2)

	def test_compare_eq3(self):
		category_text_1 = "H55"
		category_text_2 = "HME"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertFalse(test_1 == test_2)

	def test_compare_ne1(self):
		category_text_1 = "HN1"
		category_text_2 = "HN1"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertFalse(test_1 != test_2)

	def test_compare_ne2(self):
		category_text_1 = "HPA"
		category_text_2 = "DPA"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 != test_2)

	def test_compare_le1(self):
		category_text_1 = "H55"
		category_text_2 = "HMD"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 <= test_2)

	def test_compare_le2(self):
		category_text_1 = "H55"
		category_text_2 = "DMD"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 <= test_2)

	def test_compare_le3(self):
		category_text_1 = "H55"
		category_text_2 = "HME"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 <= test_2)

	def test_compare_le4(self):
		category_text_1 = "H90"
		category_text_2 = "HME"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertFalse(test_1 <= test_2)

	def test_compare_lt1(self):
		category_text_1 = "H55"
		category_text_2 = "HME"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 < test_2)

	def test_compare_ge1(self):
		category_text_1 = "H55"
		category_text_2 = "DMD"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 >= test_2)

	def test_compare_ge2(self):
		category_text_1 = "H65"
		category_text_2 = "HME"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 >= test_2)

	def test_compare_ge4(self):
		category_text_1 = "H40"
		category_text_2 = "DME"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertFalse(test_1 >= test_2)

	def test_compare_gt1(self):
		category_text_1 = "HME"
		category_text_2 = "D55"
		test_1 = categories.CategoryClass.getCategoryByString(string=category_text_1)
		test_2 = categories.CategoryClass.getCategoryByString(string=category_text_2)
		self.assertTrue(test_1 > test_2)

	def test_hashable(self):
		test = categories.CategoryClass.getCategoryByString(string="DN4")
		self.assertIsInstance(test, categories.CategoryClass)
		self.assertIsInstance(hash(test), int)

	def test_json(self):
		test1 = categories.CategoryClass.getCategoryByString(string="HB2")
		self.assertIsInstance(test1, categories.CategoryClass)
		json_string = test1.json()
		self.assertIsInstance(json_string, str)

		d = json.loads(json_string)
		test2 = categories.CategoryClass(**d)
		self.assertIsInstance(test2, categories.CategoryClass)
		self.assertTrue(test1 == test2)

	def test_serializable(self):
		test1 = categories.CategoryClass.getCategoryByString(string="DSB")
		self.assertIsInstance(test1, categories.CategoryClass)
		s = test1.serialize()

		test2 = categories.CategoryClass.deserialize(s)
		self.assertIsInstance(test2, categories.CategoryClass)
		self.assertTrue(test1 == test2)


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
		self.assertEqual(test.numberOfCategories(), 2)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("HPA"))
		self.assertFalse(test.hasCategory("DPB"))
		self.assertFalse(test.hasCategory("HC1"))

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

	def test_constructByText13(self):
		test = categories.CategoryFilterClass.fromString("*SB,*4*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 6)
		self.assertTrue(test.hasCategory("H35"))
		self.assertTrue(test.hasCategory("H40"))
		self.assertTrue(test.hasCategory("H45"))
		self.assertTrue(test.hasCategory("D35"))
		self.assertTrue(test.hasCategory("D40"))
		self.assertTrue(test.hasCategory("D45"))
		self.assertFalse(test.hasCategory("H30"))
		self.assertFalse(test.hasCategory("H50"))

	def test_constructByText14(self):
		test = categories.CategoryFilterClass.fromString("*M*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 16)
		self.assertTrue(test.hasCategory("H40"))
		self.assertTrue(test.hasCategory("D40"))
		self.assertTrue(test.hasCategory("H45"))
		self.assertTrue(test.hasCategory("D45"))
		self.assertTrue(test.hasCategory("H70"))
		self.assertTrue(test.hasCategory("D70"))
		self.assertTrue(test.hasCategory("H75"))
		self.assertTrue(test.hasCategory("D75"))

		self.assertFalse(test.hasCategory("H35"))
		self.assertFalse(test.hasCategory("H80"))
		self.assertFalse(test.hasCategory("HN4"))
		self.assertFalse(test.hasCategory("DN1"))

	def test_constructByText15(self):
		test = categories.CategoryFilterClass.fromString("*0,*5")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 28)
		self.assertTrue(test.hasCategory("H30"))
		self.assertTrue(test.hasCategory("D30"))
		self.assertTrue(test.hasCategory("H45"))
		self.assertTrue(test.hasCategory("D45"))
		self.assertTrue(test.hasCategory("H70"))
		self.assertTrue(test.hasCategory("D70"))
		self.assertTrue(test.hasCategory("H95"))
		self.assertTrue(test.hasCategory("D95"))

		self.assertTrue(test.hasCategory("HSA"))
		self.assertTrue(test.hasCategory("DMG"))

		self.assertFalse(test.hasCategory("HN4"))
		self.assertFalse(test.hasCategory("HN1"))
		self.assertFalse(test.hasCategory("DN2"))
		self.assertFalse(test.hasCategory("DPF"))

	def test_constructByText16(self):
		test = categories.CategoryFilterClass.fromString("*5")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 14)
		self.assertTrue(test.hasCategory("H35"))
		self.assertTrue(test.hasCategory("D35"))
		self.assertTrue(test.hasCategory("H45"))
		self.assertTrue(test.hasCategory("D45"))
		self.assertTrue(test.hasCategory("H95"))
		self.assertTrue(test.hasCategory("D95"))

		self.assertTrue(test.hasCategory("HSB"))
		self.assertTrue(test.hasCategory("DMH"))

		self.assertFalse(test.hasCategory("H30"))
		self.assertFalse(test.hasCategory("H50"))
		self.assertFalse(test.hasCategory("D50"))
		self.assertFalse(test.hasCategory("DMC"))

	def test_constructByText17(self):
		test = categories.CategoryFilterClass.fromString("DPA,DC*,DB*,DA*,DN*,DS*,D4*,D5*,D6*,D7*,D8*,D9*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 25)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("DC1"))
		self.assertTrue(test.hasCategory("DN4"))
		self.assertTrue(test.hasCategory("D45"))
		self.assertTrue(test.hasCategory("DMA"))
		self.assertTrue(test.hasCategory("D95"))

		self.assertFalse(test.hasCategory("H30"))
		self.assertFalse(test.hasCategory("H50"))
		self.assertFalse(test.hasCategory("H55"))
		self.assertFalse(test.hasCategory("DPB"))

	def test_constructByText18(self):
		test = categories.CategoryFilterClass.fromString("Dp*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 6)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("DPB"))
		self.assertTrue(test.hasCategory("DPC"))
		self.assertTrue(test.hasCategory("DPD"))
		self.assertTrue(test.hasCategory("DPE"))
		self.assertTrue(test.hasCategory("DPF"))

		self.assertFalse(test.hasCategory("HPA"))
		self.assertFalse(test.hasCategory("DC1"))

	def test_constructByText19(self):
		test = categories.CategoryFilterClass.fromString("HPA;DPA")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 2)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("HPA"))
		self.assertFalse(test.hasCategory("HPB"))

	def test_constructByText20(self):
		test = categories.CategoryFilterClass.fromString("HPA|DPA")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 2)
		self.assertTrue(test.hasCategory("DPA"))
		self.assertTrue(test.hasCategory("HPA"))
		self.assertFalse(test.hasCategory("HPB"))

	def test_constructByText21(self):
		test = categories.CategoryFilterClass.fromString("DA*,DN*,DS*,D40*,DSA*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertEqual(test.numberOfCategories(), 9)
		self.assertTrue(test.hasCategory("DA1"))
		self.assertTrue(test.hasCategory("DA2"))
		self.assertTrue(test.hasCategory("D40"))
		self.assertFalse(test.hasCategory("DPA"))
		self.assertFalse(test.hasCategory("HA1"))
		self.assertFalse(test.hasCategory("D45"))

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
			b = test.hasCategory("INV")

	def test_hash(self):
		test = categories.CategoryFilterClass.fromString("*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertIsInstance(hash(test), int)

	def test_hasEqual(self):
		test1 = categories.CategoryFilterClass.fromString("HS*,HM*")
		test2 = categories.CategoryFilterClass.fromString("H?0,H?5")
		self.assertIsInstance(test1, categories.CategoryFilterClass)
		self.assertIsInstance(test2, categories.CategoryFilterClass)
		self.assertTrue(test1 == test2)

	def test_notEqual(self):
		test1 = categories.CategoryFilterClass.fromString("HS*,HM*")
		test2 = categories.CategoryFilterClass.fromString("H3*")
		self.assertIsInstance(test1, categories.CategoryFilterClass)
		self.assertIsInstance(test2, categories.CategoryFilterClass)
		self.assertTrue(test1 != test2)

	def test_hashable(self):
		test = categories.CategoryFilterClass.fromString("HS*,HM*")
		self.assertIsInstance(test, categories.CategoryFilterClass)
		self.assertIsInstance(hash(test), int)

	def test_json(self):
		test1 = categories.CategoryFilterClass.fromString("HS*,HM*")
		self.assertIsInstance(test1, categories.CategoryFilterClass)
		json_string = test1.json()
		self.assertIsInstance(json_string, str)

		d = json.loads(json_string)
		test2 = categories.CategoryFilterClass(**d)
		self.assertIsInstance(test2, categories.CategoryFilterClass)
		self.assertTrue(test1 == test2)

	def test_serializable(self):
		test1 = categories.CategoryFilterClass.fromString("HS*,HM*")
		self.assertIsInstance(test1, categories.CategoryFilterClass)
		s = test1.serialize()

		test2 = categories.CategoryFilterClass.deserialize(s)
		self.assertIsInstance(test2, categories.CategoryFilterClass)
		self.assertTrue(test1 == test2)