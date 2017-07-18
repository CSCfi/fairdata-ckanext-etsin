"""Basic tests for checking that metax_api.py works"""
import ckanext.etsin.metax_api as api
import json
import time
import unittest
from unittest import TestCase
from requests.exceptions import HTTPError

def _get_fixture(filename):
    import os
    return os.path.join(os.path.dirname(__file__), "..", "test_fixtures", filename)

def _get_json_as_dict(filename):
    with open(_get_fixture(filename)) as file:
        dict = json.loads(''.join(file.readlines()))
    return dict

''' Helper for making unique identifiers '''
def _create_identifier_ending():
    return str(int(time.time())) 

class TestMetaxCalls(TestCase):
    def testEmpty(self):
        ''' Test metax put with empty dict '''
        dict = {}
        with self.assertRaises(HTTPError):
            api.create_dataset(dict)

    def testInvalid(self):
        ''' Test metax put with invalid dict '''
        dict = {} # TODO 
        with self.assertRaises(HTTPError):
            api.create_dataset(dict)

    def testMinimumValid(self):
        ''' Test metax put with valid dict '''
        minimum_valid_dict = _get_json_as_dict('minimum_valid_edited.json')
        minimum_valid_dict['identifier'] += str(int(time.time()))
        try:
            api.create_dataset(minimum_valid_dict)
        except:
            self.fail("create_dataset failed with minimum valid data")

    def testAllFieldsValid(self):
        ''' Test metax put with valid dict with all fields '''
        all_fields_valid_dict = _get_json_as_dict('all_fields_valid_edited.json')
        all_fields_valid_dict['identifier'] += str(int(time.time()))
        try:
            api.create_dataset(all_fields_valid_dict)
        except:
            self.fail("create_dataset failed with valid data containing all fields")

if __name__ == '__main__':
    unittest.main()
