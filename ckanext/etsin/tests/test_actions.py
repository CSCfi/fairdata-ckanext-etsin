import ckanext.etsin.actions as actions
from ckanext.etsin.mappers.cmdi import cmdi_mapper
from ckan import model

import unittest
from unittest import TestCase
from nose.tools import ok_, eq_
from mock import Mock, patch
import helpers


class TestActions(TestCase):
    """ Tests for actions.py """

    def testPackageCreate(self):
        """ Test action package_create with real data.

        Note: we use cmdi_mapper, so this is not a true unit test.
        Note: this test is not finished yet, so it is commented out
        """
#        with patch('ckan.logic.action.create.package_create') as mock_create:
#            # Create the MetaX data dict
#            xml_string = helpers._get_file_as_string(
#                'kielipankki_cmdi/cmdi_record_example.xml')
#            context = {
#                'xml': xml_string,
#                'model': model,
#                'session': model.Session,
#                'user': "test"
#            }
#            data_dict = {'package_dict': {'id': 123}}
#            data_dict = cmdi_mapper(context, data_dict)
#
#            # TEMP: so that refiner does not get confused
#            data_dict['organization'] = 'kielipankki'
#
#            # Try to create the package
#            actions.package_create(context, data_dict)
#
#            # Check that package creation was attempted
#            ok_(mock_create.called)
#

if __name__ == '__main__':
    unittest.main()
