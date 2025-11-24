#!/bin/python

import collections.abc
import typing
import typeguard
import inspect
import logging
import attrs
import uuid

import websocketframework.types as wst
import websocketframework.exceptions.unknowncommand as uc
import websocketframework.websocketinterface as wsi
import websocketframework.dataclasses.registrationcommand as rc
import websocketframework.dataclasses.registrationcommandargument as rca

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class Registration:
	_instance: wsi.WebsocketInterface = attrs.field(validator=attrs.validators.instance_of(wsi.WebsocketInterface))
	_name: str = attrs.field(init=False, validator=attrs.validators.instance_of(str))
	_commands: dict[str, rc.RegistrationCommand] = attrs.field(init=False, validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(rc.RegistrationCommand),
            mapping_validator=attrs.validators.instance_of(dict)))

	def __attrs_post_init__(self):
		print("register module: " + str(self._instance.getName()))
		commands: wst.CommandList = self._instance.getCommands()
		typeguard.check_type(commands, wst.CommandList)
		registration: dict[str, rc.RegistrationCommand] = {}
		for c in commands:
			print("command: " + str(c[0]))
			func = c[1]
			help_str = None if len(c) < 3 else c[2]
			typeguard.check_type(func, wst.Callback)
			sig = inspect.signature(func)
			func_args: dict[str, rca.RegistrationCommandArgument] = dict()
			for parameter in sig.parameters.values():
				print("  argument: " + parameter.name)
				name: str = parameter.name
				has_default: bool = False if parameter.default == parameter.empty else True
				#print(type(parameter.annotation))
				#print(parameter.annotation))
				func_args[name] = rca.RegistrationCommandArgument(argument=name, type=parameter.annotation, has_default=has_default)

			func_return = sig.return_annotation
			registration[c[0]] = rc.RegistrationCommand(function=func, arguments=func_args, return_type=func_return, help=help_str)

		object.__setattr__(self, "_name", self._instance.getName())
		object.__setattr__(self, "_commands", registration)

	def getInstance(self) -> wsi.WebsocketInterface:
		return self._instance

	def hasCommand(self, command: str) -> bool:
		return True if command in self._commands else False

	def call(self, client_id: uuid.UUID, command: str, data: dict[str, typing.Any] = {}) -> wst.DataType:
		if not self.hasCommand(command):
			raise uc.UnknownCommand("There is no such command '" + command + "' in module '" + self._name + "'.")
		else:
			cmd = self._commands.get(command)
			assert cmd is not None, "Command '" + command + "' is not a registered command."
			data['client_id'] = client_id
			return cmd.call(data)

	def list_all(self) -> dict[str, str|None]:
		ret: dict[str, str|None] = {}
		for cmd in self._commands:
			ret[cmd] = self._commands[cmd]._help
		return ret
