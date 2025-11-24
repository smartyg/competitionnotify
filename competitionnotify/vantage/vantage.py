#!/usr/bin/python
import typing
import typeguard
import attrs
import datetime
import dateutil.relativedelta
import asyncio
import aiohttp
import json

import traceback

import competitionnotify.dataclasses.base as base
import competitionnotify.dataclasses.distance as distance
import competitionnotify.utils.utils as utils


# https://tijden-service.schaatsen.nl/api/SearchSkater?name=Martijn%20Goedhart
# https://tijden-service.schaatsen.nl/api/SkaterTimes?id=521a5f8d-1158-4cfa-8b89-9ad196b1a7bf

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultClass(base.BaseClass):
	_season: int
	_raceDate: datetime.date = attrs.field(converter=classes.datetime_converter, validator=attrs.validators.instance_of(datetime.date))
	_venue: str = attrs.field(validator=attrs.validators.instance_of(str))
	_venueCity: str = attrs.field(validator=attrs.validators.instance_of(str))
	_venueCountry: str = attrs.field(validator=attrs.validators.instance_of(str))
	_raceTime: time.TimeClass = attrs.field(converter=time.TimeClass_converter, validator=attrs.validators.instance_of(time.TimeClass))
	_distance: distance.DistanceValueClass = attrs.field(converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_discipline: discipline.DisciplineClass
	_competitionName: str = attrs.field(validator=attrs.validators.instance_of(str))


@attrs.define(frozen=True, kw_only=True, slots=False)
class DistanceResults(base.BaseClass):
	_distance: distance.DistanceValueClass = attrs.field(converter=distance.DistanceValueClass_converter, validator=attrs.validators.instance_of(distance.DistanceValueClass))
	_races: list[ResultClass]

@attrs.define(frozen=True, kw_only=True, slots=False)
class Nameclass(base.BaseClass):
	_id: uuid.UUID
	_name: skater.PersonNameClass
	_birthDateDisplay: str
	_iocCode: str|None
	_gender: str

@attrs.define(frozen=True, kw_only=True, slots=False)
class ResultsClass(base.BaseClass):
	_skater: Nameclass
	_races: list[DistanceResults]