#!/bin/python

import typing
import typeguard
import attrs
import logging

import competitionnotify.classes.base as base
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False, hash=True, str=False, eq=False, order=False)
class PaymentClass(base.BaseClass):
	_currency: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_price: float = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(float))

	def isSameCurreny(self, o: "PaymentClass") -> bool:
		return self._currency == o._currency

	def getprice(self) -> float:
		return self._price

	def getCurrency(self) -> str:
		return self._currency

	def equal(self, o: "PaymentClass") -> bool:
		return (self._currency == o._currency and
			self._price == o._price)

	def __str__(self) -> str:
		c = self._currency
		p = self._price
		return str(f'{p:0.2} {c}')

	def __repr__(self) -> str:
		return self.__str__()

	def __lt__(self, o: object) -> bool:
		o = typeguard.check_type(o, type(self))
		if self.isSameCurreny(o):
			return self._price < o._price
		return False

	def __le__(self, o: object|float) -> bool:
		o = typeguard.check_type(o, type(self))
		if self.isSameCurreny(o):
			return self._price <= o._price
		return False

	def __gt__(self, o: object|float) -> bool:
		o = typeguard.check_type(o, type(self))
		if self.isSameCurreny(o):
			return self._price > o._price
		return False

	def __ge__(self, o: object|float) -> bool:
		o = typeguard.check_type(o, type(self))
		if self.isSameCurreny(o):
			return self._price >= o._price
		return False

@typeguard.typechecked
def PaymentClass_converter(data: PaymentClass|dict[str, typing.Any]) -> PaymentClass:
	return utils.class_converter_except(data, PaymentClass)

@typeguard.typechecked
def PaymentClass_converter_none(data: PaymentClass|dict[str, typing.Any]|None) -> PaymentClass|None:
	return utils.class_converter_none(data, PaymentClass)