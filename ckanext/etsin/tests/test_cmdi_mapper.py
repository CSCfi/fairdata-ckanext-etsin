from ckanext.etsin.mappers.cmdi import cmdi_mapper
import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
import helpers


class TestCmdiMapper(TestCase):
    def testMapping(self):
        context = {}
        context['xml'] = helpers._get_file_as_string(
            'kielipankki_cmdi/cmdi_record_example.xml')
        data_dict = {'package_dict': {}}

        metax_dict = cmdi_mapper(context, data_dict)['metax_dict']

        # TODO: validate fields (or at least check existence)
        # Right now we're basically just checking that it does
        # not throw an error with the input

if __name__ == '__main__':
    unittest.main()
