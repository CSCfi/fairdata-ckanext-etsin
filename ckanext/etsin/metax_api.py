import requests
from requests import HTTPError, exceptions
import json
from pylons import config

import logging
log = logging.getLogger(__name__)

# # Uncomment to setup http logging for debug purposes (note: will log requests
# # made from other files as well)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

TIMEOUT = 30
METAX_DATASETS_BASE_URL = 'https://{0}/rest/datasets'.format(config.get('metax.host'))


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
    r = requests.post(METAX_DATASETS_BASE_URL,
                      headers={
              'Content-Type': 'application/json',
            },
                      json=dataset_json,
                      auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                      timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to create dataset: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=dataset_json, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise
    log.debug('Response text: %s', r.text)
    return json.loads(r.text)['research_dataset']['urn_identifier']


def update_dataset(metax_urn_id, dataset_json):
    """ Update existing dataset in MetaX """
    r = requests.put(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_urn_id),
                     headers={
                'Content-Type': 'application/json'
            },
                     json=dataset_json,
                     auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                     timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to replace dataset {id}: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=dataset_json, id=metax_urn_id, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise


def delete_dataset(metax_urn_id):
    """ Delete a dataset from MetaX. """
    r = requests.delete(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_urn_id),
                        auth=(config.get('metax.api_user'), config.get('metax.api_password')), timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to delete dataset {id}: \nerror={error}, \njson={json}'.format(
            id=metax_urn_id, error=repr(e), json=json_or_empty(r)))
        raise


def check_dataset_exists(metax_urn_id):
    """ Ask MetaX whether the dataset already exists in MetaX by using metax urn_identifier.

    :return: True/False
    """
    r = requests.get(
        METAX_DATASETS_BASE_URL + '/{id}/exists'.format(id=metax_urn_id), timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except Exception as e:
        log.error(e)
        log.error("Error when connecting to MetaX dataset exists API")
        raise e

    log.debug('Checked dataset existence in MetaX: ({code}) {json}'.format(
        code=r.status_code, json=r.json()))
    return r.json()
