import json
import requests
import sys
from pprint import pprint

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
    Returns:
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


# TODO: Implement. Also, come up with a better name.
def ask_metax_whether_package_exists(id):
    pass
