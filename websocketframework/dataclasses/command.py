#!/bin/python

import typeguard
import logging
import attrs

import competitionnotify.dataclasses.base as base

import websocketframework.types as wst

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class Command(base.BaseClass):
	_module: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_command: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_data: wst.DataType = base.BaseClass.serializable(True) #TODO: check type is json parsable
	_response: int = base.BaseClass.serializable(True, default=-1, validator=attrs.validators.instance_of(int))

	def getModule(self) -> str:
		return self._module

	def getCommand(self) -> str:
		return self._command

	def getData(self) -> wst.DataType:
		return self._data

	def hasData(self) -> bool:
		return True if self._data is not None else False

	def response(self, response: int, data: wst.DataType) -> "Command":
		return attrs.evolve(self, response=response, data=data)
