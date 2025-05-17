#!/bin/python

from typing import Any
import attrs
import asyncio
import logging
import types

logger = logging.getLogger(__name__)

@attrs.define(frozen=True, kw_only=True, slots=False)
class CoroutineClass:
	_coroutine: types.CoroutineType = attrs.field(validator=attrs.validators.instance_of(types.CoroutineType))
	_name: str = attrs.field(validator=attrs.validators.instance_of(str))

	def createTask(self) -> asyncio.Task[Any]:
		task = asyncio.create_task(self._coroutine)
		task.set_name(self._name)
		return task

	def getCoroutine(self) -> types.CoroutineType:
		return self._coroutine

#TODO: implement this with the use of asyncio.TaskGroup
class TaskManager:
	tasks: set[asyncio.Task[Any]] = set()

	def __init__(self) -> None:
		return

	async def cancelProcesses(self) -> bool:
		for task in self.tasks:
			logger.info ("send cancel exception to task: " + task.get_name())
			task.cancel()
		# wait so all tasks can finish
		await asyncio.sleep (5)

		# check and wait for all reamaining tasks
		for task in self.tasks:
			logger.info ("wait for task to stop: " + task.get_name())
			loop = asyncio.get_running_loop()
			loop.run_until_complete(task)

		if len(self.tasks) == 0:
			return True
		else:
			return False

	async def startProcesses(self, cr: set[CoroutineClass]) -> bool:
		for c in cr:
			task = c.createTask()
			task.add_done_callback(self.tasks.discard)
			self.tasks.add(task)
		return True

	async def startProcess(self, cr: CoroutineClass) -> bool:
		task = cr.createTask()
		task.add_done_callback(self.tasks.discard)
		self.tasks.add(task)
		return True

	async def waitAllProcesses() -> None:
		pass

	def runningProcesses(self) -> int:
		return len(self.tasks)