#!/usr/bin/python

import typeguard
import attrs
import logging
import json
import uuid
import typing
import matplotlib.pyplot as plt
import numpy
import csv

import competitionnotify.classes.base as base
import competitionnotify.classes.discipline as discipline
import competitionnotify.classes.competition as competition
import competitionnotify.classes.distance_combination_competitors as distance_combination_competitors
import competitionnotify.classes.categories as categories

logger = logging.getLogger(__name__)

pupillen_category_filter = categories.CategoryFilterClass.fromString("*P*")
junioren_category_filter = categories.CategoryFilterClass.fromString("*C*|*B*|*A*")
neosenioren_category_filter = categories.CategoryFilterClass.fromString("*N*")
senioren_category_filter = categories.CategoryFilterClass.fromString("*S*")
masters_category_filter = categories.CategoryFilterClass.fromString("*M*")


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class Stats(base.BaseClass):
	_total: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_pupillen: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_junioren: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_neosenioren: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_senioren: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))
	_masters: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))

	_total_license_keys: set[str]  = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(set)))
	_pupillen_license_keys: set[str]  = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(set)))
	_junioren_license_keys: set[str]  = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(set)))
	_neosenioren_license_keys: set[str]  = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(set)))
	_senioren_license_keys: set[str]  = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(set)))
	_masters_license_keys: set[str]  = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(str),
		iterable_validator=attrs.validators.instance_of(set)))

	def toList(self) -> list[int]:
		return [
			self._total,
			len(self._total_license_keys),

			self._pupillen,
			len(self._pupillen_license_keys),

			self._junioren,
			len(self._junioren_license_keys),

			self._neosenioren,
			len(self._neosenioren_license_keys),

			self._senioren,
			len(self._senioren_license_keys),

			self._masters,
			len(self._masters_license_keys),
		]

	def __add__(self, other: "Stats") -> "Stats":
		if isinstance(other, Stats):
			return Stats(
				total=self._total + other._total,
				pupillen=self._pupillen + other._pupillen,
				junioren=self._junioren + other._junioren,
				neosenioren=self._neosenioren + other._neosenioren,
				senioren=self._senioren + other._senioren,
				masters=self._masters + other._masters,

				total_license_keys=self._total_license_keys.union(other._total_license_keys),
				pupillen_license_keys=self._pupillen_license_keys.union(other._pupillen_license_keys),
				junioren_license_keys=self._junioren_license_keys.union(other._junioren_license_keys),
				neosenioren_license_keys=self._neosenioren_license_keys.union(other._neosenioren_license_keys),
				senioren_license_keys=self._senioren_license_keys.union(other._senioren_license_keys),
				masters_license_keys=self._masters_license_keys.union(other._masters_license_keys),
			)
		else:
			raise ValueError("Wrong type is given.")

	@classmethod
	def empty(cls):
		return Stats(
			total=0,
			pupillen=0,
			junioren=0,
			neosenioren=0,
			senioren=0,
			masters=0,

			total_license_keys=set(),
			pupillen_license_keys=set(),
			junioren_license_keys=set(),
			neosenioren_license_keys=set(),
			senioren_license_keys=set(),
			masters_license_keys=set(),
		)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class CompetitionClubStats(Stats):
	_club: int = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(int))

	@classmethod
	def make(cls, club_code: int, competitors: distance_combination_competitors.CompetitorsClass):
		return cls(
			club=club_code,
			total=competitors.count(club_code),
			total_license_keys=competitors.getLicenseKeys(club_code),

			pupillen=competitors.count(club_code, pupillen_category_filter),
			pupillen_license_keys=competitors.getLicenseKeys(club_code, pupillen_category_filter),

			junioren=competitors.count(club_code, junioren_category_filter),
			junioren_license_keys=competitors.getLicenseKeys(club_code, junioren_category_filter),

			neosenioren=competitors.count(club_code, neosenioren_category_filter),
			neosenioren_license_keys=competitors.getLicenseKeys(club_code, neosenioren_category_filter),

			senioren=competitors.count(club_code, senioren_category_filter),
			senioren_license_keys=competitors.getLicenseKeys(club_code, senioren_category_filter),

			masters=competitors.count(club_code, masters_category_filter),
			masters_license_keys=competitors.getLicenseKeys(club_code, masters_category_filter),
		)


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class CompetitionStats(Stats):
	_clubs: set[int] = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(int),
		iterable_validator=attrs.validators.instance_of(set)))
	_club_stats: tuple[CompetitionClubStats, ...] = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(CompetitionClubStats),
		iterable_validator=attrs.validators.instance_of(tuple)))

	@classmethod
	def make(cls, competitors: distance_combination_competitors.CompetitorsClass):
		all_clubs: set[int] = competitors.getClubCodes()
		club_stats_list: list[CompetitionClubStats] = list()
		for club_code in all_clubs:
			if club_code is None:
				continue
			club_stats_list.append(CompetitionClubStats.make(club_code, competitors))
		return cls(
			total=competitors.count(),
			total_license_keys=competitors.getLicenseKeys(),

			pupillen=competitors.count(None, pupillen_category_filter),
			pupillen_license_keys=competitors.getLicenseKeys(None, pupillen_category_filter),

			junioren=competitors.count(None, junioren_category_filter),
			junioren_license_keys=competitors.getLicenseKeys(None, junioren_category_filter),

			neosenioren=competitors.count(None, neosenioren_category_filter),
			neosenioren_license_keys=competitors.getLicenseKeys(None, neosenioren_category_filter),

			senioren=competitors.count(None, senioren_category_filter),
			senioren_license_keys=competitors.getLicenseKeys(None, senioren_category_filter),

			masters=competitors.count(None, masters_category_filter),
			masters_license_keys=competitors.getLicenseKeys(None, masters_category_filter),

			clubs=all_clubs,
			club_stats=tuple(club_stats_list),
		)

	def getClubStats(self, club_code: int) -> CompetitionClubStats|None:
		for c in self._club_stats:
			if c._club == club_code:
				return c
		return None


