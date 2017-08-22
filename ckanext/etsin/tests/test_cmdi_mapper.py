from ckanext.etsin.mappers.cmdi import cmdi_mapper
import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
import helpers


class TestCmdiMapper(TestCase):
    source = {}
    source['xml'] = helpers._get_file_as_string(
        'kielipankki_cmdi/cmdi_record_example.xml')
    data_dict = {'package_dict': {}}
    metax_dict = cmdi_mapper(source, data_dict)['metax_dict']

        # TODO: validate fields (or at least check existence)
        # Right now we're basically just checking that it does
        # not throw an error with the input

    def testTelephoneNumberCuratorPerson(self):
        assert any(curator['phone'] == '+358 123 456 789' for curator in self.metax_dict['research_dataset']['curator'])

    def testTelephoneNumberCuratorPersonMissing(self):
        assert {
            'email': 'kaisa.hakkinen@utu.fi',
            'isPartOf': {'email': 'registry@utu.fi',
                'name': u'University of Turku',
                'phone': ''},
            'name': u'Kaisa H\xe4kkinen',
            'phone': ''} in self.metax_dict['research_dataset']['curator']

    def testTelephoneNumberCuratorOrganization(self):
        assert any(curator['phone'] == '+358 295 333 200' for curator in self.metax_dict['research_dataset']['curator'])

    def testTelephoneNumberCuratorOrganizationMissing(self):
        assert {
            'email': 'registry@utu.fi',
            'name': u'University of Turku',
            'phone': ''} in self.metax_dict['research_dataset']['curator']

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
