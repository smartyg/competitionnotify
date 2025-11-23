#!/bin/python

import collections.abc
import abc
import typeguard
import logging
import uuid

import websocketframework.types as wst
import websocketframework.websocket as ws

logger = logging.getLogger(__name__)

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
	def getCommands(self) -> wst.CommandList:
		"""Load in the data set"""
		raise NotImplementedError

	@abc.abstractmethod
	def registerWebsocket(self, ws: "ws.Websocket") -> bool:
		"""Load in the data set"""
		raise NotImplementedError
