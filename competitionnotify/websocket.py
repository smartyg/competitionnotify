#!/bin/python

import abc
import asyncio
import json
import logging
#import websockets
import websockets.server
from websockets.server import ServerConnection
import ssl
from pathlib import Path
from typing import Any
import attrs
import uuid
from baseclass import BaseClass

DataType = None|bool|int|str|list|dict

class ParserException(Exception):
	def __init__(self, message: str, code: int):
		super().__init__()
		self.code = code
		self.message = message

class UnknownCommand(ParserException):
	def __init__(self, message):
		super().__init__(message, 400)

class WrongDataType(ParserException):
	def __init__(self, message):
		super().__init__(message, 400)

class UnknownModule(ParserException):
	def __init__(self, message):
		super().__init__(message, 404)

class WebsocketInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, 'getName') and
				callable(subclass.getName) and
				hasattr(subclass, 'getCommands') and
				callable(subclass.getCommands) and
				hasattr(subclass, 'processCommand') and
				callable(subclass.processCommand) and
				hasattr(subclass, 'registerWebsocket') and
				callable(subclass.registerWebsocket) or
				NotImplemented)

	@abc.abstractmethod
	def getName(self) -> str:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def getCommands(self) -> list[str]:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def processCommand(self, client_id: uuid.UUID, command: str, data: DataType) -> DataType:
		"""Load in the data set"""
		raise NotImplementedError

	def registerWebsocket(self, ws: "Websocket") -> bool:
		"""Load in the data set"""
		raise NotImplementedError

@attrs.define(frozen=False, kw_only=True, slots=False)
class Websocket(WebsocketInterface):
	_host: str = attrs.field(default="0.0.0.0", validator=attrs.validators.instance_of(str))
	_port: int = attrs.field(default=6789, validator=attrs.validators.instance_of(int))
	_ssl_cert: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(Path)))
	_ssl_key: str|None = attrs.field(default=None, validator=attrs.validators.optional(attrs.validators.instance_of(Path)))

	_modules: list[WebsocketInterface] = attrs.field(default=list(), init=False)
	_connections: set[websockets.server.ServerConnection] = attrs.field(default=set(), init=False)
	_ssl_context: ssl.SSLContext|None = attrs.field(default=None, init=False)
	_server: websockets.server.WebSocketServer|None = attrs.field(default=None, init=False)

	@attrs.define(frozen=True, kw_only=True, slots=False)
	class Command(BaseClass):
		_response: int = attrs.field(default=-1, validator=attrs.validators.instance_of(int))
		_module: str = attrs.field(validator=attrs.validators.instance_of(str))
		_command: str = attrs.field(validator=attrs.validators.instance_of(str))
		_data: DataType = attrs.field() #TODO: check type is json parsable

		def getModule(self) -> str:
			return self._module

		def getCommand(self) -> str:
			return self._command

		def getData(self) -> DataType:
			return self._data

		def hasData(self) -> bool:
			return True if self._data is not None else False

		def response(self, response: int, data: DataType) -> "Command":
			return attrs.evolve(self, {'response': response, 'data': data})

	def __attrs_post_init__(self):
		if self._ssl_cert is not None and self._ssl_key is not None:
			self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
			self._ssl_context.load_cert_chain(self._ssl_cert, keyfile=self._ssl_key)
		self.registerModule(self)
		self._server = websockets.serve(self._connection, self._host, self._port, ssl=self._ssl_context)

	async def run(self):
		ws = await self._server
		await ws.serve_forever()

	def registerModule(self, module: WebsocketInterface) -> bool:
		if isinstance(module, WebsocketInterface):
			self._modules.append(module)
			return module.registerWebsocket(self)
		return False

	def unregisterModule(self, module: WebsocketInterface) -> None:
		try:
			for i, m in enumerate(self._modules):
				if m.getName() == module.getName():
					self._modules.pop(i)
					return
		finally:
			return

	async def _connection(self, client: ServerConnection) -> None:
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
					cmd = Websocket.Command(**data)
					ret_data: Bool|dict[str, Any] = False
					for m in self._modules:
						if m.getName() == cmd.getModule():
							if cmd.getCommand() in m.getCommands():
								ret_data = m.processCommand(client_id, cmd.getCommand(), cmd.getData())
								response = cmd.response(200, ret_data)
							else:
								raise UnknownModule("There is no such module '" + str(cmd.getModule()) + "'.")
				except json.JSONDecodeError as e:
					print("JSONDecodeError: " + str(e.msg))
					response = Websocket.Command(response=400,
											module='',
											command='',
											data=e.msg)
					print(str(response))
				except ParserException as e:
					print("ParserException: " + str(e.message))
					response = Websocket.Command(response=e.code,
											module='',
											command='',
											data=e.message)
				except BaseException as e:
					msg = str(e.__notes__)
					print("BaseException: " + msg)
					response = Websocket.Command(response=404,
											module='',
											command='',
											data=msg)
				finally:
					print(str(response))
					print(response.json())
					await client.send(response.json())
		finally:
			print("Close connection with client " + str(client_id))
			self._unregisterClient(client)

	def _registerClient(self, client: ServerConnection) -> None:
		self._connections.add(client)
		#return True

	def _unregisterClient(self, client: ServerConnection) -> None:
		self._connections.remove(client)

	def getName(self) -> str:
		return "main"

	def getCommands(self) -> list[str]:
		return ['connection_id', 'clients', 'ip', 'version', 'purge', 'modules' ]

	def processCommand(self, client_id: uuid.UUID, command: str, data: DataType) -> DataType:
		if command == 'connection_id':
			return str(client_id)
		elif command == 'clients':
			return [str(client.id) for client in self._connections]
		elif command == 'ip':
			for client in self._connections:
				if client.id == client_id:
					return client.remote_address[0]
		elif command == 'version':
			return "0.1"
		elif command == 'purge':
			if isinstance(data, bool):
				if data:
					return True
				else:
					return False
			else:
				raise TypeError
		elif command == 'modules':
			return [module.getName() for module in self._modules]
		else:
			raise ...

	def registerWebsocket(self, ws: "Websocket") -> bool:
		return True

async def run() -> None:
	ws = Websocket()
	await ws.run()

if __name__ == '__main__':
	#logging.basicConfig(filename='wedstrijdkalender.log', level=logging.DEBUG)
	#asyncio.run(runner())
	asyncio.run(run())