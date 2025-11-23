#!/bin/python

import typing
import typeguard
import attrs
import datetime
import dateutil.relativedelta
import re

import competitionnotify.dataclasses.base as base

@attrs.define(frozen=True, kw_only=True, slots=False)
class CategoryBase(base.BaseClass):
	_genderTypes: typing.ClassVar[tuple] = ("D", "H")
	_ageTypes: typing.ClassVar[tuple]    = ("P", "C", "B", "A", "N", "3", "4", "5", "6", "7", "8", "9")
	_ageOldTypes: typing.ClassVar[tuple] = ("P", "C", "B", "A", "N", "S", "M", "M", "M", "M", "M", "M")
	_ageSubTypes: typing.ClassVar[tuple]    = ( ("F", "E", "D", "C", "B", "A"), # Pupillen
												("1", "2"), # Junior C
												("1", "2"), # Junior B
												("1", "2"), # Junior A
												("1", "2", "3", "4"), # Neo-senior
												("0", "5"), # Senior
												("0", "5"), # Master 40
												("0", "5"), # Master 50
												("0", "5"), # Master 60
												("0", "5"), # Master 70
												("0", "5"), # Master 80
												("0", "5")) # Master 90
	_ageSubOldTypes: typing.ClassVar[tuple] = ( ("F", "E", "D", "C", "B", "A"), # Pupillen
												("1", "2"), # Junior C
												("1", "2"), # Junior B
												("1", "2"), # Junior A
												("1", "2", "3", "4"), # Neo-senior
												("A", "B"), # Senior
												("A", "B"), # Master 40
												("C", "D"), # Master 50
												("E", "F"), # Master 60
												("G", "H"), # Master 70
												("", ""), # Master 80
												("", "")) # Master 90

	@staticmethod
	def getGenderPosibilities() -> tuple[int, ...]:
		return tuple(range(0, len(CategoryBase._genderTypes)))

	@staticmethod
	def getAgePosibilities() -> tuple[int, ...]:
		return tuple(range(0, len(CategoryBase._ageTypes)))

	@staticmethod
	def getAgeSubPosibilities(age: int) -> tuple[int, ...]:
		return tuple(range(0, len(CategoryBase._ageSubTypes[age])))

	@staticmethod
	def getGenderValue(text:str) -> int:
		return CategoryBase._genderTypes.index(text.upper())

	@staticmethod
	def getAgeValue(text:str, old_style:bool = False) -> int:
		if old_style:
			return CategoryBase._ageOldTypes.index(text.upper())
		else:
			return CategoryBase._ageTypes.index(text.upper())

	@staticmethod
	def getAgeSubValue(text:str, age:int, old_style:bool = False) -> int:
		if old_style:
			return CategoryBase._ageSubOldTypes[age].index(text.upper())
		else:
			return CategoryBase._ageSubTypes[age].index(text.upper())

	@staticmethod
	def getAllCategories(old_style:bool = False) -> tuple[str, ...]:
		categories: list[str] = []

		for g in CategoryBase._genderTypes:
			i_a = 0
			if old_style:
				for a in CategoryBase._ageOldTypes:
					for s in CategoryBase._ageSubOldTypes[i_a]:
						category_string = g + a + s
						if len(category_string) == 3:
							categories.append(category_string)
					i_a += 1
			else:
				for a in CategoryBase._ageTypes:
					for s in CategoryBase._ageSubTypes[i_a]:
						category_string = g + a + s
						if len(category_string) == 3:
							categories.append(category_string)
					i_a += 1

		return tuple(categories)

@typeguard.typechecked
def category_class_gender_validator(instance: "CategoryClass", attribute: attrs.Attribute, value: int):
	if value > (len(instance._genderTypes) - 1) or value < 0:
		raise ValueError("No valid value for gender (" + str(value) + ")")

@typeguard.typechecked
def category_class_age_validator(instance: "CategoryClass", attribute: attrs.Attribute, value: int):
	if value > (len(instance._ageTypes) - 1) or value < 0:
		raise ValueError("No valid value for age (" + str(value) + ")")

@typeguard.typechecked
def category_class_age_sub_validator(instance: "CategoryClass", attribute: attrs.Attribute, value: int):
	if value > (len(instance._ageSubTypes[instance._age]) - 1) or value < 0:
		raise ValueError("No valid value for sub age (" + str(value) + ")")

