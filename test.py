#!/bin/python

import typing
import typeguard
import aiohttp
import asyncio
import attrs
import json
import logging
import traceback
import uuid
import datetime

import websocketframework.websocket as ws
#import websocketframework.websocketinterface as wsi


#T = typing.TypeVar('T')

# @typeguard.typechecked
# @attrs.define(frozen=True, kw_only=True, slots=False)
# class TestClass1:
# 	_url: str = attrs.field(validator=attrs.validators.instance_of(str))
#
# 	def getUrl(self) -> str:
# 		return self._url
#
# @typeguard.typechecked
# class TestClass2:
# 	text: str = "default"
#
# 	def getUrl(self) -> str:
# 		return self.text
#
# @typeguard.typechecked
# def testAttrsClass(cls: typing.Any) -> bool:
# 	if isinstance(cls, type):
# 		return attrs.has(cls)
# 	return attrs.has(cls.__class__)
#
# if __name__ == '__main__':
# 	t1 = TestClass1(url="hoi")
# 	t2 = TestClass2()
# 	#isinstance(t, attrs.AttrsInstance)
# 	print(testAttrsClass(t1))
# 	print(testAttrsClass(t2))
#
# 	print(testAttrsClass(TestClass1))
#
# 	a=1
# 	print(testAttrsClass(a))
#
#


# @typeguard.typechecked
# class TestClass_1(ws.WebsocketInterface):
# 	_url: str = attrs.field(validator=attrs.validators.instance_of(str))
#
# 	# Interfaces for WebsocketInterface
# 	def getName(self) -> str:
# 		return "test"
#
# 	def getCommands(self) -> ws.CommandList:
# 		return (
# 			("count", self._cmd_count),
# 			)
#
# 	def _cmd_count(self, client_id: uuid.UUID) -> int:
# 		return 1
#
# 	def registerWebsocket(self, ws: ws.Websocket) -> bool:
# 		return True
#
# if __name__ == '__main__':
# 	t1 = TestClass_1()
# 	a = typeguard.check_type(t1, ws.WebsocketInterface)
#
# 	cls = a.__class__
# 	sub_cls = cls.__subclasses__()
# 	print(a)
# 	print(type(a))
# 	print(cls)
# 	print(sub_cls)

@typeguard.typechecked
class Test[T]:
	_type: type[T]
	_value: T

	def __init__(self, t: type):
		self._type=t
		#print(str(t))
		#typeguard.check_type(self._type, type)

	def hoi(self):
		return str("Hoi")

	def doei(self):
		d = "doei"
		print(f'{self.hoi()} {d}')

	def test(self, v: T):
		return isinstance(v, self._type)

	def set(self, v: T) -> bool:
		typeguard.check_type(v, self._type)
		self._value = v
		return True

	def get(self) -> T:
		return self._value

#c: str = "hoi"
t = str
#typeguard.check_type(t, type[str])
#typeguard.check_type(type(c), type[t])
#print(type(t))
a: Test[t] = Test(t)
a.doei()
#print(a.test(1))
a.set("Hoi")
print(a.get())