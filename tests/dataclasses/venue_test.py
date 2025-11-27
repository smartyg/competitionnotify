import competitionnotify.classes.venue as venue
import competitionnotify.classes.discipline as discipline

import json
import unittest
import pytest

class TestAdressClass(unittest.TestCase):
	def test_convertor1(self):
		json_string = '{"line1":"Hoogspanningsweg 6","line2":null,"stateOrProvince":"Drenthe","postalCode":"9408 CZ","city":"Assen","countryCode":"NED"}'
		json_data = json.loads(json_string)
		test = venue.AddressClass_converter(data=json_data)
		self.assertIsInstance(test, venue.AddressClass)
		self.assertEqual(test._line1, "Hoogspanningsweg 6")
		self.assertIsNone(test._line2)
		self.assertEqual(test._stateOrProvince, "Drenthe")
		self.assertEqual(test._postalCode, "9408 CZ")
		self.assertEqual(test._city, "Assen")
		self.assertEqual(test._countryCode, "NED")

	def test_convertor2(self):
		json_string = '{"line1":"Hoogspanningsweg 6","line2":null,"stateOrProvince":"Drenthe","postalCode":"9408 CZ","city":"Assen","countryCode":"NED"}'
		json_data = json.loads(json_string)
		cls = venue.AddressClass_converter(data=json_data)
		self.assertIsInstance(cls, venue.AddressClass)

		test = venue.AddressClass_converter(data=cls)
		self.assertIsInstance(test, venue.AddressClass)
		self.assertEqual(test, cls)

		self.assertEqual(test._line1, "Hoogspanningsweg 6")
		self.assertIsNone(test._line2)
		self.assertEqual(test._stateOrProvince, "Drenthe")
		self.assertEqual(test._postalCode, "9408 CZ")
		self.assertEqual(test._city, "Assen")
		self.assertEqual(test._countryCode, "NED")

	def test_hash(self):
		json_string = '{"line1":"Hoogspanningsweg 6","line2":null,"stateOrProvince":"Drenthe","postalCode":"9408 CZ","city":"Assen","countryCode":"NED"}'
		json_data = json.loads(json_string)
		test = venue.AddressClass_converter(data=json_data)
		self.assertIsInstance(test, venue.AddressClass)
		self.assertIsInstance(hash(test), int)

class TestTrackClass(unittest.TestCase):
	def test_construct1(self):
		test = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.LongTrack")
		self.assertIsInstance(test, venue.TrackClass)
		self.assertIsInstance(test.getDiscipline(), discipline.DisciplineClass)
		self.assertEqual(test.getDiscipline().asString(), "SpeedSkating.LongTrack")
		self.assertEqual(test.getLength(), 400.0)

	def test_convertor1(self):
		json_string = '{"venueCode":"BID","venueDiscipline":"SpeedSkating.Marathon","length":400.000}'
		json_data = json.loads(json_string)
		test = venue.TrackClass_converter(data=json_data)
		self.assertIsInstance(test, venue.TrackClass)
		self.assertIsInstance(test.getDiscipline(), discipline.DisciplineClass)
		self.assertEqual(test.getDiscipline().asString(), "SpeedSkating.Marathon")
		self.assertEqual(test.getLength(), 400.0)

	def test_convertor2(self):
		with pytest.raises(ValueError) as e:
			test = venue.TrackClass_converter(data=None)

	def test_convertor3(self):
		cls = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.LongTrack")
		test = venue.TrackClass_converter(data=cls)
		self.assertIsInstance(test, venue.TrackClass)
		self.assertEqual(test, cls)

	def test_convertor_list1(self):
		json_string = '[{"venueCode":"BID","venueDiscipline":"SpeedSkating.Marathon","length":400.000}]'
		json_data = json.loads(json_string)
		test = venue.TrackClassTuple_converter(data=json_data)
		self.assertIsInstance(test, tuple)
		self.assertEqual(len(test), 1)

		item = test[0]
		self.assertIsInstance(item, venue.TrackClass)
		self.assertIsInstance(item.getDiscipline(), discipline.DisciplineClass)
		self.assertEqual(item.getDiscipline().asString(), "SpeedSkating.Marathon")
		self.assertEqual(item.getLength(), 400.0)

	def test_convertor_list2(self):
		cls = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.LongTrack")
		test = venue.TrackClassTuple_converter(data=tuple([cls]))
		self.assertIsInstance(test, tuple)
		self.assertEqual(len(test), 1)

		item = test[0]
		self.assertIsInstance(item, venue.TrackClass)
		self.assertEqual(item, cls)

	def test_hash(self):
		test = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.LongTrack")
		self.assertIsInstance(test, venue.TrackClass)
		self.assertIsInstance(hash(test), int)

