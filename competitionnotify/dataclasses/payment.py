#!/bin/python

import typing
import typeguard
import attrs
import logging

import competitionnotify.dataclasses.base as base
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class PaymentClass(base.BaseClass):
	_currency: str = attrs.field(validator=attrs.validators.instance_of(str))
	_price: float = attrs.field(validator=attrs.validators.instance_of(float))

@typeguard.typechecked
def PaymentClass_converter(data: PaymentClass|dict[str, typing.Any]) -> PaymentClass:
	return utils.class_converter_except(data, PaymentClass)

@typeguard.typechecked
def PaymentClass_converter_none(data: PaymentClass|dict[str, typing.Any]|None) -> PaymentClass|None:
	return utils.class_converter_none(data, PaymentClass)