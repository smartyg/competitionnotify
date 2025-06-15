#!/bin/python

import abc
import logging

logger = logging.getLogger(__name__)

class ResultProviderInterface(metaclass=abc.ABCMeta):
	@classmethod
	def __subclasshook__(cls, subclass):
		return (hasattr(subclass, 'getName') and
				callable(subclass.getName) or
				NotImplemented)

	@abc.abstractmethod
	def getName(self) -> str:
		"""Load in the data set"""
		raise NotImplementedError
