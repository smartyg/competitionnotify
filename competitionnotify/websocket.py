#!/bin/python

import collections.abc
import abc
import typing
import types
import typeguard
import inspect
import asyncio
import json
import logging
import websockets.server
import websockets.asyncio.server
import ssl
import attrs
import uuid
import traceback

import competitionnotify.dataclasses.base as base

logger = logging.getLogger(__name__)

DataType = None|bool|int|str|list|dict
Callback = collections.abc.Callable[[uuid.UUID, ...], DataType]|collections.abc.Callable[[uuid.UUID], DataType]
CommandList = collections.abc.Sequence[tuple[str, Callback]|tuple[str, Callback, str]]

@typeguard.typechecked
class ParserException(Exception):
	def __init__(self, message: str, code: int):
		super().__init__()
		self.code = code
		self.message = message

@typeguard.typechecked
class UnknownCommand(ParserException):
	def __init__(self, message):
		super().__init__(message, 400)

@typeguard.typechecked
class WrongDataType(ParserException):
	def __init__(self, message):
		super().__init__(message, 400)

@typeguard.typechecked
class UnknownModule(ParserException):
	def __init__(self, message):
		super().__init__(message, 404)

@typeguard.typechecked
class WebsocketInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, 'getName') and
				callable(subclass.getName) and
				hasattr(subclass, 'getCommands') and
				callable(subclass.getCommands) and
				hasattr(subclass, 'registerWebsocket') and
				callable(subclass.registerWebsocket) or
				NotImplemented)

	@abc.abstractmethod
	def getName(self) -> str:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getCommands(self) -> CommandList:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def registerWebsocket(self, ws: "Websocket") -> bool:
		"""Load in the data set"""
		raise NotImplementedError

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class RegistrationCommandArgument:
	_argument:str = attrs.field(validator=attrs.validators.instance_of(str))
	_type: type|types.GenericAlias|types.UnionType = attrs.field(validator=attrs.validators.or_(attrs.validators.instance_of(type), attrs.validators.instance_of(types.GenericAlias), attrs.validators.instance_of(types.UnionType)))
	_has_default: bool = attrs.field(validator=attrs.validators.instance_of(bool))

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class RegistrationCommand:
	_function: collections.abc.Callable[..., DataType] = attrs.field(validator=attrs.validators.instance_of(collections.abc.Callable))
	_arguments: dict[str, RegistrationCommandArgument] = attrs.field(validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(RegistrationCommandArgument),
            mapping_validator=attrs.validators.instance_of(dict)))
	_return_type: type|types.GenericAlias = attrs.field(validator=attrs.validators.or_(attrs.validators.instance_of(type), attrs.validators.instance_of(types.GenericAlias)))
	_help: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))

	def call(self, data: DataType = None) -> DataType:
		call_dict: dict[str, typing.Any] = {}
		for param_name in self._arguments:
			value = data.get(param_name)
			param = self._arguments.get(param_name, None)
			if value is None and param._has_default:
				continue
			elif value is None:
				raise WrongDataType("Paramater '" + param_name + "' is not provided.")
			typeguard.check_type(value, param._type)
			call_dict[param_name] = value

		ret = self._function(**call_dict)
		if self._return_type is not inspect.Signature.empty:
			typeguard.check_type(ret, self._return_type)
		return ret

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class Registration:
	_instance: WebsocketInterface = attrs.field(validator=attrs.validators.instance_of(WebsocketInterface))
	_name: str = attrs.field(init=False, validator=attrs.validators.instance_of(str))
	_commands: dict[str, RegistrationCommand] = attrs.field(init=False, validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(RegistrationCommand),
            mapping_validator=attrs.validators.instance_of(dict)))

	def __attrs_post_init__(self):
		print("register module: " + str(self._instance.getName()))
		commands: CommandList = self._instance.getCommands()
		typeguard.check_type(commands, CommandList)
		registration: dict[str, RegistrationCommand] = {}
		for c in commands:
			print("command: " + str(c[0]))
			func = c[1]
			help_str = None if len(c) < 3 else c[2]
			typeguard.check_type(func, Callback)
			sig = inspect.signature(func)
			func_args: dict[str, RegistrationCommandArgument] = dict()
			for parameter in sig.parameters.values():
				print("  argument: " + parameter.name)
				name: str = parameter.name
				has_default: bool = False if parameter.default == parameter.empty else True
				#print(type(parameter.annotation))
				#print(parameter.annotation))
				func_args[name] = RegistrationCommandArgument(argument=name, type=parameter.annotation, has_default=has_default)

			func_return = sig.return_annotation
			registration[c[0]] = RegistrationCommand(function=func, arguments=func_args, return_type=func_return, help=help_str)

		object.__setattr__(self, "_name", self._instance.getName())
		object.__setattr__(self, "_commands", registration)

	def getInstance(self) -> WebsocketInterface:
		return self._instance

	def hasCommand(self, command: str) -> bool:
		return True if command in self._commands else False

	def call(self, client_id: uuid.UUID, command: str, data: DataType = None) -> DataType:
		if not self.hasCommand(command):
			raise UnknownCommand("There is no such command '" + command + "' in module '" + self._name + "'.")
		else:
			cmd = self._commands.get(command)
			data['client_id'] = client_id
			return cmd.call(data)

	def list_all(self) -> dict[str, str|None]:
		ret: dict[str, str|None] = {}
		for cmd in self._commands:
			ret[cmd] = self._commands[cmd]._help
		return ret

