import requests
from requests import HTTPError
import json
from pylons import config

import logging
log = logging.getLogger(__name__)

# # Uncomment to setup http logging for debug purposes (note: will log requests
# # made from other files as well)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


def json_or_empty(response):
    response_json = ""
    try:
        response_json = response.json()
    except:
        pass
    return response_json


def create_dataset(dataset_json):
    """ Create a dataset in MetaX.

    :return: metax-id of the created dataset.
    """
    r = requests.post('https://metax-test.csc.fi/rest/datasets/',
            headers={
              'Content-Type': 'application/json',
            },
            json=dataset_json,
            auth=(config.get('metax.api_user'), config.get('metax.api_password')))
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.debug('Failed to create dataset: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=dataset_json, error=repr(e), json=json_or_empty(r)))
        raise
    log.debug('Response text: %s', r.text)
    return json.loads(r.text)['research_dataset']['urn_identifier']


def replace_dataset(metax_id, dataset_json):
    """ Replace existing dataset in MetaX with a new version. """
    r = requests.put('https://metax-test.csc.fi/rest/datasets/{id}'.format(id=metax_id),
            headers={
                'Content-Type': 'application/json'
            },
            json=dataset_json,
            auth=(config.get('metax.api_user'), config.get('metax.api_password')))
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.debug('Failed to replace dataset {id}: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=dataset_json, id=metax_id, error=repr(e), json=json_or_empty(r)))
        raise


def delete_dataset(metax_id):
    """ Delete a dataset from MetaX. """
    r = requests.delete('https://metax-test.csc.fi/rest/datasets/{id}'.format(id=metax_id),
            auth=(config.get('metax.api_user'), config.get('metax.api_password')))
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.debug('Failed to delete dataset {id}: \nerror={error}, \njson={json}'.format(
            id=metax_id, error=repr(e), json=json_or_empty(r)))
        raise


def check_dataset_exists(preferred_id):
    """ Ask MetaX whether the dataset already exists in MetaX.

    :return: True/False
    """
    r = requests.get(
        'https://metax-test.csc.fi/rest/datasets/{id}/exists'.format(id=preferred_id))
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.debug('Failed to check dataset {id} existance in metax: error={error}, json={json}'.format(
            id=preferred_id, error=repr(e), json=json_or_empty(r)))
        raise
    log.debug('Checked dataset existence: ({code}) {json}'.format(
        code=r.status_code, json=r.json()))
    return r.json()
