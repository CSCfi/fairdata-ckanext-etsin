"""Tests for mappers/iso_19139.py."""


from ckanext.etsin.mappers.iso_19139 import iso_19139_mapper
from nose.tools import eq_
from unittest import TestCase


class TestMappersISO19139(TestCase):


    def testObligatoryFieldsMap(self):
        dict = iso_19139_mapper(self, {}, _testdict())

        eq_(dict['preferred_identifier'], 'M28mitl:')
        eq_(dict['title'], [{'default': 'Testiaineisto'}])
        assert {'name': 'tekija1'} in dict['creator']
        assert {'name': 'tekija2'} in dict['creator']
        assert {'name': 'omistaja'} not in dict['creator']
        assert {'name': 'jotainmuuta'} not in dict['creator']
        assert {'name': 'tekija1'} not in dict['curator']
        assert {'name': 'tekija2'} not in dict['curator']
        assert {'name': 'omistaja'} in dict['curator']
        assert {'name': 'jotainmuuta'} not in dict['curator']
        eq_(dict['language'], [{'identifier':'http://www.lexvo.org/id/iso639-3/fin'}])


    def testObligatoryFieldsMissing(self):
        dict = iso_19139_mapper(self, {}, {})

        eq_(dict['preferred_identifier'], '')
        eq_(dict['title'], [{'default': ''}])
        eq_(dict['creator'], [])
        eq_(dict['curator'], [])
        eq_(dict['language'], [{'identifier':'http://www.lexvo.org/id/iso639-3/und'}])


def _testdict():
    return {
        'iso_values': {
            'guid': 'M28mitl:', 
            'title': 'Testiaineisto',
            'responsible-organisation': [
                {
                    'organisation-name': 'omistaja',
                    'role': ['owner']
                    },
                {
                    'organisation-name': 'tekija1',
                    'role': ['author']
                    },
                {
                    'organisation-name': 'tekija2',
                    'role': ['author']
                    },
                {
                    'organisation-name': 'muu',
                    'role': ['jotainmuuta']
                    }, 
                ],
              'metadata-language': 'fin',
            }
        }
