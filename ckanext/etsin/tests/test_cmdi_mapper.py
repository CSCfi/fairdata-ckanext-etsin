from ckanext.etsin.mappers.cmdi import cmdi_mapper
import unittest
from unittest import TestCase
from .helpers import _get_file_as_lxml

import logging
log = logging.getLogger(__name__)


class TestCmdiMapper(TestCase):

    @classmethod
    def setup_class(cls):
        cls.metax_dict = cmdi_mapper(_get_file_as_lxml(
            'kielipankki_cmdi/cmdi_record_example.xml'))

    # TODO: validate fields (or at least check existence)
    # Right now we're basically just checking that it does
    # not throw an error with the input

    # Test preferred identifier
    # Note that the identifier will be assigned by refiner, not mapper
    def testPreferredIdentifier(self):
        assert 'preferred_identifier' in self.metax_dict

    # Test language

    def testLanguage(self):
        import pprint
        pprint.pprint(self.metax_dict)
        assert {
            'identifier': 'http://lexvo.org/id/iso639-3/fin',
            'title': u'fi',
        } in self.metax_dict['language']

    # Test title

    def testTitle(self):
        print(self.metax_dict)
        assert self.metax_dict['title'].get('fi', '') == u'Mikael Agricolan teosten morfosyntaktinen tietokanta'
        assert self.metax_dict['title'].get('en', '') == u'The Morpho-Syntactic Database of Mikael Agricola\'s Works'

    # Test creators

    def testCreatorPerson(self):
        assert {
            '@type': 'Person',
            'email': 'teija@tekija.fi',
            'name': u'Teija Tekij\xe4',
            'phone': '+358501234567',
            'member_of': {
                '@type': 'Organization',
                'email': 'registry@utu.fi',
                'name': u'University of Turku',
                'phone': '',
            }
        } in self.metax_dict['creator']

    def testCreatorOrganization(self):
        assert {
            '@type': 'Organization',
            'email': 'etunim.sukunimi@kotus.fi',
            'name': u'Kotimaisten kielten keskus, Institute for the Languages of Finland',
            'phone': '+358 295 333 200',
        } in self.metax_dict['creator']

    # Test curators

    def testCuratorPerson1(self):
        assert {
            '@type': 'Person',
            'email': 'nobufumi.inaba@utu.fi',
            'member_of': {
                '@type': 'Organization',
                'email': 'registry@utu.fi',
                'name': u'University of Turku',
                'phone': ''
            },
            'name': u'Nobufumi Inaba',
            'phone': '+358 123 456 789',
        } in self.metax_dict['curator']

    def testCuratorPerson2(self):
        assert {
            '@type': 'Person',
            'email': 'kaisa.hakkinen@utu.fi',
            'member_of': {
                '@type': 'Organization',
                'email': 'registry@utu.fi',
                'name': u'University of Turku',
                'phone': ''
            },
            'name': u'Kaisa H\xe4kkinen',
            'phone': '',
        } in self.metax_dict['curator']

    def testCuratorOrganization1(self):
        assert {
            '@type': 'Organization',
            'email': 'etunim.sukunimi@kotus.fi',
            'name': u'Kotimaisten kielten keskus, Institute for the Languages of Finland',
            'phone': '+358 295 333 200',
        } in self.metax_dict['curator']

    def testCuratorOrganization2(self):
        assert {
            '@type': 'Organization',
            'email': 'registry@utu.fi',
            'name': u'University of Turku',
            'phone': '',
        } in self.metax_dict['curator']


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