@attrs.define(frozen=True, kw_only=True, slots=False)
class CategoryClass(CategoryBase):
	_gender:int = attrs.field(validator=[attrs.validators.instance_of(int), category_class_gender_validator])
	_age:int = attrs.field(validator=[attrs.validators.instance_of(int), category_class_age_validator])
	_ageSub:int = attrs.field(validator=[attrs.validators.instance_of(int), category_class_age_sub_validator])

	@staticmethod
	def getCategoryByDate(male:bool, date: datetime.date, season:int = 0) -> "CategoryClass|None":
		# Calculate age at reference date
		if season == 0:
			today = date.today()
			if today.month <= 6:
				season = today.year - 1
			else:
				season = today.year

		reference_date = datetime.date(season, 6, 30)
		age_in_years = dateutil.relativedelta.relativedelta(reference_date, date).years

		age:int
		age_sub:int
		gender:int = 1 if male else 0

		if age_in_years < 13:
			age = 0
			age_sub = max(age_in_years - 7, 0)
		elif age_in_years < 15:
			age = 1
			age_sub = age_in_years - 13
		elif age_in_years < 17:
			age = 2
			age_sub = age_in_years - 15
		elif age_in_years < 19:
			age = 3
			age_sub = age_in_years - 17
		elif age_in_years < 23:
			age = 4
			age_sub = age_in_years - 19
		elif age_in_years < 30:
			age = 5
			age_sub = 0
		elif age_in_years < 39:
			age = 5
			age_sub = 1
		else:
			age = ((age_in_years + 1) // 10) + 2
			age_sub = ((age_in_years + 1) % 10) // 5

		try:
			return CategoryClass(gender=gender, age=age, ageSub=age_sub)
		except ValueError:
			return None

	@staticmethod
	def getCategoryByString(string: str) -> "CategoryClass|None":
		if len(string) != 3:
			return None

		gender:int
		age:int|list[int]
		ageSub:int
		old_style:bool

		try:
			gender = CategoryClass._genderTypes.index(string[0].upper())
		except ValueError:
			return None

		try:
			age = CategoryClass._ageTypes.index(string[1].upper())
			old_style = False
		except ValueError:
			try:
				#age = CategoryClass._ageOldTypes.index(string[1].upper())
				age = [i for i in range(len(CategoryClass._ageOldTypes) - 1) if CategoryClass._ageOldTypes[i] == string[1].upper()]
				old_style = True
			except ValueError:
				return None

		try:
			if old_style:
				if isinstance(age, list):
					for i in age:
						try:
							ageSub = CategoryClass._ageSubOldTypes[i].index(string[2].upper())
							age = i
							break
						except ValueError:
							continue
				else:
					ageSub = CategoryClass._ageSubOldTypes[age].index(string[2].upper())
			else:
				if isinstance(age, list):
					for i in age:
						try:
							ageSub = CategoryClass._ageSubTypes[i].index(string[2].upper())
							age = i
							break
						except ValueError:
							continue
				else:
					ageSub = CategoryClass._ageSubTypes[age].index(string[2].upper())
		except ValueError:
			return None

		try:
			# Silence mypy error on following line (Argument "age" to "CategoryClass" has incompatible type "int | list[int]"; expected "int"), as code above makes sure age is not a list by this time anymore
			return CategoryClass(gender=gender, age=age, ageSub=ageSub)  # type: ignore[arg-type]
		except ValueError:
			return None

	def getGender(self) -> str:
		return self._genderTypes[self._gender]

	def match(self, filter: "CategoryFilterClass") -> bool:
		for entry in filter.getList():
			if self.equal(entry):
				return True
		return False

	def equal(self, o: "CategoryClass") -> bool:
		return (self._gender == o._gender and self._age == o._age and self._ageSub == o._ageSub)

	def asString(self, old_style:bool = False) -> str:
		if old_style:
			return str(self._genderTypes[self._gender] + self._ageOldTypes[self._age] + self._ageSubOldTypes[self._age][self._ageSub])
		else:
			return str(self._genderTypes[self._gender] + self._ageTypes[self._age] + self._ageSubTypes[self._age][self._ageSub])

	def __str__(self) -> str:
		return self.asString()

	def __repr__(self) -> str:
		return self.asString()

	def __eq__(self, o: object|str) -> bool:
		if isinstance(o, str):
			o = CategoryClass.getCategoryByString(o)

		if not isinstance(o, CategoryClass):
			raise TypeError('Can only use comparison on two CategoryClass objects')
		return self.equal(o)

	def __ne__(self, o: object|str) -> bool:
		if isinstance(o, str):
			o = CategoryClass.getCategoryByString(o)

		if not isinstance(o, CategoryClass):
			raise TypeError('Can only use comparison on two CategoryClass objects')
		return not self.equal(o)

	def __le__(self, o: object|str) -> bool:
		if isinstance(o, str):
			o = CategoryClass.getCategoryByString(o)

		if not isinstance(o, CategoryClass):
			raise TypeError('Can only use comparison on two CategoryClass objects')

		return ((self._age < o._age) or (self._age == o._age and self._ageSub <= o._ageSub))

	def __lt__(self, o: object|str) -> bool:
		if isinstance(o, str):
			o = CategoryClass.getCategoryByString(o)

		if not isinstance(o, CategoryClass):
			raise TypeError('Can only use comparison on two CategoryClass objects')

		return ((self._age < o._age) or (self._age == o._age and self._ageSub < o._ageSub))

	def __ge__(self, o: object|str) -> bool:
		if isinstance(o, str):
			o = CategoryClass.getCategoryByString(o)

		if not isinstance(o, CategoryClass):
			raise TypeError('Can only use comparison on two CategoryClass objects')

		return ((self._age > o._age) or (self._age == o._age and self._ageSub >= o._ageSub))

	def __gt__(self, o: object|str) -> bool:
		if isinstance(o, str):
			o = CategoryClass.getCategoryByString(o)

		if not isinstance(o, CategoryClass):
			raise TypeError('Can only use comparison on two CategoryClass objects')

		return ((self._age > o._age) or (self._age == o._age and self._ageSub > o._ageSub))

@typeguard.typechecked
def CategoryClass_converter(data: CategoryClass|str) -> CategoryClass:
	if isinstance(data, CategoryClass):
		return data
	else:
		ret = CategoryClass.getCategoryByString(string=data)
		if ret is None:
			raise ValueError("String '" + data + "' is not a valid category string.")
		return ret

@attrs.define(frozen=True, kw_only=True, slots=False)
class CategoryFilterClass(CategoryBase):
	_list:tuple[CategoryClass, ...] = attrs.field(validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(CategoryClass),
            iterable_validator=attrs.validators.instance_of(tuple)))

	def hasCategory(self, category:CategoryClass|str) -> bool:
		cat: CategoryClass|None
		if isinstance(category, str):
			cat = CategoryClass.getCategoryByString(category)
		else:
			cat = category

		if isinstance(cat, CategoryClass):
			return cat.match(self)
		else:
			raise ValueError("Value of parameter `category` is not a valid category ('" + str(category) + "')")

	def numberOfCategories(self) -> int:
		return len(self._list)

	def getList(self) -> tuple[CategoryClass, ...]:
		return self._list

	@staticmethod
	def fromString(filter_text: str, old_style: bool|None = None, use_except: bool = True) -> "CategoryFilterClass":
		filters_split = re.split(r'[,|\s;]+', filter_text)
		filters_text:list[str] = []
		filters:list[CategoryClass] = []
		all_categories_list = CategoryBase.getAllCategories(False)
		all_categories_list_old = CategoryBase.getAllCategories(True)
		for entry in filters_split:
			if len(entry) == 0:
				continue

			if len(entry) == 4:
				entry = entry.replace("*", ".*")
			else:
				entry = entry.replace("*", ".+")
			entry = entry.replace("?", ".?")
			regex = re.compile("(?i)^" + entry + "$")
			if old_style is None:
				filtered_categories_list = list(filter(regex.match, all_categories_list))
				if len(filtered_categories_list) == 0:
					filtered_categories_list = list(filter(regex.match, all_categories_list_old))
					if len(filtered_categories_list) == 0 and use_except:
						raise ValueError("Value of category element is not a valid category ('" + str(entry) + "')")
					elif len(filtered_categories_list) == 0:
						continue

				filters_text = filters_text + filtered_categories_list
			elif old_style:
				filtered_categories_list = list(filter(regex.match, all_categories_list_old))
				if len(filtered_categories_list) == 0 and use_except:
					raise ValueError("Value of category element is not a valid category ('" + str(entry) + "')")
				elif len(filtered_categories_list) == 0:
						continue
				filters_text = filters_text + filtered_categories_list
			elif not old_style:
				filtered_categories_list = list(filter(regex.match, all_categories_list))
				if len(filtered_categories_list) == 0 and use_except:
					raise ValueError("Value of category element is not a valid category ('" + str(entry) + "')")
				elif len(filtered_categories_list) == 0:
						continue
				filters_text = filters_text + filtered_categories_list

		for i in set(filters_text):
			c = CategoryClass.getCategoryByString(i)
			if c is not None:
				filters.append(c)
			elif use_except:
				raise ValueError("Value of category element is not a valid category ('" + i + "')")

		return CategoryFilterClass(list=tuple(filters))

@typeguard.typechecked
def CategoryFilterClass_converter(data: CategoryFilterClass|str) -> CategoryFilterClass:
	if isinstance(data, CategoryFilterClass):
		return data
	else:
		return CategoryFilterClass.fromString(filter_text=data, old_style=None)
