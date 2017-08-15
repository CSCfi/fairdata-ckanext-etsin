"""Tests for mappers/iso_19139.py."""


from ckanext.etsin.mappers.iso_19139 import iso_19139_mapper
from nose.tools import eq_
from unittest import TestCase


class TestMappersISO19139(TestCase):


    def testObligatoryFieldsMap(self):
        dict = iso_19139_mapper(self, {}, _testdict())

        eq_(dict['preferred_identifier'], 'M28mitl:')
        eq_(dict['title'], [{'default': 'Testiaineisto'}])


    def testObligatoryFieldsMissing(self):
        dict = iso_19139_mapper(self, {}, {})

        eq_(dict['preferred_identifier'], '')
        eq_(dict['title'], [{'default': ''}])


def _testdict():
    return {'iso_values': {'guid': 'M28mitl:', 'title': 'Testiaineisto'}}
