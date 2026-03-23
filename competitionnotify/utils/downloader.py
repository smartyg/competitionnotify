#!/bin/python

import typing
import typeguard
import attrs
import logging
import asyncio
import aiohttp
import json

import competitionnotify.classes.base as base
import competitionnotify.utils.utils as utils

logger = logging.getLogger(__name__)

U = typing.TypeVar('U', bound=attrs.AttrsInstance) # Declare type variable "U"

def _dataLoader(data: typing.Any, c: type[U]) -> U:
	ret = None
	if not isinstance(data, dict):
		name = base.getFirstFieldName(c)
		if name is not None:
			ret = utils.class_factory({name: data}, c)
	else:
		ret = utils.class_factory(data, c)
	if ret is None:
		raise ValueError(f'Failed to create and instance of type `{c.__name__!s}` with data: {data!s}.')
	return ret

@typeguard.typechecked
async def downloader(url: str, c: type[U]) -> U:
	async with aiohttp.ClientSession() as session:
		logger.debug (f'download file: {url} ...')
		async with session.get(url) as response:
			data = json.loads(await response.text())
			logger.debug (f'Download completed.')
			return _dataLoader(data, c)

@typeguard.typechecked
async def downloaderTuple(url: str, c: type[U]) -> tuple[U]:
	async with aiohttp.ClientSession() as session:
		logger.debug (f'download file: {url} ...')
		async with session.get(url) as response:
			data = json.loads(await response.text())
			logger.debug (f'Download completed.')

			if not isinstance(data, list):
				raise ValueError(f'Failed to create and instance of type `{c.__name__!s}` with data: {data!s}.')

			result: list[typing.Any] = []
			for element in data:
				result.append(_dataLoader(element, c))
			return tuple(result)