# coding=UTF8
"""Tests for mappers/ddi25.py."""
import pprint
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

    def testCreatorPerson(self):
        pprint.pprint(self.metax_dict['creator'])
        assert {
            '@type': 'Person',
            'name': u'Tutkija, Teijo',
            'member_of': {
                '@type': 'Organization',
                'name': {'en': u'University of Monty. School of Python',
                         'fi': u'Montyn yliopisto. Python-korkeakoulu'}
            }
        } in self.metax_dict['creator']

    def testCreatorOrganization(self):
        pprint.pprint(self.metax_dict['creator'])
        assert {
            '@type': 'Organization',
            'name': {'fi': u'Testattava organisaatioluoja', 'en': u'Test organisation author'},
        } in self.metax_dict['creator']

    def testModified(self):
        assert self.metax_dict['modified'] == '2016-05-31'

    def testDescription(self):
        assert self.metax_dict['description'][0].get('fi').startswith('Aineistossa kartoitetaan')

    def testKeywords(self):
        assert 'talouspolitiikka' in self.metax_dict['keywords']

    def testFieldOfScience(self):
        assert {'identifier': 'ta5'} in self.metax_dict['field_of_science']

    def testPublisher(self):
        pprint.pprint(self.metax_dict['publisher'])
        assert self.metax_dict['publisher']['name']['en']\
            == 'Finnish Social Science Data Archive'
        assert self.metax_dict['publisher']['homepage']['identifier']\
            == 'http://www.fsd.uta.fi/'

    def testTemporalCoverage(self):
        assert self.metax_dict['temporal'][0]['start_date'] == '2015-04-07'

    def testProvenance(self):
        assert self.metax_dict['provenance'][0]['temporal']['start_date'] == '2015-04-07'
        assert self.metax_dict['provenance'][0]['variable'][0]['pref_label']['en'] ==\
               'Students enrolled at the University of Tampere'

    def testProduction(self):
        assert self.metax_dict['provenance'][1]['temporal']['start_date'] == '2016-06-15' and\
            self.metax_dict['provenance'][1]['title']['en'] == 'Production'

    def testSpatialCoverage(self):
        assert self.metax_dict['spatial'][0]['geographic_name'] == 'Finland'
        assert self.metax_dict['spatial'][0]['place_uri']['identifier'] == 'p94426'