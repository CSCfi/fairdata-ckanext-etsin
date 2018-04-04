"""Basic tests for checking that metax_api.py works"""
import ckanext.etsin.metax_api as api
import unittest
from unittest import TestCase

from mock import Mock, patch
from nose.tools import ok_, eq_


class TestMetaxAPI(TestCase):

    def testCreateDatasetSuccess(self):
        ''' Test that create_catalog_record returns identifier on successful get request '''
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.text = '{"identifier": "123"}'
            mock_post.return_value.json.return_value = {'identifier': '123'}
            id = api.create_catalog_record({})
            ok_(mock_post.called)
            ok_(mock_post.return_value.raise_for_status.called)
            eq_(id, '123')

    def testReplaceDatasetSuccess(self):
        ''' Test that update_catalog_record does a put request and checks for http errors '''
        with patch('requests.put') as mock_put:
            mock_put.return_value = Mock()
            api.update_catalog_record('123', {})
            ok_(mock_put.called)
            ok_(mock_put.return_value.raise_for_status.called)

    def testDeleteDatasetSuccess(self):
        ''' Test that delete_catalog_record does a delete request and checks for http errors '''
        with patch('requests.delete') as mock_delete:
            mock_delete.return_value = Mock()
            api.delete_catalog_record('123')
            ok_(mock_delete.called)
            ok_(mock_delete.return_value.raise_for_status.called)

    def testCheckDatasetExists(self):
        ''' Test that check_catalog_record_exists does a get request and checks for http errors '''
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock()
            mock_get.return_value.json.return_value = True
            result = api.check_catalog_record_exists('123')
            ok_(mock_get.called)
            ok_(mock_get.return_value.raise_for_status.called)
            eq_(result, True)


if __name__ == '__main__':
    unittest.main()
