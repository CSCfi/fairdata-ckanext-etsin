import requests
from requests import HTTPError, exceptions
import json
from pylons import config

import logging
log = logging.getLogger(__name__)

TIMEOUT = 30
METAX_DATASETS_BASE_URL = 'https://{0}/rest/datasets'.format(config.get('metax.host'))


def json_or_empty(response):
    response_json = ""
    try:
        response_json = response.json()
    except:
        pass
    return response_json


def create_catalog_record(cr_json):
    """
    Create a catalog record in MetaX.

    :param cr_json: MetaX catalog record json
    :return: catalog record identifier of the created catalog record.
    """
    r = requests.post(METAX_DATASETS_BASE_URL,
                      headers={
              'Content-Type': 'application/json',
            },
                      json=cr_json,
                      auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                      timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to create dataset: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=cr_json, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise
    log.debug('Response text: %s', r.text)
    return json.loads(r.text)['identifier']


def update_catalog_record(metax_cr_id, cr_json):
    """
    Update existing catalog record in MetaX

    :param metax_cr_id: MetaX catalog record identifier
    :param cr_json: MetaX catalog record json
    """
    r = requests.put(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_cr_id),
                     headers={
                'Content-Type': 'application/json'
            },
                     json=cr_json,
                     auth=(config.get('metax.api_user'), config.get('metax.api_password')),
                     timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to update catalog record {id}: \ndataset={dataset}, \nerror={error}, \njson={json}'.format(
            dataset=cr_json, id=metax_cr_id, error=repr(e), json=json_or_empty(r)))
        log.error('Response text: %s', r.text)
        raise


def delete_catalog_record(metax_cr_id):
    """
    Delete a catalog record from MetaX.

    :param metax_cr_id: MetaX catalog record identifier
    """
    r = requests.delete(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_cr_id),
                        auth=(config.get('metax.api_user'), config.get('metax.api_password')), timeout=TIMEOUT)
    try:
        r.raise_for_status()
    except HTTPError as e:
        log.error('Failed to delete catalog record {id}: \nerror={error}, \njson={json}'.format(
            id=metax_cr_id, error=repr(e), json=json_or_empty(r)))
        raise


def check_catalog_record_exists(metax_cr_id):
    """
    Ask MetaX whether the catalog record already exists in MetaX by using metax catalog record identifier.

    :param metax_cr_id: MetaX catalog record identifier
    :return: True/False
    """
    r = requests.head(METAX_DATASETS_BASE_URL + '/{id}'.format(id=metax_cr_id))
    return r.status_code == requests.codes.ok
