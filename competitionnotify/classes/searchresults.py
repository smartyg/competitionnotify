#!/bin/python

import typing
import typeguard
import attrs
import logging

import competitionnotify.classes.base as base
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class SearchResultsClass(base.BaseClass):
	pass
#	_currency: str = attrs.field(validator=attrs.validators.instance_of(str))
#	_price: float = attrs.field(validator=attrs.validators.instance_of(float))

@typeguard.typechecked
def SearchResultsClass_converter(data: SearchResultsClass|dict[str, typing.Any]) -> SearchResultsClass:
	return utils.class_converter_except(data, SearchResultsClass)

@typeguard.typechecked
def SearchResultsClass_converter_none(data: SearchResultsClass|dict[str, typing.Any]|None) -> SearchResultsClass|None:
	return utils.class_converter_none(data, SearchResultsClass)