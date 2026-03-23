#!/bin/python

import typing
import typeguard
import attrs
import logging
import uuid
import datetime

import competitionnotify.classes.base as base
import competitionnotify.classes.time as time
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.categories as categories
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class CompetitorClass(base.BaseClass):
	_listId: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_startNumber: int = attrs.field(validator=attrs.validators.instance_of(int))
	_legNumber: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_nationalityCode: str = attrs.field(validator=attrs.validators.instance_of(str))
	_licenseDiscipline: discipline.DisciplineClass|None = attrs.field(default=None, converter=discipline.DisciplineClass_converter, validator=attrs.validators.optional(attrs.validators.instance_of(discipline.DisciplineClass)))
	_licenseKey: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_licenseFlags: int = attrs.field(validator=attrs.validators.instance_of(int))
	_status: int = attrs.field(validator=attrs.validators.instance_of(int))
	_category: categories.CategoryClass|None = attrs.field(converter=categories.CategoryClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(categories.CategoryClass))) # type: ignore [misc]
	#_class: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_sponsor: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_clubCountryCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_clubCode: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_clubShortName: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_clubShortCode: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_clubFullName: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	#_from: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder1: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_transponder2: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_organizationTransponder1: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_organizationTransponder2: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_fullName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_shortName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_added: datetime.datetime|None = attrs.field(default=None, converter=utils.datetime_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(datetime.datetime))) # type: ignore [misc]
	_source: int = attrs.field(validator=attrs.validators.instance_of(int)) # 0 = registration; 1 = manual
	_typeName: str = attrs.field(validator=attrs.validators.instance_of(str))
	_hideNameOnCompetitorsList: bool|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(bool)))
	_id: uuid.UUID = base.BaseClass.serializable(True, converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_gender: int = attrs.field(validator=attrs.validators.instance_of(int))

	def isNaturalPerson(self) -> bool:
		if self._typeName != "PersonCompetitor" and self._licenseKey is None and self._category is None:
			return False
		return True

	def getId(self) -> uuid.UUID:
		return self._id

	def getLicenseDiscipline(self) -> discipline.DisciplineClass|None:
		return self._licenseDisciplines

	def getLicenseKey(self) -> str:
		return self._licenseKey

	def getStartNumber(self) -> int:
		return self._startNumber

	def getClubCode(self) -> int|None:
		return self._clubCode

	def getCategory(self) -> categories.CategoryClass:
		return self._category

	def getName(self) -> str:
		return self._fullName

	def equal(self, o: "CompetitorClass") -> bool:
		return (self._id == o._id and
		  self._listId == o._listId and
		  self._fullName == o._fullName and
		  self._added == o._added and
		  self._startNumber == o._startNumber and
		  self._clubCode == o._clubCode)

	def __str__(self) -> str:
		return self._fullName

	def __repr__(self) -> str:
		return self.__str__()

@typeguard.typechecked
def CompetitorClass_converter(data: CompetitorClass|dict[str, typing.Any]) -> CompetitorClass:
	return utils.class_converter_except(data, CompetitorClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistanceCombinationCompetitorClass(base.BaseClass):
	_competitor: CompetitorClass = base.BaseClass.serializable(True, converter=CompetitorClass_converter, validator=attrs.validators.instance_of(CompetitorClass))
	_reserve: int|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(int)))
	_status: int = attrs.field(validator=attrs.validators.instance_of(int))

	def isConfirmed(self) -> bool:
		return self._status == 1

	def isWithdrawn(self) -> bool:
		return self._status == 2

	def isNotConfirmed(self) -> bool:
		return self._status == 0

	def isReserve(self) -> bool:
		if self._reserve is not None:
			return self._reserve > 0
		return False

	def getCompetitor(self) -> CompetitorClass:
		return self._competitor

@typeguard.typechecked
def DistanceCombinationCompetitorClass_converter(data: DistanceCombinationCompetitorClass|dict[str, typing.Any]) -> DistanceCombinationCompetitorClass:
	return utils.class_converter_except(data, DistanceCombinationCompetitorClass)

