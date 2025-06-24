#!/bin/python

import typing
import typeguard
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

@typeguard.typechecked
class LoadableProvider:
	#_data
	_loaded: bool = False
	_url: str|None
	#_cls: "dataclass"
	#_func

	def __init__(self, url: str|None, func: typing.Callable[dict[str, typing.Any], None]):
		self._url = url
		self._func = func
		self._session = aiohttp.ClientSession()

	async def getSession(self):
		return self._session

	async def load(self) -> None:
		self._loaded = False
		if self._url is not None:
			logger.debug ("Download the new data file")
			session = await self.getSession()
			async with session:
				async with session.get(self._url) as response:
					logger.debug ("New data file downloaded")
					data = json.loads(await response.text())
					await self._func(json=data)
					#self._data = class_factory(json, self._cls)
					self._loaded = True
					return None
		else:
			await self._func(json=dict())
			self._loaded = True
			return None

	def isLoaded(self) -> bool:
		return self._loaded
