"""Tests for mappers/iso_19139.py."""

from ckanext.etsin.mappers.iso_19139 import iso_19139_mapper
from nose.tools import eq_
from nose.tools import assert_not_equal as neq_
from unittest import TestCase
from ckanext.harvest.model import HarvestObject


class TestMappersISO19139(TestCase):


    def testObligatoryFieldsMap(self):
        dict = iso_19139_mapper({}, _testdict())

        eq_(dict['preferred_identifier'], 'M28mitl:')
        eq_(dict['title'], [{'fi': 'Testiaineisto'}])
        import pprint
        pprint.pprint(dict)
        # raise
        assert {'email': 'testi@testi.fi', 'name': 'tekija1'} in dict['creator']
        assert {'email': 'testi@testi.fi', 'name': 'tekija2'} in dict['creator']
        assert {'email': 'testi@testi.fi', 'name': 'omistaja'} not in dict['creator']
        assert {'email': 'testi@testi.fi', 'name': 'jotainmuuta'} not in dict['creator']
        eq_({'email': 'testi@testi.fi', 'name': 'omistaja'}, dict['rights_holder'])
        assert {'email': 'testi@testi.fi', 'name': 'tekija1'} not in dict['curator']
        assert {'email': 'testi@testi.fi', 'name': 'tekija2'} not in dict['curator']
        assert {'email': 'testi@testi.fi', 'name': 'kuratoija'} in dict['curator']
        eq_({'email': 'testi@testi.fi', 'name': 'jakelija'}, dict['publisher'])
        neq_({'email': 'testi@testi.fi', 'name': 'julkaisija'}, dict['publisher'])
        eq_(dict['language'], [{'identifier':'http://lexvo.org/id/iso639-3/fin'}])
        assert 'testiavainsana' in dict['keyword']
        eq_('POLYGON((59.880178 21.193932,59.880178 23.154996,60.87458 23.154996,60.87458 21.193932,59.880178 21.193932))', dict['spatial'][0]['polygon'])


    def testObligatoryFieldsMissing(self):
        dict = iso_19139_mapper({}, {'iso_values': {}})

        eq_(dict['preferred_identifier'], '')
        eq_(dict['title'], [{'default': ''}])
        eq_(dict['creator'], [])
        eq_(dict['curator'], [])
        eq_(dict['language'], [{'identifier':'http://lexvo.org/id/iso639-3/und'}])


def _testdict():
    ho = HarvestObject()
    ho.guid = 'M28mitl:'
    return {
        'iso_values': {
            'title': 'Testiaineisto',
            'responsible-organisation': [
                {
                    'organisation-name': 'omistaja',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['owner']
                    },
                {
                    'organisation-name': 'tekija1',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['originator']
                    },
                {
                    'organisation-name': 'tekija2',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['originator']
                    },
                {
                    'organisation-name': 'kuratoija',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['pointOfContact']
                },
                {
                    'organisation-name': 'jakelija',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['distributor']
                },
                {
                    'organisation-name': 'julkaisija',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['publisher']
                },
                {
                    'organisation-name': 'jotainmuuta',
                    'contact-info': {'email': 'testi@testi.fi'},
                    'role': ['user']
                },
            ],
            'metadata-language': 'fin',
            'abstract': 'kuvailuteksti',
            'dataset-language': ['fin'],
            'tags': ['testiavainsana'],
            'bbox': [{'west': '21.193932', 'east': '23.154996', 'north': '60.87458', 'south': '59.880178'}]
        },
        'harvest_object': ho
    }