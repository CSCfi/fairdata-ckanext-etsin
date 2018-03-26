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