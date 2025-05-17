import attrs
import typing

import base

@attrs.define(frozen=True, kw_only=True, slots=False)
class CategoryBase(base.BaseClass):
	_genderTypes: typing.ClassVar[tuple] = ("D", "H")
	_ageTypes: typing.ClassVar[tuple]    = ("P", "C", "B", "A", "N", "3", "4", "5", "6", "7", "8")
	_ageOldTypes: typing.ClassVar[tuple] = ("P", "C", "B", "A", "N", "S", "M", "M", "M", "M", "M")
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
												("0", "5")) # Master 80
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
												("", "")) # Master 80

	@staticmethod
	def getGenderPosibilities() -> tuple[int]:
		return tuple(range(len(CategoryBase._genderTypes) - 1))

	@staticmethod
	def getAgePosibilities() -> tuple[int]:
		return tuple(range(len(CategoryBase._ageTypes) - 1))

	@staticmethod
	def getAgeSubPosibilities(age: int) -> tuple[int]:
		return tuple(range(len(CategoryBase._ageSubTypes[age]) - 1))

	@staticmethod
	def getGenderValue(text:str) -> int:
		return CategoryBase._genderTypes.index(text.upper())

	@staticmethod
	def getAgeValue(text:str, old_style:bool = False) -> int:
		if old_style:
			age = CategoryBase._ageTypes.index(text.upper())
		else:
			age = CategoryBase._ageTypes.index(text.upper())

	@staticmethod
	def getAgeSubValue(text:str, age:int, old_style:bool = False) -> int:
		if old_style:
			ageSub = CategoryBase._ageSubOldTypes[age].index(text.upper())
		else:
			ageSub = CategoryBase._ageSubTypes[age].index(text.upper())

@attrs.define(frozen=True, kw_only=True, slots=False)
class CategoryFilterClass(CategoryBase):

	_list:tuple[CategoryClass]

	@staticmethod
	def fromString(filter_text: str, old_style:bool = False) -> "CategoryFilterClass":
		filters_text = split(filter_text, ',')
		filters:list[CategoryClass] = []
		for entry in filters_text:
			genders:tuple[int]
			ages:tuple[int]
			age_subs:tuple[int]|int

			if len(entry) == 3:
				if entry[0] == '*' or entry[0] == '?':
					genders = CategoryBase.getGenderPosibilities()
				else:
					genders = tuple(CategoryBase.getGenderValue(entry[0]))

				if entry[1] == '*' or entry[1] == '?':
					ages = CategoryBase.getAgePosibilities()
					age_subs = -1
				else:
					ages = tuple(CategoryBase.getAgePosibilities(entry[1]))
					if entry[2] == '*' or entry[2] == '?':
						ages = CategoryBase.getAgeSubPosibilities(ages[0])
					else:
						age_subs = tuple(CategoryBase.getAgeSubValue(entry[2], ages[0]))

			elif len(entry) == 2 and (entry[1] == '*' or entry[1] == '?'):
				genders = tuple(CategoryBase.getGenderValue(entry[0]))
				ages = CategoryBase.getAgePosibilities()
				age_subs = -1
			elif len(entry) == 1 and (entry == '*' or entry == '?'):
				genders = CategoryBase.getGenderPosibilities()
				ages = CategoryBase.getAgePosibilities()
				age_subs = -1
			else:
				return ValueError("Value (" + entry + ") is not a valid categorie string.")

			for g in genders:
				for a in ages:
					if isinstance(age_subs, list):
						for s in age_subs:
							categorie = CategoryClass(gender=g, age=a, ageSub=s)
							filters.append(categorie)
					elif isinstance(age_subs, int) and age_subs == -1:
						for s in CategoryBase.getAgeSubPosibilities(a):
							categorie = CategoryClass(gender=g, age=a, ageSub=s)
							filters.append(categorie)

		return CategoryFilterClass(list=tuple(filters))

	#_categoryFilter: str = attrs.field(validator=attrs.validators.instance_of(str))

def CategoryFilterClass_converter(data: str) -> CategoryFilterClass:
	return CategoryFilterClass(categoryFilter=data)

category_class_gender_validator(instance: "CategoryClass", attribute: str, value: int):
	if value > (len(instance._genderTypes) - 1):
		raise ValueError("No valid value for gender (" + str(value) + ")")

category_class_age_validator(instance: "CategoryClass", attribute: str, value: int):
	if value > (len(instance._ageTypes) - 1):
		raise ValueError("No valid value for age (" + str(value) + ")")

category_class_age_sub_validator(instance: "CategoryClass", attribute: str, value: int):
	if value > (len(instance._ageSubTypes[instance._age]) - 1):
		raise ValueError("No valid value for sub age (" + str(value) + ")")

@attrs.define(frozen=True, kw_only=True, slots=False)
class CategoryClass(CategoryBase):
	_gender:int = attrs.field(validator=[attrs.validators.instance_of(int), category_class_gender_validator])
	_age:int = attrs.field(validator=[attrs.validators.instance_of(int), category_class_age_validator])
	_ageSub:int = attrs.field(validator=[attrs.validators.instance_of(int), category_class_age_sub_validator])

	@staticmethod
	def getCategory(date: datetime.date, season:int = 0) -> "CategoryClass|None":
		# Calculate age at reference date
		if season == 0:
			today = date.today()
			if today.month <= 6:
				season = today.year - 1
			else:
				season = today.year

		reference_date = datetime.date(season, 6, 30)
		age_in_years = dateutil.relativedelta(reference_date, date).years

		age:int
		age_sub:int

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
	def getCategory(text: str) -> "CategoryClass|None":
		if len(text) != 3:
			return None

		gender:int
		age:int
		ageSub:int
		old_style:bool

		try:
			gender = CategoryClass._genderTypes.index(text[0].upper())
		except ValueError:
			return None

		try:
			age = CategoryClass._ageTypes.index(text[1].upper())
			old_style = False
		except ValueError:
			try:
				age = CategoryClass._ageTypes.index(text[1].upper())
				old_style = True
			except ValueError:
				return None

		try:
			if old_style:
				ageSub = CategoryClass._ageSubOldTypes[age].index(text[2].upper())
			else:
				ageSub = CategoryClass._ageSubTypes[age].index(text[2].upper())
		except ValueError:
			return None

		try:
			return CategoryClass(gender=gender, age=age, ageSub=ageSub)
		except ValueError:
			return None

	def match(self, filter: CategoryFilterClass) -> bool:
		for entry in filter.getList():
			if self.equal(entry):
				return True

	def equal(self, o: "CategoryClass") -> bool:
		return (self._gender == o._gender && self._age == o._age && self._ageSub == o._ageSub)

	def asString(self, old_style:bool = False) -> str:
		if old_style:
			return str(self._genderTypes[self._gender] + self._ageOldTypes[self._age] + self._ageSubOldTypes[self._age][self._ageSub])
		else:
			return str(self._genderTypes[self._gender] + self._ageTypes[self._age] + self._ageSubTypes[self._age][self._ageSub])

	def __str__(self) -> str:
		return self.asString()

	def __repr__(self) -> str:
		return self.asString()

def CategoryClass_converter(data: str) -> CategoryClass:
	return CategoryClass.getCategory(text=data)