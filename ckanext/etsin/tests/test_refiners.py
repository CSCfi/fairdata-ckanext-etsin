from ckanext.etsin.refine import refine
from ckanext.etsin.refiners.kielipankki import kielipankki_refiner
from ckanext.etsin.refiners.syke import syke_refiner

import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
import helpers
from mock import Mock, patch


class TestRefine(TestCase):
    """ Tests for refine.py """

    def testRefineKielipankki(self):
        with patch('ckanext.etsin.refiners.kielipankki.kielipankki_refiner') as mock_refiner:
            data_dict = {
                'organization': 'kielipankki'
            }
            refine(data_dict)
            ok_(mock_refiner.called)

    def testRefineSyke(self):
        with patch('ckanext.etsin.refiners.syke.syke_refiner') as mock_refiner:
            data_dict = {
                'organization': 'syke'
            }
            refine(data_dict)
            ok_(mock_refiner.called)


class TestKielipankkiRefiner(TestCase):
    """ Tests for kielipankki.py """

    def testRefiner(self):
        xml = helpers._get_file_as_lxml(
            'kielipankki_cmdi/cmdi_record_example.xml')
        metax_dict = {}
        metax_dict.update({
            'context': {
                'xml': xml
            }
        })
        refined_dict = kielipankki_refiner(metax_dict)

        # Check that refined fields exist
        ok_('remoteResources' in refined_dict)
        ok_(len(refined_dict['remoteResources']) > 0)
        ok_('accessURL' in refined_dict['remoteResources'][0])
        ok_('downloadURL' in refined_dict['remoteResources'][0])
        ok_('otherIdentifier' in refined_dict)

        # Check that refined fields are correct
        eq_(refined_dict['remoteResources'][0], {
            "accessURL": {
                "identifier": "todo"
            },
            "downloadURL": {
                "identifier": ""
            }
        })


class TestSykeRefiner(TestCase):
    """ Tests for syke.py """
    pass


if __name__ == '__main__':
    unittest.main()
