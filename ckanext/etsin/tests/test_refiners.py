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
        kielipankki_refiner(metax_dict)

if __name__ == '__main__':
    unittest.main()
