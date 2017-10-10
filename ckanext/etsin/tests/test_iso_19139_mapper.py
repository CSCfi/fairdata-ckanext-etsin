"""Tests for mappers/iso_19139.py."""

from ckanext.etsin.mappers.iso_19139 import iso_19139_mapper
from nose.tools import eq_
from nose.tools import assert_not_equal as neq_
from unittest import TestCase
from iso19139_test_dicts import get_iso_values_dict_1


class TestMappersISO19139(TestCase):


    # TODO: Should this test be actually in refiner tests?
    # At this point we may not have set all the required fields

    def testMapper(self):
        dict = iso_19139_mapper({}, get_iso_values_dict_1())
        print(dict)
        eq_(dict['preferred_identifier'], 'M28mitl:')
        eq_(dict['title'], {'fi': 'Testiaineisto'})
        assert {'email': 'tekija1@testi.fi', 'name': 'tekija1'} in dict['creator']
        assert {'email': 'tekija2@testi.fi', 'name': 'tekija2'} in dict['creator']
        assert {'email': 'omistaja@testi.fi', 'name': 'omistaja'} not in dict['creator']
        assert {'email': 'jotainmuuta@testi.fi', 'name': 'jotainmuuta'} not in dict['creator']
        eq_({'email': 'omistaja@testi.fi', 'name': 'omistaja'}, dict['rights_holder'])
        assert {'email': 'tekija1@testi.fi', 'name': 'tekija1'} not in dict['curator']
        assert {'email': 'tekija2@testi.fi', 'name': 'tekija2'} not in dict['curator']
        assert {'email': 'kuratoija@testi.fi', 'name': 'kuratoija'} in dict['curator']
        eq_({'email': 'jakelija@testi.fi', 'name': 'jakelija'}, dict['publisher'])
        neq_({'email': 'julkaisija@testi.fi', 'name': 'julkaisija'}, dict['publisher'])
        eq_(dict['language'], [{'identifier': 'http://lexvo.org/id/iso639-3/fin'}])
        assert 'testiavainsana' in dict['keyword']
        eq_(
            'POLYGON((59.880178 21.193932,59.880178 23.154996,60.87458 23.154996,60.87458 21.193932,59.880178 21.193932))',
            dict['spatial'][0]['as_wkt'][0])
        eq_('2017-01-01', dict['issued'])
        eq_('joopajoo', dict['access_rights']['description'][0]['fi'])
        eq_('2000-01-01', dict['temporal'][0]['start_date'])
        eq_('2001-01-01', dict['temporal'][0]['end_date'])
        eq_('2017-06-06', dict['modified'])
        eq_(dict['provenance'][0], {'description': {'fi': 'provenance'}})
