#!/bin/python

import collections.abc
import typing
import typeguard
import asyncio
import json
import logging
import websockets.server
import websockets.asyncio.server
import ssl
import attrs
import uuid
import traceback

import websocketframework.types as wst
import websocketframework.exceptions.parserexception as pe
import websocketframework.exceptions.unknowncommand as uc
import websocketframework.exceptions.unknownmodule as um
import websocketframework.exceptions.wrongdatatype as wdt
import websocketframework.websocketinterface as wsi
import websocketframework.dataclasses.registration as r
import websocketframework.dataclasses.command as c
import websocketframework.dataclasses.registrationcommand as rc
import websocketframework.dataclasses.registrationcommandargument as rca

logger = logging.getLogger(__name__)

@typeguard.typechecked
@attrs.define(frozen=False, kw_only=True, slots=False)
class Websocket(wsi.WebsocketInterface):
	_host: str = attrs.field(default="0.0.0.0", validator=attrs.validators.instance_of(str))
	_port: int = attrs.field(default=6789, validator=attrs.validators.instance_of(int))
	_ssl_cert: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_ssl_key: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(str)))
	_modules: dict[str, r.Registration] = attrs.field(default=dict(), init=False, validator=attrs.validators.deep_mapping(
            key_validator=attrs.validators.instance_of(str),
            value_validator=attrs.validators.instance_of(r.Registration),
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
	def registerModule(self, module: wsi.WebsocketInterface) -> bool:
		typeguard.check_type(module, wsi.WebsocketInterface)
		if isinstance(module, wsi.WebsocketInterface):
			name = module.getName()

			if name in self._modules.keys():
				return False
			else:
				self._modules[name] = r.Registration(instance=module)
				return module.registerWebsocket(self)
		return False

	@typeguard.typechecked
	def unregisterModule(self, module: wsi.WebsocketInterface) -> None:
		typeguard.check_type(module, wsi.WebsocketInterface)
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
				response: c.Command
				try:
					data = json.loads(message)
					if not isinstance(data, dict):
						raise wdt.WrongDataType("Data is not correctly formatted.")
					cmd = c.Command(**data)

					if cmd.getModule() not in self._modules:
						raise um.UnknownModule("There is no such module '" + str(cmd.getModule()) + "'.")

					m: r.Registration|None = self._modules.get(cmd.getModule(), None)
					if not isinstance(m, r.Registration):
						raise um.UnknownModule("There is no such module '" + str(cmd.getModule()) + "'.")

					if not m.hasCommand(cmd.getCommand()):
						raise uc.UnknownCommand("There is no such command '" + str(cmd.getCommand()) + "' in module '" + str(cmd.getModule()) + "'.")

					typeguard.check_type(cmd.getData(), dict[str, typing.Any])
					assert isinstance(cmd.getData(), dict), "Wrong data type for command."
					ret_data: wst.DataType = m.call(client_id, cmd.getCommand(), cmd.getData())
					response = cmd.response(200, ret_data)

				except json.JSONDecodeError as e:
					print("JSONDecodeError: " + str(e.msg))
					print(str(e.__traceback__))
					response = c.Command(response=400,
											module='',
											command='',
											data=e.msg)
					print(str(response))
				except pe.ParserException as e:
					print("ParserException: " + str(e.message))
					print(str(e.__traceback__))
					response = c.Command(response=e.code,
											module='',
											command='',
											data=e.message)
				except BaseException as e:
					msg = str(e)
					print("BaseException: " + str(msg))
					print(str(e.__traceback__))
					traceback.print_tb(e.__traceback__)
					response = c.Command(response=404,
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

	def getCommands(self) -> wst.CommandList:
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