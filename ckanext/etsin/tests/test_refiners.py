from ckanext.etsin.refiners.kielipankki import kielipankki_refiner
import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
import helpers


class TestKielipankkiRefiner(TestCase):
    def testRefine(self):
        xml = helpers._get_file_as_lxml('kielipankki_cmdi/cmdi_record_example.xml')
        metax_dict = {}
        metax_dict.update({
            'context': {
                'xml': xml
            }
        })
        refined_dict = kielipankki_refiner(metax_dict)

        # Check that refined fields exist
        ok_('remoteResources' in refined_dict)
        ok_('accessURL' in refined_dict['remoteResources'])
        ok_('downloadURL' in refined_dict['remoteResources'])

        # Check that refined fields are correct
        eq_(refined_dict['remoteResources'], {
            "accessURL": {
                "identifier": "todo"    # TODO: access_request_URL or access_application_URL?
            },
            "downloadURL": {
                "identifier": ""
            }
        })

if __name__ == '__main__':
    unittest.main()
