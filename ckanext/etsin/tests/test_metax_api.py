"""Basic tests for checking that metax_api.py works"""
import ckanext.etsin.metax_api as api
import unittest
from unittest import TestCase
from requests.exceptions import HTTPError

from mock import Mock, patch
from nose.tools import ok_, eq_


class TestMetaxAPI(TestCase):
    def testCreateDatasetSuccess(self):
        ''' Test that create_dataset returns identifier on successful get request '''
        with patch('requests.post') as mock_post:
            mock_post.return_value = Mock()
            mock_post.return_value.json.return_value = {'id': '123'}
            r = api.create_dataset({})
            ok_(mock_post.called)
            ok_(mock_post.return_value.raise_for_status.called)
            eq_(r, '123')

    def testReplaceDataset(self):
        ''' Test that replace_dataset does a put request and checks for http errors '''
        with patch('requests.put') as mock_put:
            mock_put.return_value = Mock()
            api.replace_dataset('123', {})
            ok_(mock_put.called)
            ok_(mock_put.return_value.raise_for_status.called)

    def testDeleteDataset(self):
        ''' Test that delete_dataset does a delete request and checks for http errors '''
        with patch('requests.delete') as mock_delete:
            mock_delete.return_value = Mock()
            api.delete_dataset('123')
            ok_(mock_delete.called)
            ok_(mock_delete.return_value.raise_for_status.called)


if __name__ == '__main__':
    unittest.main()

    # Temporary tests for some stuff
    # from helpers import _get_json_as_dict, _create_identifier_ending

    # print('Posting valid dict')
    # valid_dict = _get_json_as_dict('minimum_valid_edited.json')
    # valid_dict['identifier'] += _create_identifier_ending()
    # id = api.create_dataset(valid_dict)
    # print ('id: {}'.format(id))

    # print('Updating the dict')
    # valid_dict['versionNotes'] += 'edit'
    # api.replace_dataset(id, valid_dict)

    # print('Deleting the dict')
    # api.delete_dataset(id)