@typeguard.typechecked
@attrs.define(frozen=True, kw_only=True, slots=False)
class Command(base.BaseClass):
	_response: int = base.BaseClass.serializable(True, default=-1, validator=attrs.validators.instance_of(int))
	_module: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_command: str = base.BaseClass.serializable(True, validator=attrs.validators.instance_of(str))
	_data: DataType = base.BaseClass.serializable(True) #TODO: check type is json parsable

	def getModule(self) -> str:
		return self._module

	def getCommand(self) -> str:
		return self._command

	def getData(self) -> DataType:
		return self._data

	def hasData(self) -> bool:
		return True if self._data is not None else False

	def response(self, response: int, data: DataType) -> "Command":
		return attrs.evolve(self, response=response, data=data)

@typeguard.typechecked
@attrs.define(frozen=False, kw_only=True, slots=False)
class Websocket(WebsocketInterface):
	_host: str = attrs.field(default="0.0.0.0", validator=attrs.validators.instance_of(str))
	_port: int = attrs.field(default=6789, validator=attrs.validators.instance_of(int))
	_ssl_cert: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_ssl_key: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_modules: dict[str, Registration] = attrs.field(default=dict(), init=False, validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(Registration),
            mapping_validator=attrs.validators.instance_of(dict)))
	_connections: set[websockets.asyncio.server.ServerConnection] = attrs.field(default=set(), init=False, validator=attrs.validators.deep_iterable(
            member_validator=attrs.validators.instance_of(websockets.asyncio.server.ServerConnection),
            iterable_validator=attrs.validators.instance_of(set)))
	_ssl_context: ssl.SSLContext|None = attrs.field(default=None, init=False, validator=attrs.validators.optional(attrs.validators.instance_of(ssl.SSLContext)))
	_server: websockets.asyncio.server.serve|None = attrs.field(default=None, init=False, validator=attrs.validators.optional(attrs.validators.instance_of(websockets.asyncio.server.serve)))

	def __attrs_post_init__(self):
		if self._ssl_cert is not None and self._ssl_key is not None:
			self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			self._ssl_context.load_cert_chain(self._ssl_cert, keyfile=self._ssl_key)
		self.registerModule(self)
		self._server = websockets.serve(self._connection, self._host, self._port, ssl=self._ssl_context)

	async def run(self):
		ws = await self._server
		await ws.serve_forever()

	@typeguard.typechecked
	def registerModule(self, module: WebsocketInterface) -> bool:
		typeguard.check_type(module, WebsocketInterface)
		if isinstance(module, WebsocketInterface):
			name = module.getName()

			if name in self._modules.keys():
				return False
			else:
				self._modules[name] = Registration(instance=module)
				return module.registerWebsocket(self)
		return False

	@typeguard.typechecked
	def unregisterModule(self, module: WebsocketInterface) -> None:
		typeguard.check_type(module, WebsocketInterface)
		try:
			if module.getName() in self._modules:
				del self._modules[module.getName()]
		finally:
			return

	async def _connection(self, client: websockets.asyncio.server.ServerConnection) -> None:
		client_id = client.id
		print("New connection from client: " + str(client_id))
		self._registerClient(client)
		try:
			async for message in client:
				response: Command
				try:
					data = json.loads(message)
					if not isinstance(data, dict):
						raise WrongDataType("Data is not correctly formatted.")
					cmd = Command(**data)

					if cmd.getModule() not in self._modules:
						raise UnknownModule("There is no such module '" + str(cmd.getModule()) + "'.")

					m: Registration|None = self._modules.get(cmd.getModule(), None)
					if not isinstance(m, Registration):
						raise UnknownModule("There is no such module '" + str(cmd.getModule()) + "'.")

					if not m.hasCommand(cmd.getCommand()):
						raise UnknownCommand("There is no such command '" + str(cmd.getCommand()) + "' in module '" + str(cmd.getModule()) + "'.")

					ret_data: DataType = m.call(client_id, cmd.getCommand(), cmd.getData())
					response = cmd.response(200, ret_data)

				except json.JSONDecodeError as e:
					print("JSONDecodeError: " + str(e.msg))
					print(str(e.__traceback__))
					response = Command(response=400,
											module='',
											command='',
											data=e.msg)
					print(str(response))
				except ParserException as e:
					print("ParserException: " + str(e.message))
					print(str(e.__traceback__))
					response = Command(response=e.code,
											module='',
											command='',
											data=e.message)
				except BaseException as e:
					msg = str(e)
					print("BaseException: " + str(msg))
					print(str(e.__traceback__))
					traceback.print_tb(e.__traceback__)
					response = Command(response=404,
											module='',
											command='',
											data=msg)
				finally:
					#print(str(response))
					#print(response.json())
					await client.send(response.json())
		except websockets.exceptions.ConnectionClosedError as e:
			print("Error while closing connection with client " + str(client_id))

		finally:
			print("Close connection with client " + str(client_id))
			self._unregisterClient(client)

	@typeguard.typechecked
	def _registerClient(self, client: websockets.asyncio.server.ServerConnection) -> None:
		self._connections.add(client)

	@typeguard.typechecked
	def _unregisterClient(self, client: websockets.asyncio.server.ServerConnection) -> None:
		self._connections.remove(client)

	def getName(self) -> str:
		return "main"

	def getCommands(self) -> CommandList:
		return (
			("connection_id", self._cmd_connection_id),
			("clients", self._cmd_clients),
			("ip", self._cmd_ip),
			("version", self._cmd_version),
			("purge", self._cmd_purge),
			("modules", self._cmd_modules),
			("help", self._cmd_help, "List all modules and commands"),
			)

	def _cmd_connection_id(self, client_id: uuid.UUID) -> str:
			return str(client_id)

	def _cmd_clients(self, client_id: uuid.UUID) -> list[str]:
		return [str(client.id) for client in self._connections]

	def _cmd_ip(self, client_id: uuid.UUID):
		for client in self._connections:
			if client.id == client_id:
				return client.remote_address[0]

	def _cmd_version(self, client_id: uuid.UUID) -> str:
			return "0.1"

	def _cmd_purge(self, client_id: uuid.UUID, data: bool) -> bool:
		if data:
			return True
		else:
			return False

	def _cmd_modules(self, client_id: uuid.UUID) -> list[str]:
		return list(self._modules.keys())

	def _cmd_help(self, client_id: uuid.UUID) -> dict[str, dict[str, str|None]]:
		ret:dict[str, dict[str, str|None]] = {}
		for m in self._modules:
			ret[m] = self._modules[m].list_all()
		return ret

	def registerWebsocket(self, ws: "Websocket") -> bool:
		return True

async def run() -> None:
	ws = Websocket()
	await ws.run()

if __name__ == '__main__':
	#logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	asyncio.run(run())