@typeguard.typechecked
def DistanceCombinationCompetitorClassTuple_converter(data: tuple[DistanceCombinationCompetitorClass,...]|list[dict[str, typing.Any]]) -> tuple[DistanceCombinationCompetitorClass,...]:
	return utils.ClassTuple_converter(data, DistanceCombinationCompetitorClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class DistanceCombinationCompetitorsClass(base.BaseClass):
	_id: uuid.UUID = attrs.field(converter=utils.uuid_converter, validator=attrs.validators.instance_of(uuid.UUID)) # type: ignore [misc]
	_number: int = attrs.field(validator=attrs.validators.instance_of(int))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))
	_classFilter: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_categoryFilter: categories.CategoryFilterClass|None = attrs.field(converter=categories.CategoryFilterClass_converter_none, validator=attrs.validators.optional(attrs.validators.instance_of(categories.CategoryFilterClass))) # type: ignore [misc]
	_competitors: tuple[DistanceCombinationCompetitorClass, ...] = attrs.field(converter=DistanceCombinationCompetitorClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(DistanceCombinationCompetitorClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	def getId(self) -> uuid.UUID:
		return self._id

	def getTuple(self) -> tuple[DistanceCombinationCompetitorClass, ...]:
		return self._competitors

@typeguard.typechecked
def DistanceCombinationCompetitorsClass_converter(data: DistanceCombinationCompetitorsClass|dict[str, typing.Any]) -> DistanceCombinationCompetitorsClass:
	return utils.class_converter_except(data, DistanceCombinationCompetitorsClass)

@typeguard.typechecked
def DistanceCombinationCompetitorsClassTuple_converter(data: tuple[DistanceCombinationCompetitorsClass,...]|list[dict[str, typing.Any]]) -> tuple[DistanceCombinationCompetitorsClass,...]:
	return utils.ClassTuple_converter(data, DistanceCombinationCompetitorsClass)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=False, slots=False, hash=True, str=False, eq=False, order=False)
class CompetitorsClass(base.BaseClass):
	_distance_combination_competitors: tuple[DistanceCombinationCompetitorsClass, ...] = attrs.field(converter=DistanceCombinationCompetitorsClassTuple_converter, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(DistanceCombinationCompetitorsClass),
		iterable_validator=attrs.validators.instance_of(tuple)))

	def getTuple(self) -> tuple[DistanceCombinationCompetitorsClass, ...]:
		return self._distance_combination

	def count(self, club_code_filter: int|None = None, category_filter: categories.CategoryFilterClass|None = None, include_withdrawn: bool = False, include_reserve: bool = False, inlcude_unconfirmed: bool = False, unique: bool = True) -> int:
		count: int = 0
		unique_competitors: set[uuid.UUID] = set()
		for dcc in self._distance_combination_competitors:
			for c in dcc.getTuple():
				if c.isWithdrawn() and not include_withdrawn:
					continue
				if c.isReserve() and not include_reserve:
					continue
				if c.isNotConfirmed() and not inlcude_unconfirmed:
					continue

				competitor = c.getCompetitor()
				if not competitor.isNaturalPerson():
					continue

				club_code: int|None = competitor.getClubCode()
				if club_code is None:
					club_code = 0
				if club_code_filter is not None and club_code != club_code_filter:
					continue

				if category_filter is not None and not category_filter.hasCategory(competitor.getCategory()):
					continue

				if unique and competitor.getId() in unique_competitors:
					continue
				elif unique:
					unique_competitors.add(competitor.getId())

				count += 1
		return count

	def getClubCodes(self, include_withdrawn: bool = False, include_reserve: bool = False, inlcude_unconfirmed: bool = False) -> set[int]:
		unique_club_codes: set[int] = set()
		for dcc in self._distance_combination_competitors:
			for c in dcc.getTuple():
				if c.isWithdrawn() and not include_withdrawn:
					continue
				if c.isReserve() and not include_reserve:
					continue
				if c.isNotConfirmed() and not inlcude_unconfirmed:
					continue

				competitor = c.getCompetitor()
				if not competitor.isNaturalPerson():
					continue

				club_code: int|None = competitor.getClubCode()
				if club_code is None:
					club_code = 0
				if not club_code in unique_club_codes:
					unique_club_codes.add(club_code)

		return unique_club_codes

	def getLicenseKeys(self, club_code_filter: int|None = None, category_filter: categories.CategoryFilterClass|None = None, include_withdrawn: bool = False, include_reserve: bool = False, inlcude_unconfirmed: bool = False) -> set[str]:
		unique_license_key: set[str] = set()
		for dcc in self._distance_combination_competitors:
			for c in dcc.getTuple():
				if c.isWithdrawn() and not include_withdrawn:
					continue
				if c.isReserve() and not include_reserve:
					continue
				if c.isNotConfirmed() and not inlcude_unconfirmed:
					continue

				competitor = c.getCompetitor()
				if not competitor.isNaturalPerson():
					continue

				club_code: int|None = competitor.getClubCode()
				if club_code is None:
					club_code = 0
				if club_code_filter is not None and club_code != club_code_filter:
					continue

				if category_filter is not None and not category_filter.hasCategory(competitor.getCategory()):
					continue

				if not competitor.getLicenseKey() in unique_license_key:
					unique_license_key.add(competitor.getLicenseKey())

		return unique_license_key

	def hasCompetitor(self, license_key: str, include_withdrawn: bool = False, include_reserve: bool = False, inlcude_unconfirmed: bool = False) -> bool:
		for dcc in self._distance_combination_competitors:
			for c in dcc.getTuple():
				if c.isWithdrawn() and not include_withdrawn:
					continue
				if c.isReserve() and not include_reserve:
					continue
				if c.isNotConfirmed() and not inlcude_unconfirmed:
					continue

				if c.getCompetitor().getLicenseKey() == license_key:
					return True
		return False

@typeguard.typechecked
def CompetitorsClassClass_converter(data: CompetitorsClass|dict[str, typing.Any]) -> CompetitorsClass:
	return utils.class_converter_except(data, CompetitorsClass)
