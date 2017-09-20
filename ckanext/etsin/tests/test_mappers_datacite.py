"""Tests for mappers/datacite.py."""

from nose.tools import eq_
from unittest import TestCase

from ckanext.etsin.mappers.datacite import datacite_mapper
from ckanext.harvest.model import HarvestObject

from .helpers import _get_file_as_lxml


class TestMappersDataCite(TestCase):

    @classmethod
    def setup_class(cls):
        cls.metax_dict = datacite_mapper(
            _get_file_as_lxml('datacite/datacite1.xml'))

    def testPreferredIdentifier(self):
        assert self.metax_dict['research_dataset']['preferred_identifier'] == 'http://dx.doi.org/10.18150/9887707'
