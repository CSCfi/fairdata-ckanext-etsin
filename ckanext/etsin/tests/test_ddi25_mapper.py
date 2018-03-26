"""Tests for mappers/ddi25.py."""

from unittest import TestCase

from ckanext.etsin.mappers.ddi25 import ddi25_mapper

from .helpers import _get_file_as_lxml


class TestMappersDDI25(TestCase):

    @classmethod
    def setup_class(cls):
        cls.metax_dict = ddi25_mapper(
            _get_file_as_lxml('ddi25/ddi25_1.xml'))

    def testPreferredIdentifier(self):
        assert self.metax_dict['preferred_identifier'] == 'urn:nbn:fi:fsd:T-FSD3092', self.metax_dict

    def testTitle(self):
        assert self.metax_dict['title'].get('fi', '').startswith(u'Tampere'), self.metax_dict['title'].get('fi', '')

    def testModified(self):
        assert self.metax_dict['modified'] == '2016-05-31'
