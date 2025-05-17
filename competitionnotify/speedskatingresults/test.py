#!/usr/bin/python

from typing import TypeVar
from SpeedSkatingResults import SpeedSkatingResults, NameClass, BaseSkaterClass, DistanceClass
import asyncio

U = TypeVar('U', bound=BaseSkaterClass) # Declare type variable "U"
def getSkater(pbs: list[U], id: type[NameClass]) -> U|None:
	for pb in pbs:
		if pb.skater == id.id:
			return pb
	return None

async def main() -> None:
	season = 2014
	skaters_id = await SpeedSkatingResults.getId([
		{'familyname': "Goedhart", 'givenname': "Martijn", 'country': "NED", 'gender': 'm'},
		{'familyname': "Goedhart", 'givenname': "Jos", 'country': "NED", 'gender': 'm'},
		{'familyname': "van den Bout", 'givenname': "Frans Nico", 'country': "NED", 'gender': 'm'},
		{'familyname': "Faber", 'givenname': "Swen", 'country': "NED", 'gender': 'm'}])

	pbs = await SpeedSkatingResults.getPersonalRecord(skaters_id)
	sbs = await SpeedSkatingResults.getSeasonBest(skaters_id, None, season)
	cs = await SpeedSkatingResults.getCompetitionList(skaters_id, season)

	ds = {}
	for d in DistanceClass.allDistances():
		ds[d] = await SpeedSkatingResults.getDistanceResult(skaters_id, d, season)

	for id in skaters_id:
		pb = getSkater(pbs, id)
		sb = getSkater(sbs, id)
		c = getSkater(cs, id)

		print(id.getFullName() + " (" + id.gender + str(id.category) + ")")

		if pb is not None:
			print("\tPersoonlijke Records")
			for d in DistanceClass.allDistances():
				t = pb.getDistanceTime(d)
				if t is not None:
					print("\t\t" + str(d) + ": " + str(t))

		if sb is not None:
			print("\tSeizoens Records (" + str(season) + "/" + str(season + 1) + ")")
			for d in DistanceClass.allDistances():
				t = sb.getDistanceTime(d)
				if t is not None:
					print("\t\t" + str(d) + ": " + str(t))

		if c is not None and c.hasCompetitions():
			print("\tWedstrijden")
			for r in c.competitions:
				print("\t\t" + str(r.startdate) + " - " + r.name)

		print("\tTijden")
		for d in DistanceClass.allDistances():
			if d in ds:
				for races in ds[d]:
					if races.skater == id.id and races.hasResults():
						for race in races.results:
							print("\t\t" + str(race.distance) + ": " + str(race.time) + " - " + race.name + " (" + str(race.date) + ") - " + race.location)

	return None

if __name__ == '__main__':
	asyncio.run(main())