@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False, hash=False, str=False, eq=False, order=False)
class SummaryStats(base.BaseClass):
	_competitions: tuple[CompetitionStats, ...] = base.BaseClass.serializable(True, validator=attrs.validators.deep_iterable( # type: ignore [misc]
		member_validator=attrs.validators.instance_of(CompetitionStats),
		iterable_validator=attrs.validators.instance_of(tuple)))

	def getClubCodes(self) -> set[int]:
		clubs: set[int] = set()
		for competition in self._competitions:
			clubs = clubs.union(competition._clubs)
		return clubs

	def getTotal(self) -> int:
		total: int = 0
		for competition in self._competitions:
			total += competition._total
		return total

	def getTotalClub(self, club_code: int) -> int:
		total: int = 0
		for competition in self._competitions:
			club_stats = competition.getClubStats(club_code)
			if club_stats is None:
				continue
			total += club_stats._total
		return total

	def getTotals(self) -> Stats:
		total_stats: Stats = Stats.empty()
		for competition in self._competitions:
			total_stats += competition
		return total_stats

	def getTotalsClub(self, club_code: int) -> Stats:
		total_club_stats: Stats = Stats.empty()
		for competition in self._competitions:
			club_stats = competition.getClubStats(club_code)
			if club_stats is None:
				continue
			total_club_stats += club_stats
		return total_club_stats

	def getLicenseKeysOccurence(self) -> dict[str, int]:
		result: dict[str, int] = {}
		for competition in self._competitions:
			for license in competition._total_license_keys:
				if license in result:
					result[license] += 1
				else:
					result[license] = 1
		return result

	def getLicenseKeysOccurences(self) -> dict[str, dict[str, int]]:
		totals: dict[str, dict[str, int]] = {
			'total': {},
			'pupillen': {},
			'junioren': {},
			'neosenioren': {},
			'senioren': {},
			'masters': {},
		}
		for competition in self._competitions:
			for license in competition._total_license_keys:
				if license in totals['total']:
					totals['total'][license] += 1
				else:
					totals['total'][license] = 1

			for license in competition._pupillen_license_keys:
				if license in totals['pupillen']:
					totals['pupillen'][license] += 1
				else:
					totals['pupillen'][license] = 1

			for license in competition._junioren_license_keys:
				if license in totals['junioren']:
					totals['junioren'][license] += 1
				else:
					totals['junioren'][license] = 1

			for license in competition._neosenioren_license_keys:
				if license in totals['neosenioren']:
					totals['neosenioren'][license] += 1
				else:
					totals['neosenioren'][license] = 1

			for license in competition._senioren_license_keys:
				if license in totals['senioren']:
					totals['senioren'][license] += 1
				else:
					totals['senioren'][license] = 1

			for license in competition._masters_license_keys:
				if license in totals['masters']:
					totals['masters'][license] += 1
				else:
					totals['masters'][license] = 1
		return totals

	def getLicenseKeysOccurencesClub(self, club_code) -> dict[str, dict[str, int]]:
		totals: dict[str, dict[str, int]] = {
			'total': {},
			'pupillen': {},
			'junioren': {},
			'neosenioren': {},
			'senioren': {},
			'masters': {},
		}
		for competition in self._competitions:
			club_stats = competition.getClubStats(club_code)
			if club_stats is None:
				continue

			for license in club_stats._total_license_keys:
				if license in totals['total']:
					totals['total'][license] += 1
				else:
					totals['total'][license] = 1

			for license in club_stats._pupillen_license_keys:
				if license in totals['pupillen']:
					totals['pupillen'][license] += 1
				else:
					totals['pupillen'][license] = 1

			for license in club_stats._junioren_license_keys:
				if license in totals['junioren']:
					totals['junioren'][license] += 1
				else:
					totals['junioren'][license] = 1

			for license in club_stats._neosenioren_license_keys:
				if license in totals['neosenioren']:
					totals['neosenioren'][license] += 1
				else:
					totals['neosenioren'][license] = 1

			for license in club_stats._senioren_license_keys:
				if license in totals['senioren']:
					totals['senioren'][license] += 1
				else:
					totals['senioren'][license] = 1

			for license in club_stats._masters_license_keys:
				if license in totals['masters']:
					totals['masters'][license] += 1
				else:
					totals['masters'][license] = 1
		return totals


