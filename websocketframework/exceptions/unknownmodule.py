#!/bin/python

import typeguard
import logging
import websocketframework.exceptions.parserexception as parserexception

logger = logging.getLogger(__name__)

@typeguard.typechecked
class UnknownModule(parserexception.ParserException):
	def __init__(self, message):
		super().__init__(message, 404)
