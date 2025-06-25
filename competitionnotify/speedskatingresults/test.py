#!/usr/bin/python

import typing
import asyncio
import typeguard

import competitionnotify.utils.utils as utils
import competitionnotify.dataclasses.distance as distance
import competitionnotify.speedskatingresults.classes as classes
import competitionnotify.speedskatingresults.SpeedSkatingResults as ssr

U = typing.TypeVar('U', bound=classes.BaseSkaterClass) # Declare type variable "U"

@typeguard.typechecked
def getSkater(pbs: list[U], id: classes.NameClass) -> U|None:
	for pb in pbs:
		if pb.getSkater() == id.getId():
			return pb
	return None

@typeguard.typechecked
async def main() -> None:
	season = 2014
	skaters_id = await ssr.SpeedSkatingResults.getId([
		{'familyname': "Goedhart", 'givenname': "Martijn", 'country': "NED", 'gender': 'm'},
		{'familyname': "Goedhart", 'givenname': "Jos", 'country': "NED", 'gender': 'm'},
		{'familyname': "van den Bout", 'givenname': "Frans Nico", 'country': "NED", 'gender': 'm'},
		{'familyname': "Faber", 'givenname': "Swen", 'country': "NED", 'gender': 'm'}])

	pbs = await ssr.SpeedSkatingResults.getPersonalRecord(skaters_id)
	sbs = await ssr.SpeedSkatingResults.getSeasonBest(skaters_id, None, season)
	cs = await ssr.SpeedSkatingResults.getCompetitionList(skaters_id, season)

	ds = {}
	for d in distance.DistanceValueClass.allDistances():
		ds[d] = await ssr.SpeedSkatingResults.getDistanceResult(skaters_id, d, season)

	for id in skaters_id:
		pb = getSkater(pbs, id)
		sb = getSkater(sbs, id)
		c = getSkater(cs, id)

		print(id.getFullName() + " (" + id.getCategory() + ")")

		if pb is not None:
			print("\tPersoonlijke Records")
			for d in distance.DistanceValueClass.allDistances():
				t = pb.getDistanceTime(d)
				if t is not None:
					print("\t\t" + str(d) + ": " + str(t))

		if sb is not None:
			print("\tSeizoens Records (" + str(season) + "/" + str(season + 1) + ")")
			for d in distance.DistanceValueClass.allDistances():
				t = sb.getDistanceTime(d)
				if t is not None:
					print("\t\t" + str(d) + ": " + str(t))

		if c is not None and c.hasCompetitions():
			print("\tWedstrijden")
			for r in c.getCompetitions():
				print("\t\t" + str(r.getStartdate()) + " - " + r.getName())

		print("\tTijden")
		for d in distance.DistanceValueClass.allDistances():
			if d in ds:
				for races in ds[d]:
					if races.getSkater() == id.getId() and races.hasResults():
						for race in races.getResults():
							print("\t\t" + str(race.getDistance()) + ": " + str(race.getTime()) + " - " + race.getName() + " (" + str(race.getDate()) + ") - " + race.getLocation())

	return None

if __name__ == '__main__':
	asyncio.run(main())