@typeguard.typechecked
def loadCompetitions() -> list[competition.CompetitionClass]:
	test_file: str = "./test_data/2025-2026/competitions.json"
	json_data: list[dict[str, typing.Any]]

	print("Process file: " + test_file)
	with open(test_file, "r") as f:
		json_data = json.load(f)

	result: list[competition.CompetitionClass] = []
	for d in json_data:
		result.append(competition.CompetitionClass_converter(data=d))

	return result


@typeguard.typechecked
def loadCompetitionCompetitors(id: str) -> CompetitionStats:
	test_file: str = "./test_data/2025-2026/" + id + "-competitors.json"
	json_data: list[dict[str, typing.Any]]

	print("Process file: " + test_file)
	with open(test_file, "r") as f:
		json_data = json.load(f)
	competitors = distance_combination_competitors.CompetitorsClass(distance_combination_competitors=json_data)

	return CompetitionStats.make(competitors)


@typeguard.typechecked
def getOccurence(data: dict[str, int], max_range: int|None = None) -> dict[int, int]:
	occurence_values = list(data.values())
	occurence_range_start = 1
	occurence_range_end = max(occurence_values) if max_range is None else max_range
	occurence_range = range(occurence_range_start, occurence_range_end+1)
	occurence: dict[int, int] = {}
	for o in occurence_range:
		occurence[o] = occurence_values.count(o)
	return occurence


@typeguard.typechecked
def getOccurences(data: dict[str, dict[str, int]], range_end: int|None = None) -> dict[str, dict[int, int]]:
	total_occurence = getOccurence(data['total'], range_end)
	if range_end is None:
		range_end = len(total_occurence)
	return {
		'total': total_occurence,
		'pupillen': getOccurence(data['pupillen'], range_end),
		'junioren': getOccurence(data['junioren'], range_end),
		'neosenioren': getOccurence(data['neosenioren'], range_end),
		'senioren': getOccurence(data['senioren'], range_end),
		'masters': getOccurence(data['masters'], range_end),
	}


