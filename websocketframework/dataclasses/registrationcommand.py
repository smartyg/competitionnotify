#!/bin/python

import collections.abc
#import abc
import typing
import types
import typeguard
import inspect
import logging
import attrs

import websocketframework.types as wst
import websocketframework.exceptions.wrongdatatype as wdt
import websocketframework.dataclasses.registrationcommandargument as rca

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class RegistrationCommand:
	_function: collections.abc.Callable[..., wst.DataType] = attrs.field(validator=attrs.validators.instance_of(collections.abc.Callable))
	_arguments: dict[str, rca.RegistrationCommandArgument] = attrs.field(validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(rca.RegistrationCommandArgument),
            mapping_validator=attrs.validators.instance_of(dict)))
	_return_type: type|types.GenericAlias = attrs.field(validator=attrs.validators.or_(attrs.validators.instance_of(type), attrs.validators.instance_of(types.GenericAlias)))
	_help: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def call(self, data: dict[str, typing.Any]|None = None) -> wst.DataType:
		call_dict: dict[str, typing.Any] = {}
		for param_name in self._arguments:
			value = None
			if data is not None:
				value = data.get(param_name)
			param = self._arguments.get(param_name, None)
			assert param is not None, "Parameter name '" + param_name + "' not found in parameter list of command."
			if value is None and param._has_default:
				continue
			elif value is None:
				raise wdt.WrongDataType("Paramater '" + param_name + "' is not provided.")
			typeguard.check_type(value, param._type)
			call_dict[param_name] = value

		ret = self._function(**call_dict)
		if self._return_type is not inspect.Signature.empty:
			typeguard.check_type(ret, self._return_type)
		return ret
