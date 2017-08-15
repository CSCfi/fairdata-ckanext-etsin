import json
import sys
from pprint import pprint
import requests
from requests import HTTPError

import logging
log = logging.getLogger(__name__)

# # Uncomment to setup http logging for debug purposes (note: will log requests
# # made from other files as well)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

# TODO: All these functions must log all the API calls we make and all the responses.


def create_dataset(dataset_dict):
    """ Create a dataset in MetaX.
    :return: MetaX-id of the created dataset
        The identifier of the newly created dataset
    """
    r = requests.post('https://metax-test.csc.fi/rest/datasets/',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    json=dataset_dict)
    try:
        r.raise_for_status()
    except HTTPError:
        log.info('Failed to create dataset, response: {}'.format(r.json()))
        raise
    return r.json()['id']


def replace_dataset(id, dataset_dict):
    """ Replace existing dataset in MetaX with a new version """
    r = requests.put('https://metax-test.csc.fi/rest/datasets/{id}'.format(id=id),
                    headers={
                        'Content-Type': 'application/json',
                    },
                    json=dataset_dict)
    r.raise_for_status()


def delete_dataset(id):
    """ Delete a dataset from MetaX """
    r = requests.delete('https://metax-test.csc.fi/rest/datasets/{id}'.format(id=id))
    r.raise_for_status()


def get_metax_id(preferred_id):
    """ Retrieve the MetaX-id of a dataset. None if dataset is not in MetaX. 
    
    :param preferred_id: Preferred identifier of the dataset (specified by source).
    :return: metax-id of the dataset. If the dataset is not in metax, returns None.
    """
    r = requests.get('https://metax-test.csc.fi/rest/datasets/{id}/exists' \
        .format(id=preferred_id))
    return 123 # Temp: current endpoint returns true/false, instead of id/null
    # return r.json()

