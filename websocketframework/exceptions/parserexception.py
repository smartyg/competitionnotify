#!/bin/python

import typeguard
import logging

logger = logging.getLogger(__name__)

@typeguard.typechecked
class ParserException(Exception):
	def __init__(self, message: str, code: int):
		super().__init__()
		self.code = code
		self.message = message
