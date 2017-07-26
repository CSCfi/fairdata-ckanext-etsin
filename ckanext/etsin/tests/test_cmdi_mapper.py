from ckanext.etsin.mappers.cmdi import cmdi_mapper
import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
import helpers


class TestCmdiMapper(TestCase):
    def testMapping(self):
        context = {}
        context['xml'] = helpers._get_file_as_string('cmdi_full_example.xml')
        print(context['xml'])
        data_dict = {'package_dict': {}}

        metax_dict = cmdi_mapper(context, data_dict)
        print('ok')


if __name__ == '__main__':
    unittest.main()