if __name__ == '__main__':
	competitions_old = [
		"d32c092c-bb47-4ffd-a1ff-dec2fffbae49",
		"812f0fc5-8060-4c30-8389-67295f7199e2",
		"b85e77a3-15be-4341-a81a-2117eb305135",
		"db755c8f-0e4c-43bc-a778-0fbffaf3fc15",
		"2e42f1a3-d74a-46ed-8193-ad71308c2115",
		"d2cd1c52-f758-463b-8269-4028dbe3ff0f",
		"a543db87-c2be-4450-91be-fa556bbd9209",
		"2fb6b9f0-d8fc-46fb-a97d-74f883ee1c38",
		#"e8b158fd-5bad-4762-922a-f6f1a9ed11a8",
	]

	competitions = loadCompetitions()
	discapline_longtrack = discipline.DisciplineClass_converter("SpeedSkating.LongTrack")


	stats = SummaryStats(competitions=tuple([loadCompetitionCompetitors(str(c.getId())) for c in competitions if not c.isTest() and c.getVenueCode() == "AMS" and c.getDiscipline().equal(discapline_longtrack)]))

	#stats = SummaryStats(competitions=tuple([loadCompetitionCompetitors(c) for c in competitions_old]))

	license_occurences = stats.getLicenseKeysOccurences()
	occurences = getOccurences(license_occurences)

	totals = stats.getTotals()
	csv_row: list[int|str] = ["total"]
	csv_rows: list[list[int|str]] = [[
		"club","total participations", "total participants",
		"pupillen participations", "pupillen participants",
		"junioren participations", "junioren participants",
		"neosenioren participations", "neosenioren participants",
		"senioren participations", "senioren participants",
		"masters participations", "masters participants",
	]]
	csv_row.extend(totals.toList())
	csv_rows.append(csv_row)

	fig, ax = plt.subplots(1,6)
	bottom: int = 0 #numpy.zeros(len(occurences['total']))
	bar_width: float = 0.5
	ax[0].set_title("Totaal")
	ax[0].bar(occurences['total'].keys(), occurences['total'].values(), bar_width, label="Totaal", bottom=0)
	ax[1].set_title("Pupillen")
	ax[1].bar(occurences['pupillen'].keys(), occurences['pupillen'].values(), bar_width, label="Totaal", bottom=0)
	ax[2].set_title("Junioren")
	ax[2].bar(occurences['junioren'].keys(), occurences['junioren'].values(), bar_width, label="Totaal", bottom=0)
	ax[3].set_title("Neo-Senioren")
	ax[3].bar(occurences['neosenioren'].keys(), occurences['neosenioren'].values(), bar_width, label="Totaal", bottom=0)
	ax[4].set_title("Senioren")
	ax[4].bar(occurences['senioren'].keys(), occurences['senioren'].values(), bar_width, label="Totaal", bottom=0)
	ax[5].set_title("Masters")
	ax[5].bar(occurences['masters'].keys(), occurences['masters'].values(), bar_width, label="Totaal", bottom=0)

	for club_code in stats.getClubCodes():
		club_license_occurence = stats.getLicenseKeysOccurencesClub(club_code)
		club_totals = stats.getTotalsClub(club_code)
		club_occurences = getOccurences(club_license_occurence, len(occurences['total']))

		csv_row: list[int] = [club_code]
		csv_row.extend(club_totals.toList())
		csv_rows.append(csv_row)

		#if club_code == 6640 or len(club_license_occurence['total']) > (0.1 * len(license_occurences['total'])):
		if club_code == 6640:
			ax[0].bar(occurences['total'].keys(), club_occurences['total'].values(), bar_width, label=str(club_code), bottom=bottom)
			ax[1].bar(occurences['pupillen'].keys(), club_occurences['pupillen'].values(), bar_width, label=str(club_code), bottom=bottom)
			ax[2].bar(occurences['junioren'].keys(), club_occurences['junioren'].values(), bar_width, label=str(club_code), bottom=bottom)
			ax[3].bar(occurences['neosenioren'].keys(), club_occurences['neosenioren'].values(), bar_width, label=str(club_code), bottom=bottom)
			ax[4].bar(occurences['senioren'].keys(), club_occurences['senioren'].values(), bar_width, label=str(club_code), bottom=bottom)
			ax[5].bar(occurences['masters'].keys(), club_occurences['masters'].values(), bar_width, label=str(club_code), bottom=bottom)
			#bottom += list(club_occurences['total'].values())

	filename = "stats.csv"
	with open(filename, 'w') as csvfile:
		csvwriter = csv.writer(csvfile)        # Create writer object
		csvwriter.writerows(csv_rows)

	for i in range(0,6):
		ax[i].legend(loc="upper right")
		ax[i].set_yscale('log', subs=[2, 3, 4, 5, 6, 7, 8, 9])
		ax[i].set_xlim(left=0)
		ax[i].set_xlabel("aantal wedstrijd deelnames")
		ax[i].set_ylabel("aantal personen")
		ax[i].grid(visible=True, which='both', axis='y', alpha=0.3)
		ax[i].set_axisbelow(True)
		ax[i].set_navigate(True)

	# ax[1].legend(loc="upper right")
	# ax[2].legend(loc="upper right")
	# ax[3].legend(loc="upper right")
	# ax[4].legend(loc="upper right")
	# ax[5].legend(loc="upper right")
 #
	# ax[0].set_yscale('log')
	plt.show()
