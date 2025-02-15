#!/usr/bin/python

import typing
import numpy
import pandas
import re
import logging
import traceback

logger = logging.getLogger(__name__)

homeVenueCodes = ["ALK", "AMS"]
categoryCode = ["HPF", "DPF", "HPE", "DPE", "HPD", "DPD", "HPC", "DPC", "HPB", "DPB", "HPA", "DPA", "HC1", "DC1", "HC2", "DC2", "HB1", "DB1", "HB2", "DB2", "HA1", "DA1", "HA2", "DA2", "HN1", "DN1", "HN2", "DN2", "HN3", "DN3", "HN4", "DN4", "HSA", "DSA", "HSB", "DSB", "H40", "D40", "H45", "D45", "H50", "D50", "H55", "D55", "H60", "D60", "H65", "D65", "H70", "D70", "H75", "D75", "H80", "D80"]
disciplineCode = ["SpeedSkating.LongTrack", "SpeedSkating.ShortTrack", "SpeedSkating.Inline", "SpeedSkating.Marathon"]

class BaseDataStructure:
	def __init__(self, file: str, layout: dict[str, str], compression: int = 0):
		self._file = file
		self._layout = layout
		self._compression = compression
		self._table = None
		try:
			self._table = self._loadDatabase()
		except FileNotFoundError:
			self._table = self._createDatabase()
		finally:
			self._applyTypes()

	def _loadDatabase(self):
		table = pandas.read_hdf(self._file, 'df')
		return table

	def _createDatabase(self):
		table = pandas.DataFrame(columns=self._layout.keys())
		return table

	def __str__(self):
		return str(self._table)

	def dtypes(self):
		return self._table.dtypes

	def __getitem__(self, key):
		return self._table[key]

	def columnHasValue(self, column: str|int, value) -> bool:
		if isinstance(column, str):
			return (value in self._table[column].values)
		else:
			return (value in self._table.iloc[:, [column]].values)

	def _selectByColumnValue(self, select_column: str|int, value) -> pandas.DataFrame:
		select = None
		if isinstance(select_column, str):
			select = self._table[select_column]
		else:
			select = self._table.iloc[:,[select_column]].iloc[:,0]

		if isinstance(value, list):
			return self._table.loc[select.isin(value)]
		else:
			return self._table.loc[select.values==value]

	def selectColumnByColumnValue(self, result_column: str|int, select_column: str|int, value) -> list:
		select_table = self._selectByColumnValue (select_column, value)

		if isinstance(result_column, str):
			return select_table.loc[:, result_column].to_list()
		else:
			return z.iloc[:,[result_column]].iloc[:,0].to_list()

	def append(self, entry) -> bool:
		try:
			new_entry = self._recode(entry)
			self._table.loc[len(self._table)] = new_entry
			return True
		except ValueError:
			logger.info ("table: " + str(self._table))
			logger.info ("dtypes: " + str(self._table.dtypes))
			logger.warning ("Error can not insert \"" + str(new_entry) + "\": " + traceback.format_exc())
			return False
		except NotImplementedError:
			logger.warning ("Error can not insert \"" + str(new_entry) + "\": " + traceback.format_exc())
			return False

	def get(self) -> pandas.DataFrame:
		return self._table

	def _applyTypes (self):
		self._table = self._table.astype(self._layout, False)

	def save(self):
		self._applyTypes()
		self._table.to_hdf(self._file, key='df', mode='w', complevel=self._compression, complib='zlib', append=False, index=False)

	def _recode(self, items: list) -> list:
		ret = list()
		keys = list(self._layout.keys())
		for n,i in enumerate(list(items)):
		#for i in items:
			if len(self._layout[keys[n]]) >= 2:
				if self._layout[keys[n]][1] == 'S':
					if isinstance(i, str):
						ret.append(i.encode())
					elif i is None:
						ret.append(b'')
					else:
						ret.append(i)
				else:
					ret.append(i)
			else:
				ret.append(i)
		return ret

class HomeVenues(BaseDataStructure):
	def __init__(self, file: str):
		layout = {
			"code": "|S3",
			"countryCode": "|S3",
			"name": "|S255",
			"city": "|S255",
			"line1": "|S255",
			"line2": "|S255",
			"postalCode": "|S16",
			"stateOrProvince": "|S255"
		}
		super().__init__(file, layout, 9)

	def _selector(self, code: str) -> pandas.Series:
		return (self._table['code']==code.encode())

	def _updateHelper(self, selector, names: list[str], address):
		for name in names:
			if address[name] is not None:
				if self._table.loc[selector, name][0] is None:
					self._table.loc[selector, name] = address[name].encode()

	def update(self, address: dict, code: str, name: str):
		print("HomeVenues.update()")
		print("  address: " + str(address))
		print("  code: " + str(code))
		print("  name: " + str(name))
		if self.columnHasValue('code', code.encode()):
			selector = self._selector(code)
			self._updateHelper(selector, ['line1', 'line2', 'stateOrProvince', 'postalCode', 'city', 'countryCode'], address)
		else:
			self.append([code, address['countryCode'], name, address['city'], address['line1'], address['line2'], address['postalCode'], address['stateOrProvince']])
		return None

	def getVenue (self, code: str|None) -> dict:
		if code is None:
			return {
				"code": None,
				"countryCode": None,
				"name": None,
				"city": None,
				"line1": None,
				"line2": None,
				"postalCode": None,
				"stateOrProvince": None
		   }
		selector = self._selector(code)
		select = self._table.loc[selector]
		if (len(select)) == 0:
			return {
				"code": None,
				"countryCode": None,
				"name": None,
				"city": None,
				"line1": None,
				"line2": None,
				"postalCode": None,
				"stateOrProvince": None
		   }
		else:
			return select.iloc[0,:].to_dict()

class ProcessedCompetitions(BaseDataStructure):
	def __init__(self, file: str):
		layout = {
			"comp_id": "|S16",
			"email_id": "|S16"
		}
		super().__init__(file, layout, 9)

class Emails(BaseDataStructure):
	def __init__(self, file: str):
		layout = {
			"email_id": "|S16",
			"comp_id": "|S16",
			"email": "|S4096",
			"send": "?",
			"to": "|S1024"
		}
		super().__init__(file, layout, 9)

class EmailsSkaters(BaseDataStructure):
	def __init__(self, file: str):
		layout = {
			"email_id": "|S16",
			"skater_id": "|S16"
		}
		super().__init__(file, layout, 9)

class Skaters(BaseDataStructure):
	def __init__(self, file: str):
		layout = {
			"skater_id": "|S16",
			"first_name": "|S255",
			"last_name": "|S255",
			"email": "|S255",
			"phone": "|S255",
			"homeVenue": "i1",
			"clubCode": "i2",
			"category": "i1",
			"discipline": "i1"
		}
		super().__init__(file, layout, 9)

	def filter(self, venue: str|None, homeVenueFilter: str|list|None = None, categoryFilter: str|list|None = None, clubCodeFilter: str|list|None = None, disciplineCodeFilter: str|None = None, invitees: list|None = None) -> list:
		print("Skaters.filter()")
		print("  venue: " + str(venue))
		print("  homeVenueFilter: " + str(homeVenueFilter))
		print("  categoryFilter: " + str(categoryFilter))
		print("  clubCodeFilter: " + str(clubCodeFilter))
		print("  disciplineCodeFilter: " + str(disciplineCodeFilter))
		print("  invitees: " + str(invitees))
		return []
