class LoadableProvider:
	_data
	_loaded: bool = False
	_url: str
	_cls: "dataclass"

	def __init__(self, url: str, c: "dataclass"):
		self._url = url
		self._cls = c

	async def load(self) -> None:
		self._loaded = False
		logger.debug ("Download the new data file")
		async with aiohttp.ClientSession() as session:
			async with session.get(self._url) as response:
				logger.debug ("New data file downloaded")
				json = json.loads(await response.text())
				self._data = class_factory(json, self._cls)
				self._loaded = True
				return None

	def isLoaded(self) -> bool:
		return self._loaded

	def getData(self):
		return self._data