class TestVenueClass(unittest.TestCase):
	def test_construct1(self):
		track = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.Marathon")
		address = venue.AddressClass()
		test = venue.VenueClass(address=address, code="AMS", continentCode="EUR", name="Stichting IJscomplex Jaap Edenbaan", discipline="SpeedSkating.Marathon", tracks=tuple([track]))

		self.assertIsInstance(test, venue.VenueClass)
		self.assertEqual(test.getCode(), "AMS")
		self.assertTrue(test.hasDiscipline(discipline.DisciplineClass(discipline=2)))
		self.assertTrue(test.hasTrack(track))
		self.assertEqual(test.getAddress(), address)

	def test_AddDiscipline(self):
		track = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.Marathon")
		address = venue.AddressClass()
		test1 = venue.VenueClass(address=address, code="AMS", continentCode="EUR", name="Stichting IJscomplex Jaap Edenbaan", discipline="SpeedSkating.Marathon", tracks=tuple([track]))

		self.assertIsInstance(test1, venue.VenueClass)

		test2 = test1.AddDiscipline(discipline.DisciplineClass(discipline=1))

		self.assertEqual(test2.numOfDisciplines(), 2)
		self.assertTrue(test2.hasDiscipline(discipline.DisciplineClass(discipline=1)))
		self.assertTrue(test2.hasDiscipline(discipline.DisciplineClass(discipline=2)))

	def test_AddTrack(self):
		track1 = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.Marathon")
		address = venue.AddressClass()
		test1 = venue.VenueClass(address=address, code="AMS", continentCode="EUR", name="Stichting IJscomplex Jaap Edenbaan", discipline="SpeedSkating.Marathon", tracks=tuple([track1]))

		self.assertIsInstance(test1, venue.VenueClass)

		track2 = venue.TrackClass(venueCode="AMS", length=100.0, venueDiscipline="SpeedSkating.Inline")

		self.assertIsInstance(track2, venue.TrackClass)

		test2 = test1.AddTrack(track2)

		self.assertEqual(test2.numOfTracks(), 2)
		self.assertTrue(test2.hasTrack(track1))
		self.assertTrue(test2.hasTrack(track2))

	def test_convertor1(self):
		json_string = '{"address":{"line1":null,"line2":null,"stateOrProvince":"Noord-Holland","postalCode":null,"city":"Amsterdam","countryCode":"NED"},"tracks":[{"venueCode":"AMS","venueDiscipline":"SpeedSkating.LongTrack","length":400.000}, {"venueCode":"AMS","venueDiscipline":"SpeedSkating.Marathon","length":400.000}],"name":"Stichting IJscomplex Jaap Edenbaan","code":"AMS","discipline":["SpeedSkating.LongTrack","SpeedSkating.Marathon","SpeedSkating.ShortTrack"],"continentCode":"EUR"}'
		json_data = json.loads(json_string)
		test = venue.VenueClass_converter(data=json_data)
		self.assertIsInstance(test, venue.VenueClass)
		self.assertEqual(test.getCode(), "AMS")
		self.assertEqual(test.getName(), "Stichting IJscomplex Jaap Edenbaan")

		self.assertEqual(test.numOfDisciplines(), 3)
		self.assertTrue(test.hasDiscipline(discipline.DisciplineClass(discipline=1)))
		self.assertTrue(test.hasDiscipline(discipline.DisciplineClass(discipline=2)))
		self.assertTrue(test.hasDiscipline(discipline.DisciplineClass(discipline=3)))

		self.assertEqual(test.numOfTracks(), 2)

	def test_convertor2(self):
		json_string = '{"address":{"line1":null,"line2":null,"stateOrProvince":"Friesland","postalCode":null,"city":"Heerenveen","countryCode":"NED"},"tracks":[{"venueCode":"HVN","venueDiscipline":"SpeedSkating.LongTrack","length":400.000}],"name":"Thialf","code":"HVN","discipline":"SpeedSkating.LongTrack","continentCode":"EUR"}'
		json_data = json.loads(json_string)
		test = venue.VenueClass_converter(data=json_data)
		self.assertIsInstance(test, venue.VenueClass)
		self.assertEqual(test.getCode(), "HVN")
		self.assertEqual(test.getName(), "Thialf")

		self.assertEqual(test.numOfDisciplines(), 1)
		self.assertTrue(test.hasDiscipline(discipline.DisciplineClass(discipline=1)))

		self.assertEqual(test.numOfTracks(), 1)

	def test_hash(self):
		track = venue.TrackClass(venueCode="AMS", length=400.0, venueDiscipline="SpeedSkating.Marathon")
		address = venue.AddressClass()
		test = venue.VenueClass(address=address, code="AMS", continentCode="EUR", name="Stichting IJscomplex Jaap Edenbaan", discipline="SpeedSkating.Marathon", tracks=tuple([track]))

		self.assertIsInstance(test, venue.VenueClass)
		self.assertIsInstance(hash(test), int)
