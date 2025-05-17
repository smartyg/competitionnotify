class ResultProviderInterface(metaclass=abc.ABCMeta):
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