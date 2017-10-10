from ckanext.etsin.refine import refine
from ckanext.etsin.refiners.kielipankki import kielipankki_refiner
from ckanext.etsin.refiners.syke import syke_refiner
from iso19139_test_dicts import get_package_dict_1
from ckanext.etsin.exceptions import DatasetFieldsMissingError

import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
import helpers
from mock import Mock, patch


class TestRefine(TestCase):
    """ Tests for refine.py """

    def testRefineKielipankki(self):
        with patch('ckanext.etsin.refiners.kielipankki.kielipankki_refiner') as mock_refiner:
            context = {'harvest_source_name': 'kielipankki'}
            data_dict = {}
            refine(context, data_dict)
            ok_(mock_refiner.called)

    def testRefineSyke(self):
        with patch('ckanext.etsin.refiners.syke.syke_refiner') as mock_refiner:
            context = {'harvest_source_name': 'syke'}
            data_dict = {}
            refine(context, data_dict)
            ok_(mock_refiner.called)


class TestKielipankkiRefiner(TestCase):
    """ Tests for kielipankki.py """

    def testRefiner(self):
        xml = helpers._get_file_as_lxml(
            'kielipankki_cmdi/cmdi_record_example.xml')
        metax_dict = {}
        context = {'source_data': xml}
        refined_dict = kielipankki_refiner(context, metax_dict)
        # Check that refined fields exist
        ok_('other_identifier' in refined_dict)


class TestSykeRefiner(TestCase):
    """ Tests for syke.py """

    def testRefiner(self):
        test_dict = get_package_dict_1()
        context = {'guid': '{51C9D60D-6D41-44BD-9136-C4933510DB2D}'}
        refined_dict = syke_refiner(context, test_dict)

        if '@' not in refined_dict['creator'][1]['email']:
            self.fail("email address invalid: {0}".format(refined_dict['creator'][1]['email']))
        if '@' not in refined_dict['curator'][0]['email']:
            self.fail("email address invalid: {0}".format(refined_dict['curator'][1]['email']))
        if '@' not in refined_dict['rights_holder']['email']:
            self.fail("email address invalid: {0}".format(refined_dict['rights_holder']['email']))
        if '@' not in refined_dict['publisher']['email']:
            self.fail("email address invalid: {0}".format(refined_dict['publisher']['email']))
        if 'identifier' not in refined_dict['field_of_science'][0] or not refined_dict['field_of_science'][0]['identifier']:
            self.fail("Missing field of science information")
        if 'type' not in refined_dict['access_rights'] \
                or 'identifier' not in refined_dict['access_rights']['type'][0]:
            self.fail("Missing access type information")
        if 'license' not in refined_dict['access_rights'] \
                or 'identifier' not in refined_dict['access_rights']['license'][0]:
            self.fail("Missing license information")

        assert refined_dict['access_rights']['type'][0]['identifier'] == \
               'http://purl.org/att/es/reference_data/access_type/access_type_restricted_access'

        assert refined_dict['access_rights']['license'][0]['identifier'] == \
               'http://purl.org/att/es/reference_data/license/license_other'

    def testMissingFields(self):
        test_dict = get_package_dict_1()
        del test_dict['preferred_identifier']
        context = {}
        with self.assertRaises(DatasetFieldsMissingError):
            syke_refiner(context, test_dict)
